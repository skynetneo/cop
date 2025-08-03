
import logging
from typing import Literal

from langgraph.graph import StateGraph, START, END
from .state import GeneratePostState
from .nodes import generate_post, condense_post, finalize_post
from ...utils.processing import remove_urls

logger = logging.getLogger(__name__)

# --- Conditional Edge Logic ---

def should_condense(state: GeneratePostState) -> Literal["condense_post", "finalize_post"]:
    """
    Checks if the generated post is too long and needs to be condensed.
    """
    post_content = state.get("post", "")
    post_content = post_content if post_content is not None else ""
    
    if len(remove_urls(post_content)) > 280 and state.get("condense_count", 0) < 3:
        logger.info("Post is too long, routing to condense_post.")
        return "condense_post"
    
    logger.info("Post is a good length, routing to finalize.")
    return "finalize_post"

# --- Graph Definition ---

def create_generate_post_graph():
    """
    Builds the simplified StateGraph for the social media post generation agent.
    """
    workflow = StateGraph(GeneratePostState)

    # Add the core post-generation nodes
    workflow.add_node("generate_post", generate_post)
    workflow.add_node("condense_post", condense_post)
    workflow.add_node("finalize_post", finalize_post)

    # === Define Edges and Control Flow ===
    workflow.set_entry_point("generate_post")
    
    # After generating, check if we need to condense
    workflow.add_conditional_edges("generate_post", should_condense)
    
    # After condensing, check again (this creates the loop)
    workflow.add_conditional_edges("condense_post", should_condense)
    
    # The final node, which prepares the output for the supervisor
    workflow.add_edge("finalize_post", END)

    # Compile the graph
    generate_post_graph = workflow.compile()
    generate_post_graph.name = "Generate Post Agent"
    return generate_post_graph

# Instantiate the final, compiled graph for import
generate_post_graph = create_generate_post_graph()