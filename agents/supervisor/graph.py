from typing import Literal
from langgraph.graph import StateGraph, START, END
from .state import SupervisorState
from .nodes import planner_node, tool_executor_node, reviewer_node
from ..memory import checkpointer


class Supervisor:
    def __init__(self, checkpointer):
        self.graph = self._build_graph(checkpointer)

    def _should_continue(self, state: SupervisorState) -> Literal["__end__", "tool_executor", "reviewer"]:
        """Decision point: determine the next step based on the planner's output."""
        if state.get("task_complete"):
            return END
        if state.get("tool_call"):
            return "tool_executor"
        return "reviewer"

    def _build_graph(self, checkpointer):
        builder = StateGraph(SupervisorState)

        # Add the core nodes
        builder.add_node("planner", planner_node)
        builder.add_node("tool_executor", tool_executor_node)
        builder.add_node("reviewer", reviewer_node)

        # Define the graph's flow
        builder.add_edge(START, "planner")

        # After the planner, decide to execute a tool, end, or review
        builder.add_conditional_edges(
            "planner",
            self._should_continue,
            {
                "tool_executor": "tool_executor",
                "reviewer": "reviewer",
                END: END,
            },
        )

        # After executing a tool, always go to the reviewer
        builder.add_edge("tool_executor", "reviewer")

        # After reviewing, decide whether to loop back to the planner or end
        builder.add_conditional_edges(
            "reviewer",
            lambda state: "planner" if not state.get("task_complete") else END,
            {
                "planner": "planner",
                END: END,
            },
        )

        # The checkpointer allows the agent to be stateful and conversational
        return builder.compile(checkpointer=checkpointer)

# Singleton instance of the supervisor agent
supervisor_agent = Supervisor(checkpointer=checkpointer).graph