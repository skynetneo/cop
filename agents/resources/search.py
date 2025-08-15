import os
import json
import googlemaps
from typing import cast
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import tool
from .state import AgentState # ADAPTED: Import from new state file
from langchain_core.runnables import RunnableConfig
from copilotkit.langgraph import copilotkit_emit_state, copilotkit_customize_config


@tool
def search_for_agencies(queries: list[str]) -> list[dict]:
    """Search for local agencies based on a query (e.g., 'food banks near me'). Returns a list of agencies with their details."""

gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def search_node(state: AgentState, config: RunnableConfig):
    """Search for agencies based on the selected category or query."""
    ai_message = cast(AIMessage, state["messages"][-1])

    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "search_progress",
            "tool": "search_for_places",
            "tool_argument": "search_progress",
        }],
    )

    state["search_progress"] = state.get("search_progress", [])
    queries = ai_message.tool_calls[0]["args"]["queries"]

    for query in queries:
        state["search_progress"].append({
            "query": query,
            "results": [],
            "done": False
        })

    await copilotkit_emit_state(config, state)

    # Process results into a list of dictionaries
    agencies = []
    for i, query in enumerate(queries):
        response = gmaps.places(queries)
        for result in response.get("results", []):
            place_id = result.get("place_id")
            details = {}
            if place_id:
                details = gmaps.place(place_id=place_id, fields=['formatted_phone_number', 'website', 'opening_hours', 'editorial_summary']).get('result', {})
        
            agency = {
                "id": place_id.get("place_id"),
                "name": place_id.get("name"),
                "address": place_id.get("vicinity"),
                "latitude": place_id.get("geometry", {}).get("location", {}).get("lat"),
                "longitude": place_id.get("geometry", {}).get("location", {}).get("lng"),
                "phone": place_id.get("formatted_phone_number"),
                "website": place_id.get("website"),
                "notes": "",
            }
            agencies.append(agency)
        state["search_progress"][i]["done"] = True
        await copilotkit_emit_state(config, state)

    state["search_progress"] =[]
    await copilotkit_emit_state(config, state)

    state["messages"].append(ToolMessage(
        tool_call_id=ai_message.tool_calls[0]["id"],
        content=f"Added the following agencies: {json.dumps(agencies)}",
    ))


    # Emit the updated state with the new agencies found
    await copilotkit_emit_state(state, config, {"agencies": agencies})

    return agencies
