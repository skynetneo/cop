
import logging
from typing import Dict, Any
import httpx
from bs4 import BeautifulSoup

from .state import VerifyLinksState
from ....config import get_llm, LLMConfig
from ...utils.github_utils import get_readme_content
from ...utils.url_utils import get_url_type

logger = logging.getLogger(__name__)

async def verify_youtube_content(state: VerifyLinksState, config) -> Dict[str, Any]:
    link = state['links'][0]
    logger.info(f"Verifying YouTube content for: {link}")
    
    llm_config = config["configurable"].get("llm_config", LLMConfig(llm="google:gemini-2.5-pro"))
    # Ensure supervisor chooses a model that supports multimodal input
    vision_model = get_llm(llm_config)
    
    # Gemini can take a video URI directly
    from langchain_core.messages import HumanMessage
    message = HumanMessage(
        content=[
            {"type": "text", "text": "Summarize this video for a social media post. Focus on key announcements, technical details, and the main takeaway."},
            {"type": "media", "mimeType": "video/mp4", "fileUri": link}
        ]
    )
    
    response = await vision_model.ainvoke([message])
    summary = response.content
    
    # Placeholder for getting thumbnail
    thumbnail_url = f"https://img.youtube.com/vi/{link.split('v=')[-1]}/maxresdefault.jpg"
    
    return {
        "relevant_links": [link],
        "page_contents": [summary],
        "image_options": [thumbnail_url],
    }

async def verify_github_content(state: VerifyLinksState, config) -> Dict[str, Any]:
    link = state['links'][0]
    logger.info(f"Verifying GitHub content for: {link}")
    
    readme = await get_readme_content(link)
    # Here, you could also add an LLM call to validate if the README is relevant
    # to your business context, but for now we assume it is.
    
    return {
        "relevant_links": [link],
        "page_contents": [readme],
    }

async def verify_general_content(state: VerifyLinksState, config) -> Dict[str, Any]:
    link = state['links'][0]
    logger.info(f"Verifying general content for: {link}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(link, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple text extraction. A real solution might use a library like `readability-lxml`.
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Find images
            image_urls = [img['src'] for img in soup.find_all('img') if img.get('src')]
            
            return {
                "relevant_links": [link],
                "page_contents": [content],
                "image_options": image_urls,
            }
        except Exception as e:
            logger.error(f"Failed to scrape general content from {link}: {e}")
            return {}
