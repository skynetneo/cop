from typing import TypedDict, List, Dict, Any, Optional, Union
from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState, add_messages
from langgraph.store.base import BaseStore
from pydantic import BaseModel, Field

# Import tool specs from each agent
# You'll need to create these tool.py files for each agent
from agents.social.tool import SocialMediaAgentTool
from agents.phone.tool import PhoneAgentTool # From previous example
from agents.research.tool import ResearchAgentTool # Assuming you'll create this
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


# Define a Union of all possible tool specs
class ToolsUnion(BaseModel):
    social_media_agent: Optional[SocialMediaAgentTool] = None
    resources_agent: Optional[ResearchAgentTool] = None
    phone_agent: Optional[PhoneAgentTool] = None
    research_agent: Optional[ResearchAgentTool] = None

class SupervisorState(MessagesState):
    """The state for the supervisor agent."""
    user_request: str
    available_tools: List[ToolsUnion] = [] # List of tool 
    plan: Optional[str] = None
    selected_tool_name: Optional[str] = None
    selected_tool_input: Optional[Dict[str, Any]] = None
    tool_results: Dict[str, Any] = {}
    memory_manager: MemoryManager # Inject memory manager instance
    decision: Optional[str] = None
    feedback: Optional[str] = None
    intermediate_results: Dict[str, Any] = {} # For passing data between tool calls if needed
    memory_context: Optional[str] = None