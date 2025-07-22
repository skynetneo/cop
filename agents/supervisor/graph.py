from typing import Dict, Any, Optional, Literal
import json
from pydantic import BaseModel, Field

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import AsyncSqliteSaver
from langgraph import RunnableConfig
from langchain.prompts import ChatPromptTemplate
from .state import SupervisorState
from .nodes import planner_node, tool_executor_node, reviewer_node
from ..memory import checkpointer, memory_manager
from ..tools import KNOWN_TOOLS, tool_map
from ..config import get_llm, LLMConfig


class Supervisor:
    def __init__(self):
        self.graph = self._build_graph()

    def _should_end(self, state: SupervisorState) -> str:
        """Decision point: if a final answer is set, end. Otherwise, review."""
        if state.get("final_answer"):
            return END
        return "reviewer"

    def _build_graph(self):
        builder = StateGraph(SupervisorState)

        # Add the core nodes
        builder.add_node("planner", planner_node)
        builder.add_node("plan_reviewer", reviewer_node)
        builder.add_node("tool_executor", tool_executor_node)
        builder.add_node("reviewer", reviewer_node)

        # Define the graph's flow
        builder.add_edge(START, "planner")
        
        # After the planner, decide to execute a tool or end the conversation
        builder.add_conditional_edges(
            "planner",
            self._should_end,
            {END: END, "reviewer": "tool_executor"} # If not ending, we must have a tool to execute
        )
        
        builder.add_edge("tool_executor", "reviewer")
        
        # After reviewing, decide whether to loop back to the planner or end
        builder.add_conditional_edges(
            "reviewer",
            lambda state: END if not state.get("past_steps") else "planner",
            {END: END, "planner": "planner"}
        )

        # The checkpointer allows the agent to be stateful and conversational
        return builder.compile(checkpointer=checkpointer)

# Singleton instance of the supervisor agent
supervisor_agent = Supervisor().graph


# --- Prompts ---
TOOL_CALL_PROMPT =  ChatPromptTemplate.from_messages([
    ("system", """You are an AI supervisor orchestrating tasks for a user.
Your goal is to understand the user's request, devise a plan, and delegate steps to specialized agents (tools).
If a request can be fulfilled by a single tool, call it directly. If it requires multiple steps, generate a plan.

**Available Tools:**
{tools_description}

**User Request:**
{user_request}

**Current Plan:**
{current_plan}

**Previous Tool Results:**
{previous_tool_results_json}

**Relevant Memories:**
{memory_context}

**Your decision should be in JSON format with the following keys:**
- plan: A step-by-step plan for fulfilling the request, or None if a single tool call is sufficient.
- selected_tool_name: The name of the tool (agent) to call, or None if no tool is needed yet.
- selected_tool_input: The input arguments for the selected tool, in JSON format.
- feedback: Any feedback or clarifying questions for the user. If the task is complete, provide a concluding remark.
"""),
    ("user", "Based on the above, what is your decision? Plan, select tool, or provide feedback.")
])

# Pydantic model for LLM output for tool selection
class SupervisorToolChoice(BaseModel):
    plan: Optional[str] = Field(None, description="Step-by-step plan to fulfill the request.")
    selected_tool_name: Optional[str] = Field(None, description="Name of the agent/tool to call. Choose from: {tool_names}.")
    selected_tool_input: Optional[Dict[str, Any]] = Field(None, description="Input arguments for the selected tool. Use JSON string format if nested.")
    feedback: Optional[str] = Field(None, description="Feedback for the user or clarifying question. If the task is complete, provide a concluding remark here.")

# Helper to build tool descriptions for the LLM
def get_tools_description(tools_spec_map: Dict[str, Dict[str, Any]]) -> str:
    descriptions = []
    for name, tool_data in tools_spec_map.items():
        spec = tool_data["spec"]
        # Use model_json_schema to get a JSON representation of the schema
        schema_json = json.dumps(spec.input_schema.model_json_schema(), indent=2)
        descriptions.append(f"- **{name}**: {spec.description}\n  Input Schema: ```json\n{schema_json}\n```")
    return "\n\n".join(descriptions)

# --- Supervisor Node Logic ---
async def supervisor_decision_node(state: SupervisorState, config: RunnableConfig) -> SupervisorState:
    """
    Orchestrates tool selection and planning based on user request and memory.
    """
    memory_manager = state.get("memory_manager")
    if not memory_manager:
        raise ValueError("Memory manager not found in supervisor state.")

    tools_description = get_tools_description(KNOWN_TOOLS)
    tool_names = ", ".join(KNOWN_TOOLS.keys())

    # Load relevant memories (simplified example - in a real app, query based on user_request)
    memories = await memory_manager.search(
        query=state['user_request'],
        n_results=3,
        namespace=("semantic", "episodes", "procedures") # Search across relevant memory types
    )
    memory_context = "\n".join(
        [f"- [{m['namespace']}] {m['content']['assertion']}" for m in memories]
    ) or "No relevant memories found."

    # Prepare prompt for LLM
    prompt_text = TOOL_CALL_PROMPT.format(
        tools_description=tools_description,
        user_request=state['user_request'],
        current_plan=state['plan'] or "No plan yet.",
        previous_tool_results_json=json.dumps(state.tool_results, indent=2),
        user_message=state['user_request'],
        memory_context=memory_context,
        tool_names=tool_names, # Pass available tool names for LLM to choose from
    )

    # LLM for decision making
    tool_chooser_llm = get_llm.with_structured_output(
        SupervisorToolChoice,

    )
    
    try:
        decision: SupervisorToolChoice = await tool_chooser_llm.ainvoke(prompt_text)
        
        # Update state with LLM's decision
        state.update({
            "plan": decision.plan,
            "selected_tool_name": decision.selected_tool_name,
            "selected_tool_input": decision.selected_tool_input,
            "feedback": decision.feedback,
            "messages": AIMessage(state.get("messages", []), {"role": "assistant", "content": decision.feedback or "Thinking..."})
        })

        # Log decision to memory
        await memory_manager.append(
            {"role": "assistant", "content": f"Supervisor decision: {json.dumps(decision.model_dump())}"},
            namespace=("episodes",) # Log supervisor's own thinking process
        )

    except Exception as e:
        print(f"Error during tool selection LLM call: {e}")
        state['feedback'] = f"Sorry, I encountered an error trying to process your request: {e}. Please try again."
        state['decision'] = "llm_processing_error"
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state['feedback']})
        
    return state

async def execute_tool_node(state: SupervisorState, config: RunnableConfig) -> SupervisorState:
    """Executes the selected tool (agent) and stores its results."""
    if not state.selected_tool_name or not state.selected_tool_input:

        if state.feedback:
            state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state.feedback})
        # If the decision was 'tool_execution_error' or similar, we might route to END or a retry node.
        # For now, if no tool is selected, we'll just pass through. The review node will handle final output.
        return state

    tool_name = state.selected_tool_name
    tool_input = state.selected_tool_input
    tool_info = KNOWN_TOOLS.get(tool_name)

    if not tool_info:
        state['feedback'] = f"Error: Tool '{tool_name}' not found. Available tools: {list(KNOWN_TOOLS.keys())}"
        state['selected_tool_name'] = None # Clear invalid tool selection
        state['selected_tool_input'] = None
        state['decision'] = "tool_not_found"
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state['feedback']})
        return state

    # Ensure the tool input conforms to the spec
    try:
        # This is crucial: validate and potentially cast input to the tool's expected schema
        # The `invoke` method of the agent graph might handle some of this, but explicit validation is good.
        # use Pydantic validation here.
        pass 
    except Exception as e:
        state['feedback'] = f"Error validating input for tool '{tool_name}': {e}"
        state['selected_tool_name'] = None
        state['decision'] = "invalid_tool_input"
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state['feedback']})
        return state


    # Prepare config for the sub-graph run
    subgraph_config: RunnableConfig = {
        "configurable": config.get("configurable", {}), # Pass supervisor's configurable params
        "store": config.get("store"), # Pass the store for memory access by sub-graphs
        "run_name": f"{tool_name}_invocation",
        "run_id": config.get("run_id"), # Inherit parent run_id for tracing
    }

    try:
        print(f"Executing tool: {tool_name} with input: {tool_input}")
        # Invoke the sub-agent graph
        tool_result = await tool_info["graph"].invoke(tool_input, subgraph_config)
        print(f"Tool '{tool_name}' result: {tool_result}")

        # Store the result
        state['tool_results'][tool_name] = tool_result
        # Update assistant messages with execution status
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": f"Successfully executed '{tool_name}'."})

        # Log tool execution to memory (episodic)
        await memory_manager.append(
            {"role": "assistant", "content": f"Executed tool '{tool_name}' with input {tool_input}. Result: {json.dumps(tool_result, indent=2)}"},
            namespace=("episodes",)
        )

    except Exception as e:
        print(f"Error executing tool '{tool_name}': {e}")
        state['feedback'] = f"An error occurred while executing {tool_name}: {e}. Please check the logs."
        state['decision'] = "tool_execution_error"
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state['feedback']})
        # Consider adding a retry mechanism or moving to an error state

    return state


async def review_results_node(state: SupervisorState, config: RunnableConfig) -> SupervisorState:
    """
    Reviews tool results, potentially queries memory, and determines the next step
    (final response, more tools, human input, or end).
    """
    memory_manager = state.get("memory_manager")
    if not memory_manager:
        raise ValueError("Memory manager not found in supervisor state.")

    tools_description = get_tools_description(KNOWN_TOOLS)
    
    # Load relevant memories for context based on recent activity or original request
    memories = await memory_manager.search(
        query=f"Reviewing results for: {state['user_request']} | Tool Results: {json.dumps(state.tool_results)}",
        n_results=3,
        namespace=("semantic", "episodes", "procedures")
    )
    memory_context = "\n".join([f"- [{m['namespace']}] {m['content']['assertion']}" for m in memories]) or "No relevant memories found."

    # LLM prompt to decide next action: final response, more tools, ask user, etc.
    REVIEW_PROMPT = ChatPromptTemplate.from_messages([
        ("system", f"""You are an AI supervisor. Review the user's original request, the plan, tool execution results, available tools, and memory context.
        Decide on the next action:
        - If the user's request is fulfilled, provide a final response to the user.
        - If more information is needed from the user, ask clarifying questions.
        - If the results suggest a follow-up action with a different tool, select that tool and its input.
        - If an error occurred during tool execution, report it clearly.
        - If the task requires human intervention, indicate that.

        Available Tools:
        {{tools_description}}

        User Request: {{user_request}}
        Plan: {{plan}}
        Tool Results: {{tool_results_json}}
        Memory Context: {{memory_context}}
        """),
        ("user", "Based on the above, what is your decision for the next step? (e.g., final response, call another tool, ask user, end).")
    ])

    llm_input = REVIEW_PROMPT.format(
        tools_description=tools_description,
        user_request=state['user_request'],
        plan=state['plan'] or "No specific plan was made.",
        tool_results_json=json.dumps(state.tool_results, indent=2),
        memory_context=memory_context,
    )

    # LLM to decide the next action
    decision_llm = get_llm(config["configurable"].get("llm_config", LLMConfig(temperature=0.65)))    
    try:
        # The LLM's output here should guide the graph's next step.
        # For example, it might decide:
        # 1. To END the process with a final response (stored in 'feedback' or 'decision').
        # 2. To select a NEW tool to call (updating 'selected_tool_name', 'selected_tool_input').
        # 3. To ask the user for more info (updating 'feedback').
    
        # A more advanced setup would use structured output for plan refinement, tool chaining, etc.
        review_result = await decision_llm.invoke(llm_input)
        
        state['decision'] = review_result.content
        state['feedback'] = review_result.content
        state['selected_tool_name'] = None  # Reset tool selection after review
        state['selected_tool_input'] = None  # Reset input after review
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": review_result.content})

        # Log review to memory
        await memory_manager.append(
            {"role": "assistant", "content": f"Supervisor review: {review_result.content}"},
            namespace=("episodes",)
        )
        
    except Exception as e:
        print(f"Error during review results LLM call: {e}")
        state['feedback'] = f"Sorry, I encountered an error reviewing results: {e}."
        state['decision'] = "review_error"
        state["messages"] = AIMessage(state.get("messages", []), {"role": "assistant", "content": state['feedback']})

    return state


# --- Routing Logic ---
def decide_next_step(state: SupervisorState, config: RunnableConfig) -> Literal["execute_tool", "ask_user", "END"]:
    """
    Determines the next step in the supervisor's workflow.
    Routes based on the LLM's decision and tool selection.
    """
    # If tool was selected, execute it
    if state.selected_tool_name:
        return "execute_tool"
    
    # If there's feedback, it might imply a need for user input or task completion
    # For now, assume feedback means we're done or need user interaction handled elsewhere.
    # A more complex routing could involve checking state.decision or other fields.
    elif state.feedback or state.decision:
        return "ask_user" # Route to a human interaction node if feedback/decision implies it
    
    # If no tool selected and no specific feedback that requires user interaction, END.
    # This might happen if the task was successfully planned or completed implicitly.
    else:
        return "END"

# --- Graph Construction ---
# Initialize the memory manager once (or inject it)
# This would typically happen when the supervisor graph is initialized/compiled or passed in config
# For demonstration, we instantiate it here. In a real app, ensure this is managed properly.
# supervisor_memory_manager = MemoryManager() 

# For this example, let's make it simpler and pass a mock or a real instance via config during invoke.
# The main.py or the caller would need to inject it:
# supervisor_graph.invoke(..., config={"configurable": {"memory_manager": supervisor_memory_manager}})

# Define the Supervisor State with the memory manager
class SupervisorStateWithMemory(SupervisorState):
     # Assume memory_manager is provided during invocation config
     pass


# --- Graph Builder ---
builder = StateGraph(
    SupervisorState, # Use the state definition that includes memory_manager
    input=None,      # Input is handled directly within the state for this structure
    output=None,     # Output is managed in state
    config_schema=None # No global config schema needed if passed per-run
)

# Register nodes
builder.add_node("supervisor_decision", supervisor_decision_node)
builder.add_node("execute_tool", execute_tool_node)
builder.add_node("review_results", review_results_node)
# Add a human node if feedback needs direct user interaction
# builder.add_node("ask_user_node", human_node_for_feedback) 

# Define graph edges
builder.add_edge(START, "supervisor_decision")

# Conditional edges based on the supervisor's decision
builder.add_conditional_edges(
    "supervisor_decision",
    decide_next_step,
    {
        "execute_tool": "execute_tool",
        "ask_user": "review_results", # Placeholder for human interaction or end if no interactive feedback needed
        "END": END
    }
)

builder.add_edge("execute_tool", "review_results")
builder.add_edge("review_results", END) # Final state after review

# Compile the graph
supervisor_graph = builder.compile()
supervisor_graph.name = "Supervisor Orchestrator"