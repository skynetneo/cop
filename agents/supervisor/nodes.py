import json
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, ToolMessage, AIMessage
from langgraph.graph import create_react_agent
from langgraph.graph import RunnableGraph
from langgraph.graph.message import MessagesState
from langgraph.store.base import BaseStore
from langchain_core.tools import tool
from langchain_core.runnables import Runnable

from langgraph.prebuilt import ToolNode, create_react_agent
from .state import SupervisorState
from ..memory import SemanticMemory, EpisodicMemory, ProceduralMemory
from .tools import available_tools
from ..config import get_llm, LLMConfig
# --- LLM and Tool Executor Setup ---


# The ToolNode is a LangGraph helper that executes tools and returns the output
# It's our "Do" step.
tool_executor = ToolNode(available_tools)

# --- Node Implementations ---

async def pre_tool_response_node(state: SupervisorState, config: RunnableConfig) -> SupervisorState:
    """
    If the LLM set `state.feedback` _and_ also selected a tool,
    send that feedback as an Assistant message _before_ invoking the tool.
    Then clear feedback so we don’t loop.
    """
    if state.feedback:
        state["messages"] = AIMessage(
            state.get("messages", []),
            {"role": "assistant", "content": state.feedback}
        )
        state.feedback = None
    return state

async def planner_node(state: SupervisorState, config: RunnableConfig) -> dict:
    """
    Plan Step: Receives the user request, searches memory, and decides which tool to call.
    """
    # Get the latest user message
    user_message = state["messages"][-1].content
    
    # Search all memory types for relevant context
    semantic_mem = SemanticMemory.search(namespace="semantic", query=user_message, k=3)
    episodic_mem = EpisodicMemory.search(namespace="episodic", query=user_message, k=2)
    procedural_mem = ProceduralMemory.search(namespace="procedural", query=user_message, k=1)

    # Construct the system prompt with memory
    system_prompt = f"""You are a world-class supervisor agent. Your goal is to fulfill the user's request by intelligently orchestrating a team of specialized agents (available as tools).

Plan your actions step-by-step. Analyze the user's request and the conversation history.
Then, select the best tool to use and call it with the correct arguments.

If the user's request is fulfilled, respond directly to the user with a summary of the results.

Here is some information from your memory that might be relevant:
---
**Relevant Facts (Semantic Memory):**
{json.dumps(semantic_mem, indent=2)}
---
**Past Experiences (Episodic Memory):**
{json.dumps(episodic_mem, indent=2)}
---
**Relevant Procedures (Procedural Memory):**
{json.dumps(procedural_mem, indent=2)}
---
"""
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # Bind tools to the LLM to force a tool call
    
    # create_react_agent(model="google:gemini-2.5-pro").bind_tools(available_tools)
    llm_config = config["configurable"].get("llm_config", LLMConfig(temperature=0.65))
    llm_with_tools = get_llm(llm_config).bind_tools(available_tools)
    #
    # Invoke the LLM to get the next tool call
    response = await llm_with_tools.ainvoke(messages)
    
    # The response can be a direct answer or a tool call
    if not response.tool_calls:
         # If no tool is called, it means the agent thinks the task is done
        return {"task_complete": True}
        
    return {"tool_call": response.tool_calls[0]}


async def reviewer_node(state: SupervisorState) -> dict:
    """
    Review Step: Assesses the result of the tool call and decides if the task is complete.
    Also responsible for saving new memories.
    """
    last_tool_message = next(
        (m for m in reversed(state["messages"]) if isinstance(m, ToolMessage)), None
    )

    if not last_tool_message:
        return {"task_complete": False, "review": "No tool output to review."}

    review_prompt = f"""You are a Quality Assurance agent. Your role is to review the outcome of an action and determine if it has successfully fulfilled the original user request.

**Original User Request:**
{state['messages'][0].content}

**Conversation History:**
{"".join([f'{m.type}: {m.content}\\n' for m in state["messages"]])}

**Last Action's Output:**
{last_tool_message.content}

---
**Your Tasks:**

1.  **Assess Completeness:** Based on all the information above, is the original user request now fully complete?
2.  **Summarize for Memory:** If the task is complete, provide a concise summary of the entire interaction (request, actions, final outcome) so it can be saved to memory for future reference.

Respond with a JSON object with two keys:
- `is_complete` (boolean): true if the task is finished, false otherwise.
- `memory_summary` (string): A detailed summary of the interaction if `is_complete` is true, otherwise an empty string.
"""
    
    class Review(BaseModel):
        is_complete: bool
        memory_summary: str
        
    structured_reviewer = create_react_agent(model="groq:qwen/qwen3-32b").with_structured_output(Review)
    review = await structured_reviewer.ainvoke(review_prompt)
    
    if review.is_complete and review.memory_summary:
        # Save new memories if the task is done
        Me.add(
            namespace="episodic",
            documents=[EpisodicMemory(
                timestamp=datetime.now().isoformat(),
                user_request=state["messages"][0].content,
                actions_taken=json.dumps([m.tool_calls for m in state["messages"] if m.tool_calls]),
                final_outcome=last_tool_message.content
            )],
        )

    return {"task_complete": review.is_complete, "review": review.memory_summary}
