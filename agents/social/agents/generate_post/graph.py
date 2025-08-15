
import logging
from typing import Literal

from langgraph.graph import StateGraph, END

# Import the main state and nodes
from .state import GeneratePostState
from .nodes import (
    auth_socials_passthrough,
    generate_content_report,
    generate_post,
    condense_post,
    get_supervisor_approval,
    rewrite_post,
    update_suggested_schedule,
    rewrite_post_with_split_url,
    finalize_post,
)

# --- Import the compiled subgraphs ---
from ..verify_links.graph import verify_links_graph
from ..find_images.graph import find_images_graph

# Import utilities for conditional edges
from ...utils.stores import get_saved_urls
from ...utils.processing import remove_urls

logger = logging.getLogger(__name__)

# --- Conditional Edges (Unchanged from before) ---

async def should_generate_report(state: GeneratePostState, config) -> Literal["generate_content_report", "__end__"]:
    if not state.get("page_contents"):
        logger.info("No page content found after verification. Ending graph.")
        return "__end__"
    
    all_links = list(set(state.get("links", []) + state.get("relevant_links", [])))
    used_urls = await get_saved_urls(config) # Assumes this utility is ported
    if any(link in used_urls for link in all_links):
        logger.info("One or more URLs have been used previously. Ending graph.")
        return "__end__"
        
    return "generate_content_report"

def route_after_report(state: GeneratePostState) -> Literal["generate_post", "__end__"]:
    if state.get("report"):
        return "generate_post"
    logger.info("Report is empty, content likely irrelevant. Ending graph.")
    return "__end__"

def should_condense_or_proceed(state: GeneratePostState, config) -> Literal["condense_post", "find_images_subgraph"]:
    post_content = state.get("post", "")
    # Check text_only_mode from config if you want to skip images
    text_only_mode = config.get("configurable", {}).get("text_only_mode", False)

    if len(remove_urls(post_content)) > 280 and state.get("condense_count", 0) < 3:
        logger.info("Post is too long, routing to condense_post.")
        return "condense_post"
    
    if text_only_mode:
        logger.info("Text-only mode enabled, skipping image search.")
        return "get_supervisor_approval"

    return "find_images_subgraph"

def route_after_supervisor(state: GeneratePostState) -> str:
    next_node = state.get("next_node")
    if next_node:
        logger.info(f"Routing to '{next_node}' based on supervisor feedback.")
        # Clear the next_node so we don't get stuck in a loop
        state["next_node"] = None
        return next_node
    
    logger.info("Supervisor approved or gave no specific action. Routing to finalize.")
    return "finalize_post"


# --- Graph Definition ---

def create_generate_post_graph() -> StateGraph:
    """
    Builds the final StateGraph for the social media post generation agent,
    integrating all nodes and subgraphs.
    """
    workflow = StateGraph(GeneratePostState)

    # === Add Nodes and Subgraphs ===
    
    # 1. Start with authentication passthrough
    workflow.add_node("auth_socials_passthrough", auth_socials_passthrough)
    
    # 2. Add the verify_links_graph as a node. LangGraph will handle the invocation.
    workflow.add_node("verify_links_subgraph", verify_links_graph)

    # 3. Add the core post-generation nodes
    workflow.add_node("generate_content_report", generate_content_report)
    workflow.add_node("generate_post", generate_post)
    workflow.add_node("condense_post", condense_post)

    # 4. Add the find_images_graph as a node.
    workflow.add_node("find_images_subgraph", find_images_graph)

    # 5. Add the supervisor interaction and finalization nodes
    workflow.add_node("get_supervisor_approval", get_supervisor_approval)
    workflow.add_node("rewrite_post", rewrite_post)
    workflow.add_node("update_suggested_schedule", update_suggested_schedule)
    workflow.add_node("rewrite_with_split_url", rewrite_post_with_split_url)
    workflow.add_node("finalize_post", finalize_post)

    # === Define Edges and Control Flow ===
    
    workflow.set_entry_point("auth_socials_passthrough")
    
    workflow.add_edge("auth_socials_passthrough", "verify_links_subgraph")
    
    workflow.add_conditional_edges(
        "verify_links_subgraph",
        should_generate_report,
    )

    workflow.add_conditional_edges(
        "generate_content_report",
        route_after_report,
    )

    workflow.add_conditional_edges(
        "generate_post",
        should_condense_or_proceed,
    )
    
    workflow.add_conditional_edges(
        "condense_post",
        should_condense_or_proceed,
    )
    
    workflow.add_edge("find_images_subgraph", "get_supervisor_approval")

    workflow.add_conditional_edges(
        "get_supervisor_approval",
        route_after_supervisor,
        {
            "rewrite_post": "rewrite_post",
            "update_suggested_schedule": "update_suggested_schedule",
            "rewrite_with_split_url": "rewrite_with_split_url",
            "finalize_post": "finalize_post",
            # An edge case: if supervisor feedback is unclear, loop back
            "unknown_response": "get_supervisor_approval",
        }
    )
    
    # After an action is taken, loop back for another round of supervisor approval
    workflow.add_edge("rewrite_post", "get_supervisor_approval")
    workflow.add_edge("update_suggested_schedule", "get_supervisor_approval")
    workflow.add_edge("rewrite_with_split_url", "get_supervisor_approval")
    
    # The final node, which returns the result to the supervisor
    workflow.add_edge("finalize_post", END)

    # Compile the graph
    generate_post_graph = workflow.compile()
    generate_post_graph.name = "Social Media Post Generation Agent"
    return generate_post_graph

# Instantiate the final, compiled graph for import
generate_post_graph = create_generate_post_graph()
