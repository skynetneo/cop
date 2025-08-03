from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph 

from .state import GenerateReportState

# Import the node functions from their dedicated file
from .nodes import extract_key_details, generate_report

# The function now correctly hints that it returns a CompiledStateGraph
def create_generate_report_graph() -> CompiledStateGraph:
    """
    Builds and compiles the StateGraph for the report generation agent.

    This graph follows a simple, linear flow:
    1. Extract key details from the source content.
    2. Generate a full report based on the details and the source content.
    """
    # Initialize the builder object
    workflow = StateGraph(GenerateReportState)
    
    # Add the nodes to the graph, giving them string names
    workflow.add_node("extract_key_details", extract_key_details)
    workflow.add_node("generate_report", generate_report)
    
    # Define the workflow's edges
    workflow.set_entry_point("extract_key_details")
    workflow.add_edge("extract_key_details", "generate_report")
    workflow.add_edge("generate_report", END)
    
    # Compile the graph into a runnable object
    generate_report_graph = workflow.compile()
    generate_report_graph.name = "Generate Report Agent"
    
    # The return type now matches the type of the object being returned
    return generate_report_graph

# Instantiate the final, compiled graph so it can be imported by other parts of the system
generate_report_graph = create_generate_report_graph()