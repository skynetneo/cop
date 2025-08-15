
from typing import List, TypedDict, Optional, Annotated

class Report(TypedDict):
    report: str
    key_details: str

def list_extend_reducer(left: Optional[list], right: Optional[list]) -> list:
    if not left: left = []
    if not right: right = []
    return left + right

class GenerateReportState(TypedDict):
    page_contents: List[str]
    image_options: Optional[List[str]]
    # Output - must match the key used in the supervisor graph
    reports: Annotated[List[Report], list_extend_reducer]
