
from langgraph.graph import StateGraph, END
from .state import FindImagesState
from .nodes import find_images, validate_images, rerank_images

def should_validate(state: FindImagesState) -> str:
    return "validate_images" if state.get("image_options") else "__end__"

def create_find_images_graph() -> StateGraph:
    workflow = StateGraph(FindImagesState)
    
    workflow.add_node("find_images", find_images)
    workflow.add_node("validate_images", validate_images)
    workflow.add_node("rerank_images", rerank_images)
    
    workflow.set_entry_point("find_images")
    
    workflow.add_conditional_edges("find_images", should_validate)
    
    workflow.add_edge("validate_images", "rerank_images")
    workflow.add_edge("rerank_images", END)

    find_images_graph = workflow.compile()
    find_images_graph.name = "Find Images Subgraph"
    return find_images_graph
    
find_images_graph = create_find_images_graph()
