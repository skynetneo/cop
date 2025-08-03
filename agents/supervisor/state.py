from typing import TypedDict, List, Dict, Any, Optional, Union
from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState, add_messages
from langgraph.store.base import BaseStore
from pydantic import BaseModel, Field
from .tools import available_tools
from ..memory import get_manager, MemoryManager



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
    available_tools: List[Any] = [] # List of tool 
    plan: Optional[str] = None
    selected_tool_name: Optional[str] = None
    selected_tool_input: Optional[Dict[str, Any]] = None
    tool_results: Dict[str, Any] = {}
    memory_manager: MemoryManager # Inject memory manager instance
    decision: Optional[str] = None
    feedback: Optional[str] = None
    intermediate_results: Dict[str, Any] = {} # For passing data between tool calls if needed
    memory_context: Optional[str] = None