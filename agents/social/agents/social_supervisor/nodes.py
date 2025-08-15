
from typing import List, Dict, Literal, Optional
from typing_extensions import Annotated
import asyncio
from langgraph.graph.message import AnyMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

from ....config import get_llm, LLMConfig
from .state import SupervisorState, GroupedReport, Report, PostGenerationInfo

# --- Pydantic Schemas for Structured Output ---

class SimilarReportGroup(BaseModel):
    indices: List[int] = Field(
        description="A list of report indices that are similar enough to be grouped."
    )

class SimilarReports(BaseModel):
    """A tool schema to call when grouping similar reports."""
    similarReports: List[SimilarReportGroup] = Field(
        description="A list of objects, each containing an array of indices of similar reports."
    )

class PostTypeDecision(BaseModel):
    """The type of post to generate and the reasoning behind the decision."""
    reason: str = Field(description="The reasoning behind your decision.")
    type: Literal["thread", "post"] = Field(
        description="The type of post to generate. 'thread' for long-form posts, 'post' for shorter, more concise posts."
    )

# --- Node Implementations ---

def _format_report_key_details(reports: List[Report]) -> str:
    """Formats report details for the LLM prompt."""
    return "\n".join(
        f"<report index='{index}'>\n{report['keyDetails']}\n</report>"
        for index, report in enumerate(reports)
    )

async def group_reports(state: SupervisorState) -> dict:
    """
    Analyzes reports and groups them by topic similarity.
    """
    IDENTIFY_SIMILAR_REPORTS_PROMPT = """You are an advanced AI assistant... (prompt text)""" # Prompt skipped as requested
    
    model = get_llm(LLMConfig(llm="flash")).with_structured_output(
        SimilarReports, method="tool_calling", include_raw=False
    )
    
    formatted_prompt = ChatPromptTemplate.from_messages([
        ("system", IDENTIFY_SIMILAR_REPORTS_PROMPT),
        ("human", _format_report_key_details(state["reports"]))
    ])
    
    chain = formatted_prompt | model
    result = await chain.ainvoke({})

    processed_indices = set()
    grouped_reports: List[GroupedReport] = []

    for group in result.similarReports:
        if not group.indices:
            continue
        
        report_group = {
            "reports": [state["reports"][i]["report"] for i in group.indices],
            "keyDetails": [state["reports"][i]["keyDetails"] for i in group.indices],
        }
        grouped_reports.append(report_group)
        for i in group.indices:
            processed_indices.add(i)

    for i, report in enumerate(state["reports"]):
        if i not in processed_indices:
            grouped_reports.append({
                "reports": [report["report"]],
                "keyDetails": [report["keyDetails"]],
            })
            
    return {"groupedReports": grouped_reports}

def _format_determine_post_type_prompt(report: GroupedReport) -> List[AnyMessage]:
    """Formats the prompt for the determine_post_type node."""
    DETERMINE_POST_TYPE_PROMPT = """You're a highly skilled marketer... (prompt text)""" # Prompt skipped as requested
    
    if len(report["reports"]) == 1:
        user_message = f"""Here are the key details for the report:
<key-details>{report['keyDetails'][0] or "no key details"}</key-details>
And here is the full report:
<report>{report['reports'][0]}</report>
Please take your time, and identify the best type of post to generate for this report, and why! Thank you!"""
    else:
        details_and_reports = "\n".join(
            f"""<report index="{i}">{r}</report>\n<key-details index="{i}">{report['keyDetails'][i] or "no key details"}</key-details>"""
            for i, r in enumerate(report["reports"])
        )
        user_message = f"""Here are all of the key details & reports I've written for this post:
<key-details-and-reports>{details_and_reports}</key-details-and-reports>
Please take your time, and identify the best type of post to generate for these reports, and why! Thank you!"""

    return [("system", DETERMINE_POST_TYPE_PROMPT), ("human", user_message)]

async def determine_post_type(state: SupervisorState) -> dict:
    """
    For each group of reports, determines whether to generate a single post or a thread.
    """
    model = get_llm(LLMConfig(llm="anthropic")).with_structured_output(
        PostTypeDecision, method="tool_calling", include_raw=False
    )
    
    tasks = []
    for report_group in state["groupedReports"]:
        prompt = _format_determine_post_type_prompt(report_group)
        chain = prompt | model
        tasks.append(chain.ainvoke({}))

    decisions = await asyncio.gather(*tasks)
    
    report_and_post_type: List[PostGenerationInfo] = [
        {**decision.dict(), **report_group}
        for decision, report_group in zip(decisions, state["groupedReports"])
    ]
    
    return {"reportAndPostType": report_and_post_type}
    
