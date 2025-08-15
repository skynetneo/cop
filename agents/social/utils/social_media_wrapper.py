from langchain_core.tools import tool, BaseTool
from typing import List, Optional, Any
from langgraph_sdk import get_client

SocialMediaToolInput = ""

class SocialMediaAgentWrapper(BaseTool):
    """A wrapper for the social media agent to be used as a tool."""

    def __init__(self, langgraph_client: Any):
        self.client = langgraph_client

    @tool("social_media_planner", args_schema=SocialMediaToolInput)
    async def plan(self, topic_summary: str, source_urls: Optional[List[str]] = None, image_url: Optional[str] = None, schedule_priority: str = "p2"):    
        pass
    @tool("social_media_post_generator", args_schema=SocialMediaToolInput)
    async def invoke(self, post_type: str, topic_summary: str, source_urls: Optional[List[str]] = None, image_url: Optional[str] = None, schedule_priority: str = "p2"):
        """
        Kicks off a process to generate and schedule a social media post or thread.
        This process is asynchronous and includes a human-in-the-loop review step.
        """
        # 1. Determine which graph (assistant) to call based on the post_type.
        assistant_id = "generate_thread" if post_type == "thread" else "generate_post"

        # 2. Prepare the initial input state for the graph.
        # We are "injecting" state to bypass the initial scraping/verification
        # steps by providing the report and links directly.
        # This makes the tool more direct and faster.
        initial_state = {
            "links": source_urls or [],
            "report": f"Content report based on supervisor request:\n\n{topic_summary}",
            "relevantLinks": source_urls or [],
            "scheduleDate": schedule_priority,
        }
        if image_url:
            initial_state["image"] = {"imageUrl": image_url, "mimeType": "image/jpeg"} # Assuming jpeg, could be fetched

        try:
            # 3. Create a new thread for this task.
            thread = await self.client.threads.create()
            thread_id = thread["thread_id"]

            # 4. Create the run. This is a "fire-and-forget" action from the supervisor's POV.
            # The social media agent will run independently and handle its own human-in-the-loop.
            run = await self.client.runs.create(
                thread_id,
                assistant_id,
                input={}, # Input is empty because we set the state directly
                command={
                    "goto": "generatePost", # Go directly to the post generation node
                    "update": initial_state
                }
            )

            # 5. Return a confirmation message to the supervisor.
            # Including IDs is crucial for observability.
            return f"Successfully started the social media agent to create a {post_type}. The task will proceed with a human review step. Run ID: {run['run_id']}, Thread ID: {thread_id}."

        except Exception as e:
            # It's important to handle errors and report them back to the supervisor.
            print(f"Error invoking social media agent: {e}")
            return f"Error: Could not start the social media agent. Details: {e}"
