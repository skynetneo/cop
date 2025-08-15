from typing import cast
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from .chat import chat_node
from .search import search_node
from .state import AgentState

def route(state: AgentState):
    """Route after the chat node based on tool calls."""
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        ai_message = cast(AIMessage, messages[-1])
        
        if ai_message.tool_calls:
            tool_name = ai_message.tool_calls[0]["name"]
            if tool_name == "search_for_agencies":
                return "search_node"
            # display_agencies is a frontend action, so after calling it, we can end.
            if tool_name == "display_agencies":
                return END
    
    # If no tool calls or after a search result, loop back to chat for the next step.
    return "chat_node"

graph_builder = StateGraph(AgentState)

graph_builder.add_node("chat_node", chat_node)
graph_builder.add_node("search_node", search_node)

graph_builder.add_conditional_edges("chat_node", route, {
    "search_node": "search_node",
    "chat_node": "chat_node",
    END: END
})

graph_builder.add_edge(START, "chat_node")
graph_builder.add_edge("search_node", "chat_node") # After searching, go back to chat to process results

graph = graph_builder.compile()
