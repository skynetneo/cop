
from typing import List, TypedDict, Annotated, Optional
from ...agents.generate_post.state import Image # Re-use the Image TypedDict

def list_extend_reducer(left: Optional[list], right: Optional[list]) -> list:
    if not left: left = []
    if not right: right = []
    return left + right

def update_reducer(left, right):
    if right is None: return left
    return right

class FindImagesState(TypedDict):
    # Inputs from the main graph
    page_contents: List[str]
    relevant_links: List[str]
    image_options: Annotated[List[str], list_extend_reducer]
    report: str
    post: str

    # Output
    image: Annotated[Optional[Image], update_reducer]