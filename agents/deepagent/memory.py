import asyncio
from datetime import datetime
from typing import Iterable, Callable, Tuple, List
from pydantic import BaseModel, Field
from apscheduler.schedulers.background import BackgroundScheduler
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import create_react_agent
from langmem import (
    ReflectionExecutor,
    create_memory_store_manager,
    create_search_memory_tool,
    create_manage_memory_tool,
)

# ---- Constants ----
GEMINI_CHAT_MODEL = "gemini-1.5-pro-latest"
GEMINI_FAST_MODEL = "gemini-1.5-flash-latest"
GEMINI_EMBED_MODEL = "text-embedding-004"
VECTOR_DIM = 768

# ---- Memory Schema Definitions ----
class UserFlag(BaseModel):
    user_id: str
    score: int
    locked: bool
    flag_type: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SemanticMemory(BaseModel):
    topic: str
    fact: str
    source: str
    mention_count: int
    salience: float
    user_flags: List[UserFlag] = []
    last_verified: datetime = Field(default_factory=datetime.utcnow)

class EpisodicMemory(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
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
    steps: List[dict]
    outcome: str = ""
    feedback: str = ""

# ---- Store Setup ----
shared_store = InMemoryStore(
    index={"dims": VECTOR_DIM, "embed": f"google:{GEMINI_EMBED_MODEL}"}
)

# ---- Memory Managers Factory ----
def build_memory_managers(
    agent_ids: Iterable[str],
    user_ids: Iterable[str],
    task_ids_for: Callable[[str], Iterable[str]],
) -> dict:
    managers = {}
    for ag in agent_ids:
        for us in user_ids:
            for task in task_ids_for(us):
                key = (ag, us, task)
                namespace_prefix = f"{ag}_{us}_{task}"
                managers[key] = {
                    "semantic": create_memory_store_manager(
                        GEMINI_FAST_MODEL,
                        namespace=("semantic",),
                        schemas=[SemanticMemory],
                        store=shared_store,
                    ),
                    "episodic": create_memory_store_manager(
                        GEMINI_FAST_MODEL,
                        namespace=(f"{namespace_prefix}_episodes",),
                        schemas=[EpisodicMemory],
                        store=shared_store,
                    ),
                    "procedural": create_memory_store_manager(
                        GEMINI_FAST_MODEL,
                        namespace=(f"{namespace_prefix}_procedural",),
                        schemas=[ProceduralMemory, InstructionMemory],
                        store=shared_store,
                    ),
                }
    return managers

# ---- Reflection Executor ----
# Example: Create a reflector for a specific manager
# reflector = ReflectionExecutor(managers[('agent1', 'user1', 'task1')]['semantic'], store=shared_store)

# ---- Retrieval Helper ----
from typing import Optional

async def retrieve_relevant_memories(
    store: InMemoryStore,
    namespace: Tuple[str, ...],
    query: str,
    metadata_filter: Optional[dict] = None,
    limit: int = 5,
):
    results = await store.asearch(
        namespace,
        query=query,
        filter=metadata_filter or {},
        limit=limit,
    )
    return results

# ---- Memory Curation Agent ----
memory_review_agent = create_react_agent(
    model=GEMINI_CHAT_MODEL,
    tools=[
        create_manage_memory_tool(namespace=("semantic",)),
        create_search_memory_tool(namespace=("semantic",)),
    ],
    prompt=lambda state: [
        {"role": "system", "content": "Curate memories: merge duplicates, purge low-salience entries."},
        *state.get("messages", []),
    ],
)

# ---- Scheduler ----
scheduler = BackgroundScheduler(daemon=True)

def run_weekly_curation():
    memory_review_agent.invoke(
        {"messages": [{"role": "user", "content": "Review and clean up the semantic memory."}]},
        config={"configurable": {"thread_id": "weekly_curation"}},
    )

def start_scheduler():
    scheduler.add_job(run_weekly_curation, "interval", weeks=1, id="weekly_curation")
    if not scheduler.running:
        scheduler.start()

# ---- Example Usage ----
if __name__ == '__main__':
    agent_ids_example = ["agent1"]
    user_ids_example = ["user1"]
    def task_ids_for_example(user_id: str) -> List[str]:
        return ["task1"]

    managers = build_memory_managers(agent_ids_example, user_ids_example, task_ids_for_example)
    
    # Start the scheduler
    start_scheduler()

    # Keep the script running to allow the scheduler to work
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
