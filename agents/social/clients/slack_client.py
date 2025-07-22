import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional, TypedDict

from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

# --- Type Definitions ---
# These types mirror the structure of the data we expect from the Slack API
# and the simplified format we'll use internally.

class SlackMessageAttachment(TypedDict, total=False):
    # Define fields for attachments if needed
    pass

class SlackMessageFile(TypedDict, total=False):
    # Define fields for files if needed
    pass

class SimpleSlackMessage(TypedDict):
    """A simplified, consistent representation of a Slack message."""
    id: str
    timestamp: str
    username: Optional[str]
    user: Optional[str]
    text: str
    type: str
    attachments: Optional[List[SlackMessageAttachment]]
    files: Optional[List[SlackMessageFile]]

# --- Client Implementation ---

class SlackClient:
    """
    An asynchronous wrapper around the Slack SDK for fetching messages and sending notifications.

    Handles communication with the Slack API, including fetching channel history,
    resolving channel names to IDs, and posting messages.

    Required Slack API Scopes:
    - 'channels:history': To fetch messages from a public channel.
    - 'groups:history': To fetch messages from a private channel.
    - 'channels:read', 'groups:read': To look up channels by name.
    - 'chat:write': To send messages.
    """
    client: AsyncWebClient
    channel_id: Optional[str]
    channel_name: Optional[str]

    def __init__(
        self,
        channel_id: Optional[str] = None,
        channel_name: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """
        Initializes the SlackClient.

        Args:
            channel_id: The ID of the Slack channel to interact with.
            channel_name: The name of the Slack channel (used if channel_id is not provided).
            token: The Slack Bot OAuth token. Defaults to SLACK_BOT_OAUTH_TOKEN env var.
        
        Raises:
            ValueError: If neither channel_id nor channel_name is provided, or if the token is missing.
        """
        if not channel_id and not channel_name:
            raise ValueError("Either channel_id or channel_name must be provided.")

        slack_token = token or os.getenv("SLACK_BOT_OAUTH_TOKEN")
        if not slack_token:
            raise ValueError(
                "Slack token not provided. Pass it to the constructor or set "
                "the SLACK_BOT_OAUTH_TOKEN environment variable."
            )

        self.client = AsyncWebClient(token=slack_token)
        self.channel_id = channel_id
        self.channel_name = channel_name

    def _convert_slack_messages_to_simple_messages(
        self, messages: List[dict]
    ) -> List[SimpleSlackMessage]:
        """
        Filters and maps raw Slack API message objects to a simplified, consistent format.
        
        Args:
            messages: A list of message objects from the Slack API.
            
        Returns:
            A list of messages formatted as SimpleSlackMessage.
        """
        simple_messages = []
        for msg in messages:
            # Ensure the message is a standard message with text and a timestamp.
            if msg.get("type") == "message" and msg.get("text") and msg.get("ts"):
                simple_messages.append(
                    {
                        "id": msg.get("client_msg_id"),
                        "timestamp": msg.get("ts"),
                        "username": msg.get("username"),
                        "user": msg.get("user"),
                        "text": msg.get("text"),
                        "type": msg.get("type"),
                        "attachments": msg.get("attachments"),
                        "files": msg.get("files"),
                    }
                )
        return simple_messages

    async def fetch_last_messages(
        self,
        max_messages: Optional[int] = 100,
        max_days_history: Optional[int] = 1,
    ) -> List[SimpleSlackMessage]:
        """
        Fetches recent messages from the configured Slack channel.

        Paginates through channel history to retrieve messages up to the specified limits.

        Args:
            max_messages: The maximum number of messages to retrieve.
            max_days_history: The maximum number of days to look back in the channel history.
        
        Returns:
            A list of simplified Slack messages.
        """
        if not self.channel_id:
            self.channel_id = await self.get_channel_id()
        
        try:
            oldest_timestamp = (
                datetime.now(timezone.utc) - timedelta(days=max_days_history)
            ).timestamp()
            
            messages = []
            cursor = None
            
            while True:
                limit = 100
                if max_messages:
                    remaining = max_messages - len(messages)
                    if remaining <= 0:
                        break
                    limit = min(remaining, 100)

                response = await self.client.conversations_history(
                    channel=self.channel_id,
                    oldest=str(oldest_timestamp),
                    limit=limit,
                    cursor=cursor,
                )
                
                if response.get("messages"):
                    messages.extend(response["messages"])

                if not response.get("has_more"):
                    break
                
                cursor = response.get("response_metadata", {}).get("next_cursor")

            return self._convert_slack_messages_to_simple_messages(messages)

        except SlackApiError as e:
            print(f"Error fetching Slack messages: {e.response['error']}")
            raise

    async def get_channel_id(self) -> str:
        """
        Retrieves the channel ID for the configured channel name.

        Paginates through all public and private channels the bot is a member of
        to find a match. Caches the result in `self.channel_id`.
        
        Returns:
            The found channel ID.
        
        Raises:
            ValueError: If the channel cannot be found.
        """
        if self.channel_id:
            return self.channel_id
        if not self.channel_name:
            raise ValueError("Channel name is not configured.")

        try:
            cursor = None
            while True:
                response = await self.client.conversations_list(
                    exclude_archived=True,
                    types="public_channel,private_channel",
                    limit=200,
                    cursor=cursor,
                )
                
                for channel in response.get("channels", []):
                    if channel.get("name") == self.channel_name:
                        self.channel_id = channel.get("id")
                        return self.channel_id

                if not response.get("response_metadata", {}).get("next_cursor"):
                    break
                cursor = response["response_metadata"]["next_cursor"]
            
            raise ValueError(f"Channel '{self.channel_name}' not found.")
        except SlackApiError as e:
            print(f"Error getting channel ID: {e.response['error']}")
            raise

    async def send_message(self, message: str) -> None:
        """
        Posts a message to the configured Slack channel.

        Args:
            message: The text of the message to send.
        """
        if not self.channel_id:
            self.channel_id = await self.get_channel_id()
            
        try:
            await self.client.chat_postMessage(
                channel=self.channel_id, text=message
            )
        except SlackApiError as e:
            print(f"Error sending Slack message: {e.response['error']}")
            raise