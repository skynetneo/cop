
import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from .state import GenerateReportState, Report
from ....config import get_llm
from ...utils.prompts import EXTRACT_KEY_DETAILS_PROMPT, GENERATE_REPORT_PROMPT_O1 # Assumed ported
from ...utils.parse import parse_report

logger = logging.getLogger(__name__)

async def extract_key_details(state: GenerateReportState, config) -> Dict[str, Any]:
    logger.info("Executing node: extract_key_details")
    llm = get_llm(config.get("llm_model", "default_model"))
    response = await llm.ainvoke(EXTRACT_KEY_DETAILS_PROMPT.format(content=state['page_contents']))
    key_details = response.get("key_details", "")
    if not key_details:
        raise ValueError("No key details extracted from the page contents.")
    return {"key_details": key_details}

async def generate_report(state: GenerateReportState, config) -> Dict[str, Any]:
    logger.info("Executing node: generate_report")
    llm = get_llm(config.get("llm_model", "default_model"))
    key_details = state.get("key_details", "")
    if not key_details:
        raise ValueError("Key details not found in state.")
    response = await llm.ainvoke(GENERATE_REPORT_PROMPT_O1.format(key_details=key_details))
    report_content = response.get("report_content", "")

def create_generate_report_graph() -> StateGraph:
    workflow = StateGraph(GenerateReportState)
    
    workflow.add_node("extract_key_details", extract_key_details)
    workflow.add_node("generate_report", generate_report)
    
    workflow.set_entry_point("extract_key_details")
    workflow.add_edge("extract_key_details", "generate_report")
    workflow.add_edge("generate_report", END)
    
    generate_report_graph = workflow.compile()
    generate_report_graph.name = "Generate Report Subgraph"
    return generate_report_graph

generate_report_graph = create_generate_report_graph()
