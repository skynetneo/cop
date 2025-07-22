
import asyncio
from typing import List
from langgraph_sdk import Client
from langgraph.graph import StateGraph, START, END, Send
from typing_extensions import Annotated, TypedDict, Literal, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from ....config import get_llm, LLMConfig
from .state import SupervisorState, Report, GroupedReport, PostGenerationInfo, GeneratedPostRun, CuratedData
from .nodes import group_reports, determine_post_type, PostTypeDecision, format_determine_post_type_prompt

async def determine_post_type(state: SupervisorState) -> dict:
    """
    Determines the type of post to generate for each group of reports.
    """
    model = get_llm(LLMConfig(llm="groq")).with_structured_output(
        PostTypeDecision, method="tool_calling", include_raw=False
    )
    
    tasks = []
    for report_group in state["groupedReports"]:
        prompt = format_determine_post_type_prompt(report_group)
        chain = prompt | model
        tasks.append(chain.ainvoke({}))

    decisions = await asyncio.gather(*tasks)
    
    # Collect decisions into a structured format
    report_and_post_type = [
        {
            "reports": report_group["reports"],
            "keyDetails": report_group["keyDetails"],
            "type": decision.type,
            "reason": decision.reason,
        }
        for report_group, decision in zip(state["groupedReports"], decisions)
    ]
    
    return {"reportAndPostType": report_and_post_type}

async def curate_data_graph(state: dict) -> dict:
    print(f"---Executing Curate Data Graph for: {state.keys()}---")
    # This would invoke the data curation subgraph and return curated data.
    await asyncio.sleep(1)
    return {
        "curatedData": {
            "tweetsGroupedByContent": [{"content": "Tweet 1"}, {"content": "Tweet 2"}],
            "redditPosts": [{"content": "Reddit Post 1"}, {"content": "Reddit Post 2"}],
            "generalContents": [{"content": "General Content 1"}],
            "githubTrendingData": [{"pageContent": "GitHub Repo 1", "repoURL": ""}, {"pageContent": "GitHub Repo 2", "repoURL": ""}],
        }
    }


async def generate_report_graph(state: dict) -> dict:
    print(f"---Executing Generate Report Graph for: {state.keys()}---")
    # This would generate a detailed report.
    await asyncio.sleep(1)
    report_text = f"Report on {state.get('pageContent', ['some content'])[0][:50]}..."
    key_details = f"Key details for {state.get('pageContent', ['some content'])[0][:50]}"
    return {"reports": [{"report": report_text, "keyDetails": key_details}]}


# This is the entry point node for the supervisor
async def ingest_data(state: SupervisorState) -> dict:
    """Invokes the data curation subgraph."""
    # In a real scenario, you'd pass specific sources from config
    config = {"configurable": {"sources": ["github", "twitter"]}}
    return await curate_data_graph(state)

def start_generate_report_runs(state: SupervisorState) -> List[Send]:
    """
    Dynamically creates parallel invocations of the generate_report_graph
    for each piece of curated data.
    """
    curated_data: CuratedData = state["curatedData"]
    sends = []
    
    # Example for GitHub data
    if "githubTrendingData" in curated_data:
        for item in curated_data["githubTrendingData"]:
            sends.append(
                Send(
                    "generate_report",
                    {
                        "pageContent": [item["pageContent"]],
                        "relevantLinks": [item["repoURL"]],
                    },
                )
            )
    # Example for Twitter data
    if "tweetsGroupedByContent" in curated_data:
        for item in curated_data["tweetsGroupedByContent"]:
            sends.append(
                Send(
                    "generate_report",
                    {
                        "pageContent": [item["content"]],
                        "relevantLinks": [],
                    },
                )
            )
    # Example for Reddit data
    if "redditPosts" in curated_data:
        for item in curated_data["redditPosts"]:
            sends.append(
                Send(
                    "generate_report",
                    {
                        "pageContent": [item["content"]],
                        "relevantLinks": [],
                    },
                )
            )
    # Example for general contents
    if "generalContents" in curated_data:
        for item in curated_data["generalContents"]:
            sends.append(
                Send(
                    "generate_report",
                    {
                        "pageContent": [item["content"]],
                        "relevantLinks": [],
                    },
                )
            )
            
    return sends

async def generate_posts(state: SupervisorState) -> dict:
    """
    Invokes the generate_post or generate_thread subgraphs for each
    grouped report.
    """
    client = Client() # Assumes default localhost URL or LANGGRAPH_API_URL env var
    tasks = []
    
    for item in state['reportAndPostType']:
        if item['type'] == 'thread':
            # Create a run for the 'generate_thread' graph
            task = client.runs.create(
                thread_id=(await client.threads.create())['thread_id'],
                assistant_id="generate_thread", # Name of the deployed graph
                input={"reports": item['reports']},
            )
        else: # 'post'
            # Create a run for the 'generate_post' graph
            task = client.runs.create(
                thread_id=(await client.threads.create())['thread_id'],
                assistant_id="generate_post",
                input={"report": "\n---\n".join(item['reports'])}
            )
        tasks.append(task)
        
    runs = await asyncio.gather(*tasks)
    
    ids_and_types = [
        {"type": item['type'], "thread_id": run['thread_id'], "run_id": run['run_id']}
        for item, run in zip(state['reportAndPostType'], runs)
    ]
    
    return {"idsAndTypes": ids_and_types}


# --- Graph Definition ---
builder = StateGraph(SupervisorState)

# Add nodes to the graph
builder.add_node("ingest_data", ingest_data)
builder.add_node("generate_report", generate_report_graph)
builder.add_node("group_reports", group_reports)
builder.add_node("determine_post_type", determine_post_type)
builder.add_node("generate_posts", generate_posts)

# Define the workflow edges
builder.add_edge(START, "ingest_data")

# After ingesting data, fan out to the report generation graph
builder.add_conditional_edges("ingest_data", start_generate_report_runs)

# After all report generation runs complete, group them
builder.add_edge("generate_report", "group_reports")

# After grouping, determine the post type for each group
builder.add_edge("group_reports", "determine_post_type")

# After determining types, generate the final posts
builder.add_edge("determine_post_type", "generate_posts")

# End the graph after posts are generated
builder.add_edge("generate_posts", END)

# Compile the graph
social_supervisor_graph = builder.compile()
social_supervisor_graph.name = "Social Supervisor"