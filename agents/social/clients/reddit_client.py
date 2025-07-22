
import os
import json
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, TypedDict

import praw
from praw.models import Submission, Comment, MoreComments

# --- Type Definitions ---
# These types provide a simplified, consistent structure for Reddit data within our agent.

class SimpleRedditComment(TypedDict):
    id: str
    author: Optional[str]
    body: str
    created_utc: float
    replies: Optional[List["SimpleRedditComment"]]

class SimpleRedditPost(TypedDict):
    id: str
    title: str
    url: str
    created_utc: float
    selftext: str

class SimpleRedditPostWithComments(TypedDict):
    post: SimpleRedditPost
    comments: List[SimpleRedditComment]

# --- Client Implementation ---

class RedditClient:
    """
    An asynchronous wrapper for the Reddit API using PRAW (Python Reddit API Wrapper).

    Handles userless (app-only) authentication, fetches posts and comments,
    and simplifies the data structures for use within the agent.

    Required environment variables for `from_userless`:
    - REDDIT_CLIENT_ID
    - REDDIT_CLIENT_SECRET
    """
    reddit: praw.Reddit

    def __init__(self, reddit_instance: praw.Reddit):
        """Initializes the RedditClient with a PRAW instance."""
        self.reddit = reddit_instance

    @classmethod
    async def from_userless(cls) -> "RedditClient":
        """

        Creates a RedditClient instance using userless (app-only) authentication.
        Credentials are read from environment variables.
        """
        if not os.getenv("REDDIT_CLIENT_ID") or not os.getenv("REDDIT_CLIENT_SECRET"):
            raise ValueError("Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables.")

        # PRAW handles token management automatically for userless auth
        reddit_instance = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="SocialMediaAgent/1.0.0 by u/your_reddit_username", # Replace with your username
        )
        return cls(reddit_instance)

    async def get_top_posts(
        self, subreddit_name: str, limit: int = 15
    ) -> List[Submission]:
        """
        Fetches top posts from a subreddit for the last day.

        Args:
            subreddit_name: The name of the subreddit.
            limit: The maximum number of posts to retrieve.

        Returns:
            A list of PRAW Submission objects.
        """
        subreddit = await self.reddit.subreddit(subreddit_name)
        # PRAW's async methods are accessed via `await subreddit.top()`
        return [post async for post in subreddit.top(time_filter="day", limit=limit)]

    async def get_new_posts(
        self, subreddit_name: str, limit: int = 25
    ) -> List[Submission]:
        """
        Fetches the newest posts from a subreddit.

        Args:
            subreddit_name: The name of the subreddit.
            limit: The maximum number of posts to retrieve.

        Returns:
            A list of PRAW Submission objects.
        """
        subreddit = await self.reddit.subreddit(subreddit_name)
        return [post async for post in subreddit.new(limit=limit)]

    def simplify_post(self, post: Submission) -> SimpleRedditPost:
        """Converts a PRAW Submission object into a simplified dictionary."""
        return {
            "id": post.id,
            "title": post.title,
            "url": post.url,
            "created_utc": post.created_utc,
            "selftext": post.selftext,
        }

    def simplify_comment(self, comment: Comment) -> SimpleRedditComment:
        """
        Recursively converts a PRAW Comment object and its replies into a simplified dictionary.
        """
        replies = []
        if isinstance(comment, Comment) and hasattr(comment, 'replies'):
            # Fetch more replies if needed (if a MoreComments object exists)
            comment.replies.replace_more(limit=0) 
            for reply in comment.replies:
                if isinstance(reply, Comment):
                    replies.append(self.simplify_comment(reply))

        return {
            "id": comment.id,
            "author": str(comment.author) if comment.author else None,
            "body": comment.body,
            "created_utc": comment.created_utc,
            "replies": replies if replies else None,
        }

    async def get_post_comments(self, post_id: str, limit: int = 10, depth: int = 3) -> List[Comment]:
        """
        Fetches comments for a given post ID.
        
        Args:
            post_id: The ID of the Reddit post.
            limit: The number of top-level comments to fetch.
            depth: The depth of comment replies to fetch.
        
        Returns:
            A list of PRAW Comment objects.
        """
        submission = await self.reddit.submission(id=post_id)
        # Setting limit here controls top-level comments
        submission.comment_limit = limit
        # Setting depth via replace_more limit (0 means fetch all up to the depth)
        await submission.comments.replace_more(limit=None, threshold=depth)
        return submission.comments.list()

    async def get_post_by_url(self, url: str) -> Submission:
        """Fetches a submission object from a Reddit post URL."""
        return await self.reddit.submission(url=url)
    
    async def get_simple_post_and_comments(self, id_or_url: str) -> SimpleRedditPostWithComments:
        """
        Fetches a post and its comments, returning them in a simplified format.

        This method handles both post IDs and full URLs.
        
        Args:
            id_or_url: The ID or the full URL of the Reddit post.

        Returns:
            A simplified post object with its comments.
        """
        try:
            post = await self.get_post_by_url(id_or_url)
        except Exception:
            # If URL parsing fails, assume it's an ID
            post = await self.reddit.submission(id=id_or_url)
            await post.load() # Load the submission data

        comments = await self.get_post_comments(post.id)
        
        simple_comments = [
            self.simplify_comment(comment) 
            for comment in comments 
            if isinstance(comment, Comment)
        ]

        return {
            "post": self.simplify_post(post),
            "comments": simple_comments
        }