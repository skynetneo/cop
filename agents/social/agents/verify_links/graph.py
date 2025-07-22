
from langgraph.graph import StateGraph, END, Send
from .state import VerifyLinksState
from .nodes import (
    verify_youtube_content,
    verify_github_content,
    verify_general_content,
)
from ...utils.url_utils import get_url_type # Assume this utility is ported

def route_link_types(state: VerifyLinksState):
    """
    Routes each link to the appropriate verification node.
    This uses the 'Send' command to invoke nodes in parallel for each link.
    """
    sends = []
    for link in state['links']:
        url_type = get_url_type(link)
        if url_type == "youtube":
            sends.append(Send("verify_youtube_content", {"links": [link]}))
        elif url_type == "github":
            sends.append(Send("verify_github_content", {"links": [link]}))
        else: # general, twitter, reddit, etc.
            sends.append(Send("verify_general_content", {"links": [link]}))
    # If there are no links, end the subgraph
    return sends if sends else END

def create_verify_links_graph() -> StateGraph:
    workflow = StateGraph(VerifyLinksState)

    workflow.add_node("verify_youtube_content", verify_youtube_content)
    workflow.add_node("verify_github_content", verify_github_content)
    workflow.add_node("verify_general_content", verify_general_content)
    
    workflow.add_conditional_edges("__start__", route_link_types)

    # After each verification node runs, it's done.
    workflow.add_edge("verify_youtube_content", END)
    workflow.add_edge("verify_github_content", END)
    workflow.add_edge("verify_general_content", END)

    verify_links_graph = workflow.compile()
    verify_links_graph.name = "Verify Links Subgraph"
    return verify_links_graph

verify_links_graph = create_verify_links_graph()