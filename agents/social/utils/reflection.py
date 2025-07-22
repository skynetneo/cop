
import logging
from typing import Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph_sdk import get_client

logger = logging.getLogger(__name__)

REFLECTIONS_NAMESPACE = ("reflection_rules",)
REFLECTIONS_KEY = "rules"
PROMPT_KEY = "prompt"

async def get_reflections_prompt(config: dict) -> str:
    """Gets the current reflection prompt from the store."""
    checkpoint_saver: Optional[BaseCheckpointSaver] = config['configurable'].get('checkpoint')
    if not checkpoint_saver:
        logger.warning("No checkpoint saver found in config. Cannot get reflections.")
        return "No reflection rules have been created yet."
    
    data = await checkpoint_saver.aget(REFLECTIONS_NAMESPACE, REFLECTIONS_KEY)
    return data.get(PROMPT_KEY, "No reflection rules have been created yet.")

async def run_reflection_graph(original_post: str, new_post: str, user_response: str, config: dict):
    """
    Triggers the reflection graph as a fire-and-forget background task.
    """
    try:
        
        client = get_client()
        thread_config = {"configurable": {"checkpoint": config["configurable"]["checkpoint"]}}
        await client.runs.create(
            assistant_id="reflection_assistant_id", # reflection graph
            thread_id=None, # Creates a new thread for each reflection
            input={"original_post": original_post, "new_post": new_post, "user_response": user_response},
            config=thread_config,
        )
        logger.info("Successfully triggered reflection graph.")
    except Exception as e:
        logger.error(f"Failed to trigger reflection graph: {e}")