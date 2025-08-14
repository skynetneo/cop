import os, json, asyncio, time, hashlib
import re
from typing import cast, List, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, ToolMessage
from langchain.tools import tool
from .state import AgentState
from copilotkit.langgraph import copilotkit_emit_state, copilotkit_customize_config
from google import genai

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")  # supports google_search
client = genai.Client()



GEOCODER_UA = os.getenv("GEOCODER_UA", "accessible-solutions/1.0 (contact@example.com)")
_geocoder = Nominatim(user_agent=GEOCODER_UA, timeout=10) # type: ignore
_geocode = RateLimiter(_geocoder.geocode, min_delay_seconds=1.05)  # be nice to public API



def _stable_id(name: str, address: Optional[str]) -> str:
    h = hashlib.sha1()
    h.update((name or "").encode()); h.update((address or "").encode())
    return h.hexdigest()[:16]

async def _gemini_search(query: str):
    """Use Gemini chat with the built-in google_search tool and return normalized agencies."""
    search_tool = {"google_search": {}}
    prompt = (
        f"Return ONLY a JSON array of agencies with fields: name, address, phone, website, "
        f"latitude, longitude, notes. Provide lat/long when available. Do not include markdown "
        f"or commentary. Query: {query}"
    )
    # create chat with google_search tool
    chat = client.chats.create(
        model=MODEL,
        config={
            "tools": ["google_search"]
        } # type: ignore
            
    )
    # send prompt and get response
    response = chat.send_message(prompt)
    text = response.text or ""
    
    # Extract first JSON array
    s = text.strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.IGNORECASE | re.DOTALL)
    m = re.search(r"\[.*\]", s, flags=re.DOTALL)
    raw = m.group(0) if m else s

    try:
        items = json.loads(raw)
    except Exception:
        items = []

    out: List[Dict] = []
    for a in items if isinstance(items, list) else []:
        out.append({
            "name": a.get("name"),
            "address": a.get("address"),
            "phone": a.get("phone"),
            "website": a.get("website"),
            "latitude": a.get("latitude"),
            "longitude": a.get("longitude"),
            "notes": a.get("notes") or "",
        })
    return out

def _fill_coords_inplace(agencies: List[Dict]) -> None:
    for a in agencies:
        if not a.get("latitude") or not a.get("longitude"):
            addr = a.get("address")
            if not addr:
                continue
            loc = _geocode(addr)
            if loc:
                a["latitude"] = loc.latitude
                a["longitude"] = loc.longitude

@tool
def search_for_agencies(queries: List[str]) -> List[Dict]:
    """Search for local agencies (e.g., 'food banks in Eugene OR'). Returns a list of agencies with details."""
    # This is a sync tool for LangChain’s tool-calling; it internally calls Gemini + geocoding.
    all_rows: List[Dict] = []
    for q in queries:
        rows = asyncio.run(_gemini_search(q))  # safe here because tool is sync; swap to fully-async if desired
        all_rows.extend(rows)
    # Geocode missing coords via OSM Nominatim (rate limited)
    _fill_coords_inplace(all_rows)
    # Add IDs and prune empties
    final = []
    seen = set()
    for a in all_rows:
        if not a.get("name"):
            continue
        a["id"] = _stable_id(a["name"], a.get("address"))
        key = (a["name"], a.get("address"))
        if key in seen:
            continue
        seen.add(key)
        final.append(a)
    return final

async def search_node(state: AgentState, config: RunnableConfig):
    """Search for agencies from selected category or query, stream progress to UI."""
    ai_message = cast(AIMessage, state["messages"][-1])

    # Make the tool name consistent with the actual tool
    config = copilotkit_customize_config(
        config,
        emit_intermediate_state=[{
            "state_key": "search_progress",
            "tool": "search_for_agencies",
            "tool_argument": "search_progress",
        }],
    )

    state["search_progress"] = state.get("search_progress", [])
    queries = ai_message.tool_calls[0]["args"]["queries"]
    for q in queries:
        state["search_progress"].append({"query": q, "results": [], "done": False})
    await copilotkit_emit_state(config, state)

    # Run searches sequentially to respect rate limits; parallelize if you self-host geocoder
    agencies: List[Dict] = []
    for i, q in enumerate(queries):
        found = await asyncio.get_event_loop().run_in_executor(None, lambda: search_for_agencies(q))
        if not isinstance(found, list):
            found = [found]
        # Filter to only dicts to avoid type errors
        dict_found = [item for item in found if isinstance(item, dict)]
        agencies.extend(dict_found)
        # Ensure results are a list of strings
        state["search_progress"][i]["results"] = [str(r) for r in dict_found]
        state["search_progress"][i]["done"] = True
        await copilotkit_emit_state(config, state)

    # Clear progress and emit final list
    state["search_progress"] = []
    await copilotkit_emit_state(config, state)

    state["messages"].append(ToolMessage(
        tool_call_id=ai_message.tool_calls[0]["id"],
        content=f"Added the following agencies: {json.dumps(agencies)}",
    ))

    await copilotkit_emit_state(config, {"agencies": agencies})
    return agencies