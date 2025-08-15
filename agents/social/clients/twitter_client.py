
import os
import tweepy
import logging
from typing import List, Optional, Union

# Define a type for a single tweet request
class CreateTweetRequest(dict):
    text: str
    media_ids: Optional[List[str]] = None

logger = logging.getLogger(__name__)

class TwitterClient:
    """
    A client for interacting with the Twitter API v2 using tweepy.
    """
    def __init__(self, consumer_key: str, consumer_secret: str, access_token: str, access_token_secret: str):
        """
        Initializes the Twitter client with API credentials.
        """
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("All Twitter API credentials must be provided.")
        
        # v2 API client
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # v1.1 API client is needed for media uploads
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        self.api_v1 = tweepy.API(auth)

    @classmethod
    def from_env(cls) -> "TwitterClient":
        """
        Creates a TwitterClient instance from environment variables.
        """
        consumer_key = os.environ.get("TWITTER_API_KEY")
        consumer_secret = os.environ.get("TWITTER_API_KEY_SECRET")
        access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        
        return cls(consumer_key, consumer_secret, access_token, access_token_secret)

    async def upload_media(self, media_buffer: bytes, mime_type: str) -> Optional[str]:
        """
        Uploads a media file (buffer) to Twitter.
        
        Args:
            media_buffer: The media content as a byte buffer.
            mime_type: The MIME type of the media.

        Returns:
            The media ID string from Twitter, or None if upload fails.
        """
        try:
            # Tweepy's media_upload expects a filename, so we must write to a temp file.
            # A more advanced implementation might use a more direct method if the library allows.
            # For simplicity here, we'll use the available method.
            # Note: This is a synchronous call, wrap in to_thread for async contexts if it's blocking.
            media = self.api_v1.media_upload(filename="upload", file=media_buffer)
            return media.media_id_string
        except tweepy.errors.TweepyException as e:
            logger.error(f"Failed to upload media to Twitter: {e}")
            return None

    async def upload_tweet(self, text: str, media_buffer: Optional[bytes] = None, mime_type: Optional[str] = None) -> dict:
        """
        Posts a single tweet, with an optional media attachment.
        
        Args:
            text: The text content of the tweet.
            media_buffer: Optional media content as a byte buffer.
            mime_type: The MIME type of the media, required if media_buffer is provided.

        Returns:
            The Twitter API response.
        """
        media_ids = []
        if media_buffer and mime_type:
            media_id = await self.upload_media(media_buffer, mime_type)
            if media_id:
                media_ids.append(media_id)

        try:
            response = self.client.create_tweet(text=text, media_ids=media_ids if media_ids else None)
            logger.info(f"Successfully posted tweet: {response.data['id']}")
            return response.data
        except tweepy.errors.TweepyException as e:
            logger.error(f"Failed to post tweet: {e}")
            raise

    async def upload_thread(self, posts: List[CreateTweetRequest]) -> List[dict]:
        """
        Posts a sequence of tweets as a thread.
        Media can be attached to any tweet in the thread.
        
        Args:
            posts: A list of CreateTweetRequest dictionaries.

        Returns:
            A list of Twitter API responses for each tweet in the thread.
        """
        if not posts:
            return []

        responses = []
        reply_to_tweet_id = None

        for i, post in enumerate(posts):
            try:
                response = self.client.create_tweet(
                    text=post['text'], 
                    media_ids=post.get('media_ids'),
                    in_reply_to_tweet_id=reply_to_tweet_id
                )
                logger.info(f"Successfully posted tweet {i+1}/{len(posts)} of thread: {response.data['id']}")
                responses.append(response.data)
                reply_to_tweet_id = response.data['id']
            except tweepy.errors.TweepyException as e:
                logger.error(f"Failed to post tweet {i+1} in thread: {e}")
                # Optional: Decide whether to stop the thread on failure or continue
                raise

        return responses
