from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import NotRequired, Annotated, List, Dict, Optional
from typing_extensions import TypedDict

class Todo(TypedDict):
    """Todo to track."""
    content: str
    status: str  # Literal["pending", "in_progress", "completed"]

def file_reducer(
    left: Optional[Dict[str, str]], right: Optional[Dict[str, str]]
) -> Optional[Dict[str, str]]:
    if left is None:
        return right
    if right is None:
        return left
    return {**left, **right}

class DeepAgentState(AgentState):
    todos: NotRequired[List[Todo]]
    files: Annotated[NotRequired[Dict[str, str]], file_reducer]
