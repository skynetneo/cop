import os
import asyncio
import math
from datetime import datetime, timezone
from typing import Dict, Tuple
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler
from langgraph.store.sqlite.aio import AsyncSqliteStore
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langmem import (
    ReflectionExecutor,
    create_memory_store_manager,
    create_manage_memory_tool,
    create_search_memory_tool,
    
)

# Configuration constants
GEMINI_CHAT_MODEL = "google:gemini-2.5-pro-latest"
GEMINI_FAST_MODEL = "google:gemini-2.5-flash-lite-preview-06-17"
GEMINI_EMBED_MODEL = "google:gemini-embedding-exp-03-07"
VECTOR_DIM = 1536
SQLITE_PATH = os.getenv("SQLITE_PATH", "langgraph.db")


# Salience calculation helpers
a = 1.0   # semantic similarity weight
b = 0.7   # mention‑count weight
g_c = 0.5 # recency decay weight
d = 2.0   # user‑flag boost
tau_hours = 72.0


def _age_hours(ts: str) -> float:
    dt = datetime.fromisoformat(ts)
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600


def _recency_decay(ts: str) -> float:
    return math.exp(-_age_hours(ts) / tau_hours)


def compute_salience(mem, similarity: float) -> float:
    count_term = b * math.log1p(mem.mention_count)
    ts = getattr(mem, "timestamp", getattr(mem, "last_verified", ""))
    recent_term = g_c * _recency_decay(ts) if ts else 0
    flag_term = d * sum((f.score or 0) + (5 if getattr(f, "locked", False) else 0)
                        for f in getattr(mem, "user_flags", []))
    return a * similarity + count_term + recent_term + flag_term


# Memory schemas
class UserFlag(BaseModel):
    user_id: str
    score: int
    locked: bool
    flag_type: str
    description: str
    timestamp: str

class SemanticMemory(BaseModel):
    topic: str
    fact: str
    source: str
    mention_count: int
    salience: float
    user_flags: list[UserFlag] = []
    last_verified: str

class EpisodicMemory(BaseModel):
    timestamp: str
    convo_id: str
    speaker: str
    text: str
    mention_count: int = 1
    salience: float = 0
    extracted_prefs: dict = {}

class InstructionMemory(BaseModel):
    task_id: str
    task: str
    instructions: str

class ProceduralMemory(BaseModel):
    task_id: str
    steps: list[dict]
    outcome: str = ""
    feedback: str = ""

SCHEMAS = [SemanticMemory, EpisodicMemory, InstructionMemory, ProceduralMemory]


# Core state – shared vector store & manager registry
shared_store = InMemoryStore(index={"dims": VECTOR_DIM, "embed": GEMINI_EMBED_MODEL})
checkpointer = AsyncSqliteSaver.from_conn_string(SQLITE_PATH)

# registry: (agent, user, task) → MemoryStoreManager
_managers: Dict[Tuple[str, str, str], any] = {}

# Lazy manager factory
def get_manager(agent_id: str, user_id: str, task_id: str):
    """Fetch or create a `MemoryStoreManager` for the given identifiers."""
    key = (agent_id, user_id, task_id)
    if key not in _managers:
        ns = (
            "semantic",  # global namespace shared across all tuples
            f"{agent_id}_episodes_{user_id}",
            f"{agent_id}_instructions_{user_id}_{task_id}",
            f"{agent_id}_procedures_{user_id}_{task_id}",
        )
        _managers[key] = create_memory_store_manager(
            model=GEMINI_FAST_MODEL,
            namespace=ns,
            schemas=SCHEMAS,
            instructions=(
                "• semantic: global facts\n"
                "• episodic: chat history\n"
                "• instructions: original spec\n"
                "• procedural: actionable steps",
            ),
            enable_inserts=True,
            memory_store=shared_store,
        )
    return _managers[key]

# per‑task maintenance


def _make_review_agent(agent_id: str, user_id: str, task_id: str):
    sem = ("semantic",)
    epi = (f"{agent_id}_episodes_{user_id}",)
    ins = (f"{agent_id}_instructions_{user_id}_{task_id}",)
    prc = (f"{agent_id}_procedures_{user_id}_{task_id}",)
    tools = [
        create_manage_memory_tool(namespace=ns)
        for ns in (sem, epi, ins, prc)
    ] + [
        create_search_memory_tool(namespace=ns)
        for ns in (sem, epi, ins, prc)
    ]
    return create_react_agent(
        model=GEMINI_CHAT_MODEL,
        prompt=lambda s: [
            {"role": "system", "content": "Curate memories: merge duplicates, purge low‑salience."},
            *s.get("messages", []),
        ],
        tools=tools,
        memory_manager=get_manager(agent_id, user_id, task_id),
    )


async def curate_memories(agent_id: str, user_id: str, task_id: str):
    """One‑shot curation pass for the specified tuple."""
    agent = _make_review_agent(agent_id, user_id, task_id)
    await asyncio.to_thread(agent.run)

# Global semantic reflector (runs regardless of tuples)
reflector = ReflectionExecutor(
    llm=GEMINI_CHAT_MODEL,
    memory_namespace=("semantic",),
)

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(lambda: reflector.run([]), "interval", hours=24, id="daily_semantic_reflection")
scheduler.start()