import logging
from typing import Dict, Any, List

from langchain_core.runnables import RunnableConfig

from .state import GeneratePostState, ComplexPost
from ....config import get_llm, LLMConfig
from ...utils.prompts import (
    get_prompts,

    GENERATE_REPORT_PROMPT,
    GENERATE_POST_PROMPT,
    CONDENSE_POST_PROMPT,
    REWRITE_POST_PROMPT,
    REWRITE_WITH_SPLIT_URL_PROMPT,
    REFLECTION_PROMPT,
    SCHEDULE_POST_DATE_PROMPT,
)
from ...utils.parse import parse_report, parse_post, parse_schedule_date
from ...utils.processing import filter_links_for_post_content, remove_urls
from ...utils.reflection import get_reflections_prompt, run_reflection_graph
from ...utils.scheduling import get_next_saturday_date, timezone_to_utc, parse_date_response
from ...utils.routing import route_supervisor_feedback

# Setup logger
logger = logging.getLogger(__name__)


# --- Node Implementations ---

async def auth_socials_passthrough(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Placeholder for social media authentication checks.
    In a real-world scenario, this would use client libraries to verify tokens.
    For this tool-based agent, we assume the supervisor provides valid credentials
    or handles auth, so this node might simply passthrough or perform a basic check.
    """
    logger.info("Executing node: auth_socials_passthrough")
    # In this new architecture, the supervisor is responsible for providing credentials
    # that will be used by the clients. We can assume they are valid.
    # If a check were needed, it would happen here.
    return {}

async def generate_content_report(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Generates a detailed report based on the web page contents.
    """
    logger.info("Executing node: generate_content_report")
    if not state.get("page_contents"):
        logger.warning("No page_contents found to generate report. Skipping.")
        return {"report": None}

    llm_config = config["configurable"].get("llm_config", LLMConfig())
    report_model = get_llm(llm_config)

    page_contents_str = "\n\n".join(
        [f"<Content index={i+1}>\n{content}\n</Content>" for i, content in enumerate(state["page_contents"])]
    )
    
    prompt = f"""The following text contains summaries, or entire pages from the content I submitted to you. Please review the content and generate a report on it.
{page_contents_str}"""

    response = await report_model.ainvoke([
        {"role": "system", "content": GENERATE_REPORT_PROMPT},
        {"role": "user", "content": prompt},
    ])

    report = parse_report(response.content)
    return {"report": report}

async def generate_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Generates the initial social media post from the report.
    """
    logger.info("Executing node: generate_post")
    report = state.get("report")
    relevant_links = state.get("relevant_links")

    if not report or not relevant_links:
        logger.error("Missing report or relevant_links to generate post.")
        return {}

    llm_config = config["configurable"].get("llm_config", LLMConfig(temperature=0.5))
    post_model = get_llm(llm_config)
    
    reflections = await get_reflections_prompt(config)
    reflections_prompt_str = REFLECTION_PROMPT.format(reflections=reflections)

    system_prompt = GENERATE_POST_PROMPT.format(reflectionsPrompt=reflections_prompt_str)
    
    user_prompt = f"""Here is the report I wrote on the content I'd like promoted:
<report>
{report}
</report>

Here are the relevant links. At least one must be included in the final post.
<links>
{filter_links_for_post_content(relevant_links)}
</links>"""

    response = await post_model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])
    
    post_content = parse_post(response.content)
    
    # Suggest a schedule, which the supervisor can override.
    suggested_schedule = get_next_saturday_date()

    return {
        "post": post_content,
        "suggested_schedule": suggested_schedule,
        "condense_count": 0 # Initialize condense_count
    }

async def condense_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Condenses the post if it's too long.
    """
    logger.info("Executing node: condense_post")
    post = state.get("post")
    report = state.get("report")
    relevant_links = state.get("relevant_links")
    
    if not all([post, report, relevant_links]):
        logger.error("Missing required state to condense post.")
        return {}

    llm_config = config["configurable"].get("llm_config", LLMConfig(temperature=0.5))
    condense_model = get_llm(llm_config)
    
    reflections = await get_reflections_prompt(config)
    reflections_prompt_str = REFLECTION_PROMPT.format(reflections=reflections)

    original_post_len = len(remove_urls(post))

    system_prompt = CONDENSE_POST_PROMPT.format(
        report=report,
        links=filter_links_for_post_content(relevant_links),
        originalPostLength=original_post_len,
        reflectionsPrompt=reflections_prompt_str,
        postStructureInstructions=get_prompts().post_structure_instructions,
        postContentRules=get_prompts().post_content_rules
    )

    response = await condense_model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the original post:\n\n{post}"},
    ])

    return {
        "post": parse_post(response.content),
        "condense_count": state.get("condense_count", 0) + 1,
    }

async def rewrite_post_with_split_url(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Rewrites the post to split the main content from the URL, creating a thread.
    """
    logger.info("Executing node: rewrite_post_with_split_url")
    post = state.get("post")
    if not post:
        logger.error("No post found to rewrite with split URL.")
        return {}
    
    llm_config = config["configurable"].get("llm_config")
    post_model = get_llm(llm_config)
    
    rewriter = post_model.with_structured_output(ComplexPost)
    
    prompt = REWRITE_WITH_SPLIT_URL_PROMPT.format(POST=post)
    
    rewritten_post: ComplexPost = await rewriter.ainvoke(prompt)
    
    return {"complex_post": rewritten_post}

async def rewrite_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Rewrites the post based on supervisor feedback.
    """
    logger.info("Executing node: rewrite_post")
    original_post = state.get("post")
    feedback = state.get("supervisor_feedback")

    if not original_post or not feedback:
        logger.error("Missing original_post or supervisor_feedback for rewriting.")
        return {}

    llm_config = config["configurable"].get("llm_config", LLMConfig(temperature=0.5))
    rewrite_model = get_llm(llm_config)

    reflections = await get_reflections_prompt(config)
    reflections_prompt_str = REFLECTION_PROMPT.format(reflections=reflections)

    system_prompt = REWRITE_POST_PROMPT.format(
        originalPost=original_post,
        reflectionsPrompt=reflections_prompt_str,
    )
    
    response = await rewrite_model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": feedback},
    ])

    new_post = response.content

    # Trigger reflection graph as a fire-and-forget subprocess
    await run_reflection_graph(
        original_post=original_post,
        new_post=new_post,
        user_response=feedback,
        config=config
    )

    return {
        "post": new_post,
        "next_node": None,
        "supervisor_feedback": None
    }

async def update_suggested_schedule(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Updates the suggested schedule based on supervisor feedback.
    """
    logger.info("Executing node: update_suggested_schedule")
    feedback = state.get("supervisor_feedback")
    if not feedback:
        logger.error("No supervisor_feedback found to update schedule.")
        return {}

    llm_config = config["configurable"].get("llm_config", LLMConfig(temperature=0.5))
    schedule_model = get_llm(llm_config)

  
    current_time_pst = timezone_to_utc("America/Los_Angeles").isoformat()
    system_prompt = SCHEDULE_POST_DATE_PROMPT.format(currentDateAndTime=current_time_pst)

    response = await schedule_model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": feedback},
    ])
    
    date_str = parse_schedule_date(response.content)
    new_schedule = parse_date_response(date_str)

    return {
        "suggested_schedule": new_schedule,
        "next_node": None,
        "supervisor_feedback": None,
    }

async def get_supervisor_approval(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    This is the new "humanNode". It pauses the graph and waits for the supervisor.
    The supervisor will review the state and provide feedback, which resumes the graph.
    """
    logger.info("Executing node: get_supervisor_approval")

    feedback = state.get("supervisor_feedback")

    if not feedback:
       
        logger.info("Awaiting supervisor approval/feedback.")
      
        return {"review_request": {"post": state.get("post"), "image": state.get("image")}}
        
    # If we are here, it means the supervisor has provided feedback and reinvoked the graph.
    logger.info(f"Supervisor provided feedback: {feedback}")

    # Use an LLM to route the feedback to the correct next step.
    route = await route_supervisor_feedback(
        post=state.get("post", ""),
        date_or_priority=str(state.get("suggested_schedule", "p1")),
        supervisor_response=feedback,
        llm_config=config["configurable"].get("llm_config")
    )
    
    if route == "rewrite_post":
        return {"next_node": "rewritePost"}
    elif route == "update_date":
        return {"next_node": "updateScheduleDate"}
    elif route == "rewrite_with_split_url":
        return {"next_node": "rewriteWithSplitUrl"}
    else: # "unknown_response" or "accept"
        # If the supervisor approves (e.g., by responding with "ok", "looks good"),
        # or gives an unknown response, we proceed to the final step.
        return {"next_node": "finalizePost"}

async def finalize_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    This is the new "schedulePost" node. Instead of scheduling directly, it prepares
    the final output for the supervisor agent. The supervisor is responsible for the
    actual scheduling using its own tools.
    """
    logger.info("Executing node: finalize_post")
    
    # This node's job is to return the final, approved post details.
    final_output = {
        "post_content": state.get("post"),
        "complex_post_content": state.get("complex_post"),
        "image_details": state.get("image"),
        "schedule_details": state.get("suggested_schedule"),
    }
    
    # The supervisor can now take this output and use its scheduling tools.
    return {"final_output": final_output}
