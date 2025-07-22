# graph.py
import asyncio
import json
import datetime
from typing import cast, Any, Literal, List

from pydantic import BaseModel, Field
from tavily import AsyncTavilyClient
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END, StateGraph

from .lmstudio import ChatLMStudio as Chat
from .configuration import Configuration
from .state import InputState, OverallState, OutputState
from .utils import deduplicate_sources, format_sources, format_all_notes
from .prompts import (
    QUERY_WRITER_PROMPT,
    INFO_PROMPT,
    EXTRACTION_PROMPT,
    REFLECTION_PROMPT,
)


#  LLM & Search Client Setup
rate_limiter = InMemoryRateLimiter(
    requests_per_second=4, check_every_n_seconds=0.1, max_bucket_size=10
)
llm = Chat(
    base_url="http://localhost:9000/v1",
    model="qwen_qwq-32b",
    temperature=0.65,
    format="json",            
    rate_limiter=rate_limiter,
)
search_client = AsyncTavilyClient()

# Memory Imports & Procedural Memory Setup

from .mem import (
    memory_manager,  
    FactRecord,
    EpisodeRecord,
    memory_store,
    LLM_ID,
)
from langmem import create_memory_store_manager

class ProcedureRecord(BaseModel):
    """Schema for procedural memory: reusable research steps."""
    topic: str = Field(..., description="Schema title or category")
    procedure: str = Field(..., description="A search query or research step")

procedural_memory_manager = create_memory_store_manager(
    model=LLM_ID,
    namespace=("procedural",),
    schemas=[ProcedureRecord],
    instructions="Store and retrieve reusable research procedures or queries.",
    enable_inserts=True,
    memory_store=memory_store,
)


# Structured Output Models
class Queries(BaseModel):
    queries: list[str] = Field(description="Generated search queries")

class ReflectionOutput(BaseModel):
    is_satisfactory: bool = Field(description="All required fields populated?")
    missing_fields: list[str] = Field(description="Which fields remain incomplete")
    search_queries: list[str]  = Field(description="Follow-up queries if needed")
    reasoning: str  = Field(description="Why/how the assessment was made")

# Router for Conditional Research Nodes
def pick_research_node(
    state: OverallState, config: RunnableConfig
) -> Literal["research_person", "research_company", "research_grants", "general_research", "research_jobs"]:
    title = state.extraction_schema.get("title", "").lower()
    if title.startswith("person"):
        return "research_person"
    if title.startswith("company"):
        return "research_company"
    if title.startswith("grant"):
        return "research_grants"
    if title.startswith("job"):
        return "research_jobs"
    if title.startswith("general"):
        return "general_research"
    return "general_research"  # Fallback for unrecognized titles

# Graph Nodes
def generate_queries(state: OverallState, config: RunnableConfig) -> dict[str, Any]:
    """Produce search queries, seeding from semantic & procedural memory."""
    cfg = Configuration.from_runnable_config(config)
    max_q = cfg.max_search_queries

    # 1) Fetch past semantic facts
    past = memory_manager.search(topic=state.subject) or []
    past_facts = "\n".join(f"{r['topic']}: {r['assertion']}" for r in past)

    # 2) Fetch past procedural steps for this schema
    schema_title = state.extraction_schema.get("title", "")
    proc = procedural_memory_manager.search(topic=schema_title) or []
    past_procedures = "\n".join(r["procedure"] for r in proc)

    structured = llm.with_structured_output(Queries)
    prompt = QUERY_WRITER_PROMPT.format(
        subject=state.subject,
        info=json.dumps(state.extraction_schema, indent=2),
        user_notes=state.user_notes or "",
        past_facts=past_facts,
        past_procedures=past_procedures,
        max_search_queries=max_q,
    )

    result = cast(
        Queries,
        structured.invoke([
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Generate schema-driven search queries."},
        ])
    )
    return {"search_queries": result.queries}


async def research_person(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Generic Tavily search + info-stitch for a person profile."""
    cfg = Configuration.from_runnable_config(config)
    tasks = [
        search_client.search(q, max_results=cfg.max_search_results, include_raw_content=True, topic="general")
        for q in state.search_queries
    ]
    docs = await asyncio.gather(*tasks)
    dedup = deduplicate_sources(docs)
    content = format_sources(dedup, max_tokens_per_source=1000, include_raw_content=True)

    prompt = INFO_PROMPT.format(
        subject=state.subject,
        info=json.dumps(state.extraction_schema, indent=2),
        content=content,
        user_notes=state.user_notes or "",
    )
    resp = await llm.ainvoke(prompt)
    out = {"completed_notes": [str(resp.content)]}
    if cfg.include_search_results:
        out["search_results"] = dedup
    return out

async def research_company(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Same pattern, but for corporate targets."""
    return await research_person(state, config)

async def research_grants(
    state: OverallState, config: RunnableConfig
) -> dict[str, Any]:
    """Same pattern, but using your legal-specific prompt if you have one."""
    return await research_person(state, config)


def gather_notes_extract_schema(state: OverallState) -> dict[str, Any]:
    """Extract all schema fields from the accumulated notes."""
    notes = format_all_notes(state.completed_notes)
    prompt = EXTRACTION_PROMPT.format(
        info=json.dumps(state.extraction_schema, indent=2),
        notes=notes,
    )
    structured = llm.with_structured_output(state.extraction_schema)
    result = structured.invoke([
        {"role": "system", "content": prompt},
        {"role": "user",   "content": "Produce structured JSON per schema."},
    ])
    return {"info": result}


def persist_memory(state: OverallState) -> dict[str, Any]:
    """Write new facts, procedural steps, and an episodic record to memory."""
    # 1) Semantic: each top-level field
    for field, val in state.info.items():
        if val not in (None, "", [], {}):
            memory_manager.add(
                FactRecord(topic=state.subject, assertion=f"{field} = {val}")
            )

    # 2) Episodic: record this completed research run
    ts = datetime.datetime.utcnow().isoformat()
    context = f"Research run on '{state.subject}' via '{state.extraction_schema.get('title')}'"
    outcome = json.dumps(state.info)
    memory_manager.add(
        EpisodeRecord(timestamp=ts, context=context, resolution=outcome)
    )

    # 3) Procedural: store each search query under this schema title
    schema_title = state.extraction_schema.get("title", "")
    for q in state.search_queries:
        procedural_memory_manager.add(
            ProcedureRecord(topic=schema_title, procedure=q)
        )

    return {}


def reflection(state: OverallState) -> dict[str, Any]:
    """Assess completeness and propose follow-up if necessary."""
    structured = llm.with_structured_output(ReflectionOutput)
    prompt = REFLECTION_PROMPT.format(
        schema=json.dumps(state.extraction_schema, indent=2),
        info=state.info,
    )
    result = cast(
        ReflectionOutput,
        structured.invoke([
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Produce a structured reflection."},
        ])
    )
    if result.is_satisfactory:
        return {"is_satisfactory": True}
    return {
        "is_satisfactory": False,
        "search_queries": result.search_queries,
        "reflection_steps_taken": state.reflection_steps_taken + 1,
    }


def route_from_reflection(
    state: OverallState, config: RunnableConfig
) -> Literal["END", "research_person"]:
    cfg = Configuration.from_runnable_config(config)
    if state.is_satisfactory or state.reflection_steps_taken > cfg.max_reflection_steps:
        return END
    return "research_person"


# Build & Compile the Graph
builder = StateGraph(
    OverallState,
    input=InputState,
    output=OutputState,
    config_schema=Configuration,
)

builder.add_node("generate_queries", generate_queries)
builder.add_node("research_person", research_person)
builder.add_node("research_company", research_company)
builder.add_node("research_grants", research_grants)
builder.add_node("gather_notes_extract_schema", gather_notes_extract_schema)
builder.add_node("persist_memory", persist_memory)
builder.add_node("reflection", reflection)

builder.add_edge(START, "generate_queries")
builder.add_conditional_edges("generate_queries", pick_research_node)

builder.add_edge("research_person", "gather_notes_extract_schema")
builder.add_edge("research_company", "gather_notes_extract_schema")
builder.add_edge("research_grants", "gather_notes_extract_schema")

builder.add_edge("gather_notes_extract_schema", "persist_memory")
builder.add_edge("persist_memory","reflection")

builder.add_conditional_edges("reflection", route_from_reflection)

graph = builder.compile()
