import os
from typing import Literal, Dict, Any
from tavily import TavilyClient
from .graph import create_deep_agent
from .sub_agent import SubAgent

# Ensure TAVILY_API_KEY is set in your environment
if "TAVILY_API_KEY" not in os.environ:
    raise ValueError("TAVILY_API_KEY environment variable not set.")

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
) -> Dict[str, Any]:
    """Run a web search using Tavily."""
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return response

sub_research_prompt = """You are a dedicated researcher. Your job is to conduct research based on the user's questions.
Conduct thorough research and then reply with a detailed answer. Your FINAL answer will be passed on, so make it a comprehensive report."""

research_sub_agent: SubAgent = {
    "name": "research-agent",
    "description": "Used to research in-depth questions. Give this researcher one topic at a time.",
    "prompt": sub_research_prompt,
    "tools": ["internet_search"]
}

sub_critique_prompt = """You are a dedicated editor. Critique a report found at `final_report.md` based on the question in `question.txt`.
Provide a detailed critique focusing on clarity, comprehensiveness, structure, and factual accuracy. Do not rewrite the report yourself.
Things to check:
- Section naming and structure.
- Ensure it is text-heavy and comprehensive, not just bullet points.
- Check for missing details or shallow paragraphs.
- Verify it deeply analyzes causes, impacts, and trends.
- Confirm it directly answers the research question.
"""

critique_sub_agent: SubAgent = {
    "name": "critique-agent",
    "description": "Used to critique the final report. Provide guidance on what to critique.",
    "prompt": sub_critique_prompt,
    "tools": ["internet_search"]
}

research_instructions = """You are an expert researcher. Your job is to conduct thorough research and write a polished report.
First, write the original user question to `question.txt`.
Use the `research-agent` for deep research and the `critique-agent` to review your draft.
Write the final report to `final_report.md`. You can iterate on research and critiques as needed.

<report_instructions>
CRITICAL: The final report must be in the same language as the user's question.

Please create a detailed answer that:
1. Is well-organized with Markdown headings (#, ##, ###).
2. Includes specific facts and insights.
3. References sources using `[Title](URL)` format.
4. Provides a balanced, thorough analysis.
5. Includes a "Sources" section at the end.

<Citation Rules>
- Assign each unique URL a citation number [1], [2], etc.
- End with `### Sources` listing each source with its number.
- Example: `[1] Source Title: URL`
- Citations are critical.
</Citation Rules>
</report_instructions>

You have access to the `internet_search` tool to run searches.
"""

def get_research_agent():
    return create_deep_agent(
        [internet_search],
        research_instructions,
        subagents=[
            critique_sub_agent,
            research_sub_agent
        ],
    ).with_config({"recursion_limit": 100})


