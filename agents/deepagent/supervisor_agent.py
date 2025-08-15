import os
from typing import Dict, Any, Literal
from tavily import TavilyClient
from langchain_core.tools import tool

from .graph import create_deep_agent
from .sub_agent import SubAgent
from ..resources.search import search_for_agencies
from ..resources.chat import display_agencies
from ..tools.frontend_actions import (
    show_resume_builder,
    update_resume_data,
    show_cover_letter_builder,
)


@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> Dict[str, Any]:
    """Run a web search using Tavily."""
    api_key = os.getenv("TAVILY_API_KEY", "")
    client = TavilyClient(api_key=api_key)
    return client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_raw_content=include_raw_content,
        topic=topic,
    )


resources_sub_agent: SubAgent = {
    "name": "resources-agent",
    "description": "Finds local resources such as food banks or shelters.",
    "prompt": (
        "You help users locate local social service agencies. "
        "Use search_for_agencies to look up resources and display_agencies to show results."
    ),
    "tools": ["search_for_agencies", "display_agencies"],
}

resume_builder_sub_agent: SubAgent = {
    "name": "resume-builder",
    "description": "Guides users through creating a professional resume.",
    "prompt": (
        "Assist the user with building a resume. "
        "Use show_resume_builder to open the form and update_resume_data to fill sections."
    ),
    "tools": ["show_resume_builder", "update_resume_data"],
}

job_research_sub_agent: SubAgent = {
    "name": "job-research",
    "description": "Researches jobs, companies, or industries for the user.",
    "prompt": (
        "Perform job or company research and summarize findings for the user. "
        "Use internet_search to gather information."
    ),
    "tools": ["internet_search"],
}

cover_letter_sub_agent: SubAgent = {
    "name": "cover-letter-builder",
    "description": "Helps users craft personalized cover letters.",
    "prompt": (
        "Assist the user in writing a tailored cover letter. "
        "Use show_cover_letter_builder to display the form for editing."
    ),
    "tools": ["show_cover_letter_builder"],
}


def get_supervisor_agent():
    """Return the main agent with access to specialized sub-agents."""
    tools = [
        search_for_agencies,
        display_agencies,
        show_resume_builder,
        update_resume_data,
        show_cover_letter_builder,
        internet_search,
    ]
    subagents = [
        resources_sub_agent,
        resume_builder_sub_agent,
        job_research_sub_agent,
        cover_letter_sub_agent,
    ]
    instructions = (
        "You are a helpful assistant who can delegate complex tasks to specialized agents "
        "for researching jobs, finding community resources, and creating application materials."
    )
    return create_deep_agent(tools, instructions, subagents=subagents)
