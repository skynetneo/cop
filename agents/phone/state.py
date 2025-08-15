# agents/call/state.py
from typing import TypedDict, Optional

class CallInput(TypedDict):
    """Input for the call agent tool."""
    phone_number: str
    instructions: str
    context: Optional[str]

class CallState(CallInput):
    """The full state of the call agent graph."""
    call_sid: Optional[str]
    status: Optional[str]

class CallOutput(TypedDict):
    """The final output of the call agent tool."""
    call_sid: str
    status: str
