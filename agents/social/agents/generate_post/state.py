from typing import List, Optional, TypedDict, Annotated, Union, Literal
from datetime import date
from langgraph.graph import add_messages

# A simple type for our DateType enum from TS
DateType = Union[date, Literal["p1", "p2", "p3", "r1", "r2", "r3"]]

class Image(TypedDict):
    imageUrl: str
    mimeType: str

class ComplexPost(TypedDict):
    main_post: str
    reply_post: str

# Reducer functions
def update_reducer(left, right):
    # Overwrite the left value with the right
    if right is None:
        return left
    return right

def list_update_reducer(left, right):
    if right is None:
        return left or []
    return right

def list_extend_reducer(left: Optional[list], right: Optional[list]) -> list:
    if not left:
        left = []
    if not right:
        right = []
    return left + right

class GeneratePostState(TypedDict):
    """
    Represents the state of the generate_post graph.
    """
    # Input fields
    links: Annotated[List[str], list_update_reducer]

    # Fields populated by the graph
    report: Annotated[Optional[str], update_reducer]
    relevant_links: Annotated[List[str], list_extend_reducer]
    image_options: Annotated[List[str], list_extend_reducer]
    post: Annotated[Optional[str], update_reducer]
    complex_post: Annotated[Optional[ComplexPost], update_reducer]
    image: Annotated[Optional[Image], update_reducer]
    condense_count: Annotated[int, update_reducer]

    # Fields for human-in-the-loop and scheduling
    # Note: scheduleDate is handled by the supervisor now, but the agent
    # can still suggest one.
    suggested_schedule: Annotated[Optional[DateType], update_reducer]
    
    # State for the supervisor-led "human" feedback loop
    # The supervisor will populate this field instead of a human
    supervisor_feedback: Annotated[Optional[str], update_reducer]
    
    # Internal routing
    next_node: Annotated[Optional[str], update_reducer]