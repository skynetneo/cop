import json
from .state import AgentState
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from .search import search_for_agencies
from langchain_core.runnables import RunnableConfig

# This is a placeholder tool for the new frontend action
from langchain_core.tools import tool

@tool
def display_agencies(category_name: str, agencies: list):
    """Displays a carousel of agencies to the user in the chat window."""
    # This tool's implementation is on the frontend via useCopilotAction.
    # The backend just needs to know it exists to call it.
    return f"Displayed {len(agencies)} agencies for the category: {category_name}"

llm = ChatOpenAI(model="gpt-4o")
tools = [search_for_agencies, display_agencies]

async def chat_node(state: AgentState, config: RunnableConfig):
    """Handle chat operations for finding local resources."""
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    system_message = f"""
    You are a helpful assistant for finding local social service agencies. Your goal is to understand the user's need (e.g., food, clothing, shelter) and help them find relevant local resources.

    1.  **Clarify the Need**: If the user's request is vague, ask for clarification. For example, "I need help" -> "What kind of help do you need? For example, are you looking for food, shelter, or something else?"
    2.  **Search for Agencies**: Once you understand the need (e.g., "food banks"), use the `search_for_agencies` tool. Your query should be specific, like "food banks in San Francisco".
    3.  **Display Results**: After getting the search results, you MUST call the `display_agencies` tool. Pass the `category_name` (e.g., "Food Banks") and the list of agencies you found. This will show the user an interactive list.
    4.  **Do not manage lists**: You do not have tools to add, update, or delete agencies or categories. All interactions are through chat. If the user wants to change something, they should ask you to search again or refine their request.
    """

    response = await llm_with_tools.ainvoke(
        [
            SystemMessage(content=system_message),
            *state["messages"]
        ],
        config=config,
    )

    return {"messages": [response]}
