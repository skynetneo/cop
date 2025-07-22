# ADAPTED: Renamed and redefined state for agencies
from typing import TypedDict, List, Optional
from langgraph.graph import MessagesState

class Agency(TypedDict):
    """An agency that provides local resources."""
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str]
    hours: Optional[str]
    website: Optional[str]
    notes: Optional[str]

class AgencyCategory(TypedDict):
    """A category of agencies, like 'Food Banks'."""
    id: str
    name: str
    center_latitude: float
    center_longitude: float
    zoom: int
    agencies: List[Agency]

class SearchProgress(TypedDict):
    """The progress of a search."""
    query: str
    results: list[str]
    done: bool

class AgentState(MessagesState):
    """The state of the agent."""
    selected_category_id: Optional[str]
    categories: List[AgencyCategory]
    search_progress: List[SearchProgress]