
import logging
from typing import Dict, Any, List

from langchain_core.runnables import RunnableConfig

from .state import GeneratePostState
from ....config import get_llm, LLMConfig
from ...prompts.generate_post import GENERATE_POST_PROMPT, CONDENSE_POST_PROMPT
from ...utils.parse import parse_post
from ...utils.processing import filter_links_for_post_content, remove_urls
from ...utils.scheduling import get_next_saturday_date
from ...prompts.reflection import  REFLECTION_PROMPT, get_prompts

logger = logging.getLogger(__name__)

async def generate_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Generates the initial social media post from the provided report and links.
    """
    logger.info("Executing node: generate_post")
    report = state["report"]
    relevant_links = state["relevant_links"]

    configurable = config.get("configurable", {})
    llm_config = configurable.get("llm_config", LLMConfig(temperature=0.5))
    post_model = get_llm(llm_config)
    
    reflections =  REFLECTION_PROMPT
    reflections_prompt_str = reflections.format(reflections=reflections)

    system_prompt = GENERATE_POST_PROMPT.format(reflectionsPrompt=reflections_prompt_str)
    
    user_prompt = f"""Here is the report on the content:
<report>{report}</report>
Here are the relevant links. At least one must be included in the final post.
<links>{filter_links_for_post_content(relevant_links)}</links>"""

    response = await post_model.ainvoke([
        ("system", system_prompt),
        ("user", user_prompt),
    ])
    
    post_content = parse_post(str(response.content))
    
    return {"post": post_content}

async def condense_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Condenses the post if it's too long.
    """
    logger.info("Executing node: condense_post")
    post = state["post"]
    report = state["report"]
    relevant_links = state["relevant_links"]
    
    configurable = config.get("configurable", {})
    llm_config = configurable.get("llm_config", LLMConfig(temperature=0.5))
    condense_model = get_llm(llm_config)
    
    reflections = get_prompts()
    reflections_prompt_str = REFLECTION_PROMPT.format(reflections=reflections)
    original_post_len = len(remove_urls(post or ""))

    system_prompt = CONDENSE_POST_PROMPT.format(
        report=report,
        links=filter_links_for_post_content(relevant_links),
        originalPostLength=original_post_len,
        reflectionsPrompt=reflections_prompt_str,
    )

    response = await condense_model.ainvoke([
        ("system", system_prompt),
        ("user", f"Here is the original post:\n\n{post}")
    ])
  

    return {
        "post": parse_post(str(response.content)),
        "condense_count": state.get("condense_count", 0) + 1,
    }

async def finalize_post(state: GeneratePostState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Selects the best image and suggests a schedule, preparing the final output.
    """
    logger.info("Executing node: finalize_post")
    
    final_image = None
    image_options = state.get("image_options")
    if image_options and isinstance(image_options, list) and len(image_options) > 0:
        # A simple strategy: pick the first image. A more complex one could use an LLM.
        best_image_url = image_options[0]
        final_image = {"imageUrl": best_image_url, "mimeType": "image/jpeg"} # Assuming jpeg
        
    return {
        "final_post": state["post"],
        "final_image": final_image,
        "suggested_schedule": get_next_saturday_date(),
    }