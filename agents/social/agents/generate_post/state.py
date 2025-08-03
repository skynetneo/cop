
from typing import List, Optional, TypedDict, Union, Literal
from datetime import date
from typing_extensions import Annotated

# A simple type for our DateType enum
DateType = Union[date, Literal["p1", "p2", "p3"]]

class Image(TypedDict):
    imageUrl: str
    mimeType: str

def _overwrite(left, right):
    """Reducer to always take the right-side value."""
    return right if right is not None else left

class GeneratePostState(TypedDict):
    """
    Represents the state of the simplified generate_post graph.
    """
    # --- Input fields (provided by the supervisor) ---
    report: str
    relevant_links: List[str]
    image_options: Optional[List[str]] # Images found by the find_images agent

    # --- Internal State ---
    post: Optional[str]
    condense_count: Annotated[int, lambda x, y: x + y, 0]

    # --- Output fields (returned to the supervisor) ---
    final_post: Optional[str]
    final_image: Optional[Image]
    suggested_schedule: Optional[DateType]