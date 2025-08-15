import os
import asyncio
from typing import Any

from langgraph.graph import StateGraph, START, END
from twilio.rest import Client
from dotenv import load_dotenv
from langmem import create_memory_store_manager

from .state import CallState, CallInput, CallOutput

# --- Configuration ---
load_dotenv()

# We need the public URL of the server that handles the real-time stream
# This must be set in your environment for the tool to work.
SERVER_URL = os.getenv("SERVER_URL") 
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

if not all([SERVER_URL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER]):
    raise ValueError("Missing required environment variables for Call Agent: SERVER_URL, TWILIO_*")

# --- Clients and Managers ---
# These are instantiated once and used by the node.
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# Assuming gemi model_id is accessible or can be configured here
memory_manager = create_memory_store_manager(model="google:gemini-1.5-pro-latest")


# --- Graph Node ---
async def make_call_node(state: CallState) -> dict[str, Any]:
    """
    Initiates a phone call using Twilio and stores session context.
    This is the core action of the tool.
    """
    phone_number = state["phone_number"]
    instructions = state["instructions"]
    context = state.get("context", "")

    try:
        # Twilio will make a POST request to this URL when the call is answered.
        # The real-time server at SERVER_URL will handle this request.
        twiml_url = f"{SERVER_URL}/outgoing-call-twiml"
        
        call = twilio_client.calls.create(
            to=phone_number,
            from_=TWILIO_NUMBER,
            url=twiml_url,
            method="POST"
        )

        # Store the instructions and context linked to the CallSid.
        # The WebSocket handler will retrieve this to properly configure the conversation.
        await memory_manager.create_session(call.sid, {
            "instructions": instructions,
            "context": context
        })
        
        print(f"Call initiated to {phone_number} with SID: {call.sid}")

        return {"call_sid": call.sid, "status": "initiated"}

    except Exception as e:
        print(f"Error making call: {e}")
        return {"call_sid": None, "status": f"error: {e}"}


# --- Graph Definition ---
# This defines the agent that the supervisor will invoke.
builder = StateGraph(
    CallState,
    input=CallInput,
    output=CallOutput,
)

builder.add_node("make_call", make_call_node)
builder.add_edge(START, "make_call")
builder.add_edge("make_call", END)

# The final, compiled graph is the tool.
call_agent = builder.compile()
call_agent.name = "call_agent"
