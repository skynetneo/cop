
import logging
from typing import List, Optional, cast

from langgraph.checkpoint.base import BaseCheckpointSaver

logger = logging.getLogger(__name__)

# Constants for the namespace and keys, to avoid magic strings
NAMESPACE_USED_URLS = ("saved_data", "used_urls")
KEY_URLS = "urls"
OBJECT_KEY_DATA = "data"

async def get_saved_urls(config: dict) -> List[str]:
    """
    Retrieves the list of previously used URLs from the checkpoint store.
    
    Args:
        config: The runnable config, which must contain the 'checkpoint' saver.

    Returns:
        A list of saved URLs, or an empty list if none are found or no store is configured.
    """
    checkpoint_saver: Optional[BaseCheckpointSaver] = config.get("configurable", {}).get("checkpoint")
    if not checkpoint_saver:
        logger.warning("No checkpoint saver found in config. Cannot retrieve used URLs.")
        return []

    try:
        saved_data = await checkpoint_saver.aget(NAMESPACE_USED_URLS, KEY_URLS)
        if saved_data and isinstance(saved_data, dict) and OBJECT_KEY_DATA in saved_data:
            # Ensure the data is a list of strings
            urls = saved_data[OBJECT_KEY_DATA]
            if isinstance(urls, list):
                return [str(url) for url in urls]
        return []
    except Exception as e:
        logger.error(f"Error retrieving saved URLs from store: {e}")
        return []

async def save_used_urls(urls_to_save: List[str], config: dict):
    """
    Saves a list of URLs to the checkpoint store, merging with existing URLs.

    Args:
        urls_to_save: The new list of URLs to add to the store.
        config: The runnable config, containing the 'checkpoint' saver.
    """
    checkpoint_saver: Optional[BaseCheckpointSaver] = config.get("configurable", {}).get("checkpoint")
    if not checkpoint_saver:
        logger.warning("No checkpoint saver found in config. Cannot save used URLs.")
        return
        
    if not urls_to_save:
        return

    try:
        # First, get the existing URLs to avoid overwriting them
        existing_urls = await get_saved_urls(config)
        
        # Combine and deduplicate the URLs
        combined_urls = sorted(list(set(existing_urls + urls_to_save)))
        
        # Create the object to be stored
        data_to_store = {OBJECT_KEY_DATA: combined_urls}
        
        # Put the updated list back into the store
        await checkpoint_saver.aput(NAMESPACE_USED_URLS, KEY_URLS, data_to_store)
        logger.info(f"Successfully saved {len(combined_urls)} used URLs to the store.")
        
    except Exception as e:
        logger.error(f"Error saving used URLs to store: {e}")