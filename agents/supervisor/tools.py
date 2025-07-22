

import os
from typing import List, Dict, Literal, Optional
from langchain_core.tools import tool

# --- Import Sub-Agent Graphs ---
# These are the entrypoints to your other specialized agents.
from agents.research.graph import graph as research_agent
from agents.phone.graph import call_agent as phone_agent
from agents.resources.graph import graph as resources_agent
# --- Import Python Toolkits and Functions ---
from tools.calendar.calendar_toolkit import CalendarToolkit
from tools.gmail.gmail_toolkit import GmailToolkit
from tools.playwright.playwright_toolkit import PlayWrightToolkit
from tools.ipyrepl import run_python as ipyrepl_tool_func
from tools.tts import tts_stream_tool as tts_tool_func

# --- Agent Wrappers ---
# We wrap the sub-agent graphs in a @tool decorator so the supervisor can call them.

@tool
async def research_tool(
    subject: str,
    schema_type: Literal["company", "person", "job","grants", "general"] = "general",
    user_notes: str = ""
) -> dict:
    """Conducts detailed research on a subject and returns structured information."""
    config = {"configurable": {"thread_id": "supervisor-research"}}
    result = await research_agent.ainvoke(
        {"subject": subject, "schema_type": schema_type, "user_notes": user_notes},
        config
    )
    return result.get("info", {})

@tool
async def phone_tool(
    phone_number: str,
    instructions: str,
    context: str = ""
) -> dict:
    """Initiates an outbound phone call with specific instructions."""
    config = {"configurable": {"thread_id": "supervisor-phone"}}
    result = await phone_agent.ainvoke(
        {"phone_number": phone_number, "instructions": instructions, "context": context},
        config
    )
    return result

@tool
async def resources_tool(
    query: str,
) -> dict:
    """
    Finds local social service agencies like food banks, shelters, or clothing closets based on a user's query.
    The query should be specific, like "food banks in Portland, OR" or "shelters for families near downtown".
    """
    # The thread_id can be static or dynamically generated for each sub-task
    config = {"configurable": {"thread_id": "supervisor-resource-finder"}}
    
    # We invoke the resource_finder graph with a single HumanMessage containing the query
    result = await resources_agent.ainvoke(
        [{"role": "user", "content": query}],
        config
    )
    # The resource_finder agent's job is to call the `display_agencies` tool on the frontend.
    # The return value to the supervisor can be a confirmation message.
    # The AIMessage containing the tool call to `display_agencies` is in result['messages'][-1]
    final_message = result['messages'][-1]
    if final_message.tool_calls:
        return f"Successfully found agencies and displayed them to the user for query: '{query}'"
    else:
        return f"Agent ran for query '{query}' but did not display agencies. It might have asked a clarifying question."


# --- Toolkit and Function Wrappers ---

# Initialize toolkits
gmail_toolkit = GmailToolkit()
calendar_toolkit = CalendarToolkit()
playwright_toolkit = PlayWrightToolkit()
# Expose individual methods from toolkits
gmail_tools = gmail_toolkit.get_tools()
calendar_tools = calendar_toolkit.get_tools()
playwright_tools = playwright_toolkit.get_tools()


@tool
def python_repl_tool(code: str) -> dict:
    """Executes Python code in a sandboxed REPL environment. Returns stdout, stderr, and images."""
    return ipyrepl_tool_func(code)

@tool
def tts_tool(text: str) -> str:
    """Converts text to speech and returns a Base64-encoded MP3 audio string."""
    return tts_tool_func.func(text)


# --- Final Tool List ---
# This is the complete list of capabilities the supervisor's planner can choose from.
available_tools = (
    [resources_tool, research_tool, phone_tool, python_repl_tool, tts_tool]
    + gmail_tools
    + calendar_tools
   
)

# Create a dictionary for easy lookup by name
tool_map = {t.name: t for t in available_tools}