
from typing import List, TypedDict, Annotated, Optional

# Reducer functions from the main state file can be reused or defined here
def list_extend_reducer(left: Optional[list], right: Optional[list]) -> list:
    if not left: left = []
    if not right: right = []
    return left + right

class VerifyLinksState(TypedDict):
    """
    State for the link verification subgraph.
    """
    # Input
    links: List[str]

    # Output
    relevant_links: Annotated[List[str], list_extend_reducer]
    page_contents: Annotated[List[str], list_extend_reducer]
    image_options: Annotated[List[str], list_extend_reducer]