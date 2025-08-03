
import re
from typing import Dict, Any, List

from .state import GenerateReportState, Report
from ....config import get_llm, LLMConfig
from ...prompts.extract_details import EXTRACT_KEY_DETAILS_PROMPT
from ...prompts.generate_report import GENERATE_REPORT_PROMPT

def _format_content_for_prompt(page_contents: List[str]) -> str:
    """Formats a list of page contents into a single string for the LLM."""
    if not page_contents:
        return "No content provided."
    return "\n\n".join(
        f"<Content index={i+1}>\n{content}\n</Content>"
        for i, content in enumerate(page_contents)
    )

async def extract_key_details(state: GenerateReportState) -> Dict[str, Any]:
    """
    Node to extract key details from the raw page content.
    This node reads `page_contents` and adds `key_details` to the state.
    """
    print("---GENERATE REPORT AGENT: EXTRACTING KEY DETAILS---")
    
    content_str = _format_content_for_prompt(state["page_contents"])
    
    # The prompt might be simple or complex
    prompt = f"Extract the key details from the following content:\n\n{content_str}"

    model = get_llm(LLMConfig(llm="flash"))
    
    response = await model.ainvoke(prompt)
    
    # This node returns a dictionary to UPDATE the state.
    return {"key_details": str(response.content)}

async def generate_report(state: GenerateReportState) -> Dict[str, Any]:
    """
    Node to generate the final, structured report.
    This node reads `page_contents` and `key_details`.
    """
    print("---GENERATE REPORT AGENT: WRITING FINAL REPORT---")
    

    key_details = state.get("key_details")
    if not key_details:
        raise ValueError("Cannot generate report: key_details are missing from the state.")
        
    content_str = _format_content_for_prompt(state["page_contents"])

    # Placeholder for business context, which should be managed better
    BUSINESS_CONTEXT = input("Enter the business context for the report: ")
    
    prompt_template = GENERATE_REPORT_PROMPT
    
    system_prompt = (
        prompt_template
        .replace("{getPrompts().businessContext}", BUSINESS_CONTEXT)
        .replace("{keyDetails}", key_details)
    )
    
    model = get_llm(LLMConfig(llm="pro"))
    
    response = await model.ainvoke([
        ("system", system_prompt),
        ("user", content_str)
    ])
    
    def parse_generation(generation: str) -> str:
        match = re.search(r"<report>([\s\S]*?)</report>", generation, re.DOTALL)
        return match.group(1).strip() if match else generation

    report_content = parse_generation(str(response.content))
    
    final_report: Report = {
        "report": report_content,
        "key_details": key_details
    }
    
    return {"reports": [final_report]}