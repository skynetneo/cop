
from typing import List, TypedDict, Optional, Literal
from typing_extensions import Annotated
import tweepy

# Assuming these types are defined in a central `types.py` or similar
from ...clients.reddit_client import SimpleRedditPostWithComments

# --- Type Definitions for Data Structures ---

Source = Literal["github", "twitter", "latent_space", "ai_news", "reddit"]

class GitHubTrendingData(TypedDict):
    repoURL: str
    pageContent: str

class TweetV2WithURLs(TypedDict):
    # This structure should align with what your Twitter client returns,
    # plus the added external_urls field. We'll use tweepy's Tweet object
    # as a base reference.
    id: str
    text: str
    author_id: Optional[str]
    note_tweet: Optional[dict]
    entities: Optional[dict]
    external_urls: List[str]

class TweetsGroupedByContent(TypedDict):
    explanation: str
    tweets: List[TweetV2WithURLs]

class ThreadRunId(TypedDict):
    thread_id: str
    run_id: str

class CuratedData(TypedDict, total=False):
    tweetsGroupedByContent: Optional[List[TweetsGroupedByContent]]
    redditPosts: Optional[List[SimpleRedditPostWithComments]] # Assuming type from reddit_client
    generalContents: Optional[List[dict]]
    githubTrendingData: Optional[List[GitHubTrendingData]]

# --- State Definition for the CurateData Graph ---

class CurateDataState(TypedDict):
    """The state for the data curation graph."""
    
    # Final curated data object
    curatedData: Optional[CuratedData]

    # Raw ingested data from various sources
    rawTweets: Optional[List[tweepy.Tweet]]
    rawTrendingRepos: Optional[List[str]]
    rawRedditPosts: Optional[List[SimpleRedditPostWithComments]]
    aiNewsPosts: Optional[List[str]]
    generalUrls: Optional[List[str]]

    # Processed data
    validatedTweets: Optional[List[tweepy.Tweet]]
    tweetsGroupedByContent: Optional[List[TweetsGroupedByContent]]
    similarGroupIndices: Optional[List[int]]
    githubTrendingData: Optional[List[GitHubTrendingData]]
    redditPosts: Optional[List[dict]] # A more processed version
    
    # For kicking off post generation runs
    threadRunIds: Optional[List[ThreadRunId]]

    # Shared state with verify-links subgraph
    pageContents: Annotated[Optional[List[str]], lambda a, b: (a or []) + (b or [])]
    relevantLinks: Annotated[Optional[List[str]], lambda a, b: list(set((a or []) + (b or [])))]
    imageOptions: Annotated[Optional[List[str]], lambda a, b: list(set((a or []) + (b or [])))]


class CurateDataConfigurable(TypedDict, total=False):
    """Configurable fields for the data curation graph."""
    sources: List[Source]
    num_posts_per_subreddit: int