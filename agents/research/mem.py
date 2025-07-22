import asyncio
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler

from langchain.chat_models import init_chat_model
from langgraph.store.memory import InMemoryStore
from langgraph.func import entrypoint
from langgraph import (
    create_react_agent,
    create_search_memory_tool,
    create_manage_memory_tool,
)
from langgraph.checkpoint.sqlite import AsyncSqliteSaver

from langmem import (
    ReflectionExecutor,
    create_memory_store_manager,
)


LLM =  "google:gemini-2.5-pro-latest"
EMBED_MODEL = "google:gemini-embedding-exp-03-07"
LLM_ID = "google:gemini-2.5-flash-lite-preview-06-17"  
VECTOR_DIM = 1536
SQLITE_PATH = "langgraph.db"

# Vector store (pure‑Python, no external DB)
memory_store = InMemoryStore(index={"dims": VECTOR_DIM, "embed": EMBED_MODEL})

# LLM used everywhere
llm = init_chat_model(LLM)

# Checkpointer for workflow state (not for the vector index itself)
checkpointer = AsyncSqliteSaver.from_conn_string(SQLITE_PATH)



# Semantic & Episodic schemas
class FactRecord(BaseModel):
    """Schema for semantic facts."""
    topic: str     = Field(..., description="The subject of the fact.")
    assertion: str = Field(..., description="The factual statement.")

class EpisodeRecord(BaseModel):
    """Schema for episodic memory: problem-solving logs."""
    timestamp: str   = Field(..., description="ISO datetime when episode occurred.")
    context: str     = Field(..., description="What triggered the episode.")
    resolution: str  = Field(..., description="How it was solved or key takeaway.")

memory_manager = create_memory_store_manager(
    model=LLM_ID,
    namespace=("semantic", "episodes"),
    schemas=[FactRecord, EpisodeRecord],
    instructions=(
        "For semantic memory, store atomic facts under FactRecord.\n"
        "For episodic memory, store problem solving examples under EpisodeRecord."
    ),
    enable_inserts=True,
    memory_store=memory_store,
)

reflector = ReflectionExecutor(
    llm=LLM,
    memory_namespace=("semantic", "episodes"),
)

memory_review_agent = create_react_agent(
    model=LLM,
    prompt=lambda state: [
        {
            "role": "system",
            "content": (
                "You are a memory curator. Your job is to:\n"
                "  1. Prune duplicate FactRecords;\n"
                "  2. Consolidate similar EpisodeRecords;\n"
                "  3. Keep the store performant.\n\n"
                "Tools available: manage_semantic, search_semantic, "
                "manage_episodes, search_episodes."
            ),
        },
        *state.get("messages", []),
    ],
    tools=[
        create_manage_memory_tool(namespace=("semantic",)),
        create_search_memory_tool(namespace=("semantic",)),
        create_manage_memory_tool(namespace=("episodes",)),
        create_search_memory_tool(namespace=("episodes",)),
    ],
    memory_manager=memory_manager,
)


# Daily housekeeping to keep the vector index tidy
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(lambda: memory_review_agent.run([]), "interval", hours=24, id="daily_memory_review")
scheduler.start()

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    lambda: memory_review_agent.run([]),
    trigger="interval",
    hours=24,
    id="daily_memory_review"
)
scheduler.start()
