from typing import List, TypedDict, Optional
from typing_extensions import Annotated

class Report(TypedDict):
    """The final structured output of this agent."""
    report: str
    key_details: str

def list_extend_reducer(left: Optional[List[Report]], right: Optional[List[Report]]) -> List[Report]:
    """Reducer to safely concatenate lists of Report dictionaries."""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + right

class GenerateReportState(TypedDict):
    """
    The complete, evolving state for the report generation graph.
    """

    page_contents: List[str]
    key_details: Optional[str]

    reports: Annotated[Optional[List[Report]], list_extend_reducer]