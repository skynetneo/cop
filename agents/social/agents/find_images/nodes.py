
import logging
from typing import Dict, Any, List

from .state import FindImagesState
from ...utils.image_utils import take_screenshot_and_upload
from ...utils.processing import extract_urls
from ....config import get_llm, LLMConfig
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# Pydantic models for structured output
class VotableImage(BaseModel):
    index: int = Field(description="The index of the image being evaluated.")
    is_relevant: bool = Field(description="Whether the image is relevant to the post and report.")
    reasoning: str = Field(description="A brief reason for the relevance decision.")

class ImageValidationResponse(BaseModel):
    validated_images: List[VotableImage]

class RerankedImages(BaseModel):
    reranked_indices: List[int] = Field(description="List of image indices, from most to least relevant.")


async def find_images(state: FindImagesState, config) -> Dict[str, Any]:
    logger.info("Executing node: find_images")
    image_urls = set(state.get("image_options", []))

    # Extract images from markdown content
    for content in state.get("page_contents", []):
        urls = extract_urls(content)
        for url in urls:
            # A simple check for image file extensions
            if any(url.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                image_urls.add(url)
    
    # Take screenshot of the primary link
    if state.get("relevant_links"):
        screenshot_url = await take_screenshot_and_upload(state["relevant_links"][0])
        if screenshot_url:
            image_urls.add(screenshot_url)

    return {"image_options": list(image_urls)}


async def validate_images(state: FindImagesState, config) -> Dict[str, Any]:
    logger.info("Executing node: validate_images")
    image_options = state.get("image_options")
    if not image_options:
        return {}

    llm_config = config["configurable"].get("llm_config", LLMConfig(llm="vertexai"))
    vision_model = get_llm(llm_config).with_structured_output(ImageValidationResponse)

    prompt = f"""Review the following images and determine if they are relevant to the social media post and report below. Exclude logos, icons, and low-quality images.

Post: "{state['post']}"
Report: "{state['report'][:1000]}..."
"""
    
    messages = [
        {"type": "text", "text": prompt},
    ]
    for i, url in enumerate(image_options):
        messages.append({"type": "text", "text": f"Image Index: {i}"})
        messages.append({"type": "image_url", "image_url": {"url": url}})

    response: ImageValidationResponse = await vision_model.ainvoke([HumanMessage(content=messages)])
    
    relevant_urls = [
        image_options[img.index] for img in response.validated_images if img.is_relevant
    ]
    
    logger.info(f"Found {len(relevant_urls)} relevant images out of {len(image_options)}.")
    return {"image_options": relevant_urls}


async def rerank_images(state: FindImagesState, config) -> Dict[str, Any]:
    logger.info("Executing node: rerank_images")
    image_options = state.get("image_options")
    if not image_options:
        return {"image": None}
    if len(image_options) == 1:
        return {"image": {"imageUrl": image_options[0], "mimeType": "image/jpeg"}}

    llm_config = config["configurable"].get("llm_config", LLMConfig(llm="vertexai"))
    vision_model = get_llm(llm_config).with_structured_output(RerankedImages)
    
    prompt = f"""Please re-rank the following images from most to least relevant for this social media post. Return a list of indices in the new order.

Post: "{state['post']}"
"""
    # ... (similar message construction as validate_images) ...
    
    response: RerankedImages = await vision_model.ainvoke(...) # Pass constructed messages
    
    reranked_urls = [image_options[i] for i in response.reranked_indices]
    best_image_url = reranked_urls[0]
    
    return {"image": {"imageUrl": best_image_url, "mimeType": "image/jpeg"}}
