from typing import List, Dict, Any, Optional
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field
from ..memory import MemoryManager

class MemoryRecord(BaseModel):
    """Generic memory record structure for supervisor's memory interaction."""
    topic: str
    assertion: str
    timestamp: str
    mention_count: int = 1
    salience: float = 0.0
    extracted_prefs: Dict[str, Any] = Field(default_factory=dict)

class UserFlag(BaseModel):
    user_id: str
    score: int
    locked: bool
    flag_type: str
    description: str
    timestamp: str

class EpisodicMemory(BaseModel):
    timestamp: str
    convo_id: str
    speaker: str
    text: str
    mention_count: int = 1
    salience: float = 0
    extracted_prefs: Dict[str, Any] = Field(default_factory=dict)
    user_flags: List[UserFlag] = Field(default_factory=list)

class SupervisorState(MessagesState):
    """The state for the supervisor agent."""
    user_request: str
    plan: Optional[str] = None
    tool_call: Optional[dict] = None
    tool_results: Optional[dict] = None
    task_complete: bool = False
    review: str = ""
    memory_manager: MemoryManager