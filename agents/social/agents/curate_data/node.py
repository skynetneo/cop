import os
import asyncio
from typing import List, Optional, cast

import tweepy
from langgraph.graph.message import AnyMessage
from langchain_core.runnables import RunnableLambda, RunnableConfig
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from ...clients.twitter_client import TwitterClient
from ...clients.reddit_client import RedditClient
from ...clients.slack_client import SlackClient
from ....config import get_llm, LLMConfig
from ...utils import chunk_array, extract_urls, get_url_type
from ...utils.github_utils import get_repo_contents # Assuming this exists

from .state import (
    CurateDataState, CurateDataConfigurable, Source,
    SimpleRedditPostWithComments, TweetsGroupedByContent, TweetV2WithURLs
)

# Placeholder for loaders, which would be in a separate `loaders.py` file
async def twitter_loader_with_langchain(config: RunnableConfig) -> List[tweepy.Tweet]:
    # In a real implementation, this would call the Twitter client
    print("---(MOCK) Loading LangChain-related tweets---")
    return []

async def langchain_dependency_repos_loader(config: RunnableConfig) -> List[str]:
    print("---(MOCK) Loading GitHub repos with LangChain dependencies---")
    return ["https://github.com/langchain-ai/opengpts"]

async def get_langchain_reddit_posts(config: RunnableConfig) -> List[SimpleRedditPostWithComments]:
    print("---(MOCK) Loading LangChain-related Reddit posts---")
    return []

# --- Node Implementations ---

async def ingest_data(state: CurateDataState, config: RunnableConfig) -> dict:
    """
    Node to ingest data from various sources based on the configuration.
    """
    sources = cast(CurateDataConfigurable, config.get("configurable", {})).get("sources", [])
    if not sources:
        raise ValueError("No sources provided in configuration.")

    use_langchain_prompts = os.getenv("USE_LANGCHAIN_PROMPTS") == "true"
    
    # Using RunnableLambda to wrap loaders for better tracing
    tasks = {}
    if use_langchain_prompts:
        if "twitter" in sources:
            tasks["rawTweets"] = RunnableLambda(twitter_loader_with_langchain).ainvoke({}, config)
        if "github" in sources:
            tasks["rawTrendingRepos"] = RunnableLambda(langchain_dependency_repos_loader).ainvoke({}, config)
        if "reddit" in sources:
            tasks["rawRedditPosts"] = RunnableLambda(get_langchain_reddit_posts).ainvoke({}, config)
    else:
        # Implement non-LangChain specific loaders here if needed
        # For now, we'll keep it simple
        print("---(MOCK) Running generic ingestion loaders---")
        if "twitter" in sources: tasks["rawTweets"] = asyncio.sleep(1, [])
        if "github" in sources: tasks["rawTrendingRepos"] = asyncio.sleep(1, [])
        if "reddit" in sources: tasks["rawRedditPosts"] = asyncio.sleep(1, [])
        if "latent_space" in sources: tasks["generalUrls"] = asyncio.sleep(1, [])
        if "ai_news" in sources: tasks["aiNewsPosts"] = asyncio.sleep(1, [])
        
    results = await asyncio.gather(*tasks.values())
    return dict(zip(tasks.keys(), results))

class RelevantTweets(BaseModel):
    """Schema for the LLM to identify relevant tweets."""
    answer: List[int] = Field(description="A list of the index numbers of the relevant tweets.")

async def validate_bulk_tweets(state: CurateDataState) -> dict:
    """
    Node to validate a batch of tweets for relevance using an LLM.
    """
    raw_tweets = state.get("rawTweets")
    if not raw_tweets:
        return {"validatedTweets": []}

    VALIDATE_BULK_TWEETS_PROMPT = """You are an AI assistant... (prompt text)""" # Prompt skipped

    model = get_llm(LLMConfig(llm="anthropic")).with_structured_output(
        RelevantTweets, method="tool_calling", name="answer"
    )
    
    all_relevant_tweets = []
    for chunk in chunk_array(raw_tweets, 25):
        formatted_tweets = "\n".join(
            f"<tweet index='{i}'>{t.text or ''}</tweet>"
            for i, t in enumerate(chunk)
        )
        prompt = VALIDATE_BULK_TWEETS_PROMPT.replace("{TWEETS}", formatted_tweets)
        result = await model.ainvoke(prompt)
        
        answer_set = set(result.answer)
        relevant_in_chunk = [tweet for i, tweet in enumerate(chunk) if i in answer_set]
        all_relevant_tweets.extend(relevant_in_chunk)
        
    return {"validatedTweets": all_relevant_tweets}

# ... [Implementation for other nodes like extract_ai_newsletter_content] ...
# Due to complexity, we will mock the return of some nodes for now.
# A full implementation would require porting all the logic.

async def extract_ai_newsletter_content(state: CurateDataState) -> dict:
    """Mock implementation of newsletter content extraction."""
    print("---(MOCK) Extracting AI Newsletter Content---")
    # This would normally scrape newsletters, extract links, and fetch new content.
    return {}

class TweetGroups(BaseModel):
    explanation: str
    tweet_indices: List[int] = Field(description="List of tweet indices for this group.")

class AllTweetGroups(BaseModel):
    groups: List[TweetGroups]
    
async def group_tweets_by_content(state: CurateDataState) -> dict:
    """Node to group tweets by topic using an LLM."""
    GROUP_BY_CONTENT_PROMPT = """You're an advanced AI software engineer... (prompt text)""" # Skipped
    
    validated_tweets = state.get("validatedTweets")
    if not validated_tweets:
        return {"tweetsGroupedByContent": []}

    model = get_llm(LLMConfig(llm="openai", model_name="gpt-4o")).with_structured_output(
        AllTweetGroups, method="tool_calling"
    )

    formatted_tweets = "\n".join(
        f"<tweet index='{i}'>{t.text or ''}</tweet>"
        for i, t in enumerate(validated_tweets)
    )
    
    chain = ChatPromptTemplate.from_messages([
        ("system", GROUP_BY_CONTENT_PROMPT),
        ("human", f"<all-tweets>{formatted_tweets}</all-tweets>")
    ]) | model

    result = await chain.ainvoke({})

    tweets_grouped: List[TweetsGroupedByContent] = []
    for group in result.groups:
        tweets_in_group: List[TweetV2WithURLs] = []
        for index in group.tweet_indices:
            tweet = validated_tweets[index]
            # simplified for example
            tweets_in_group.append({
                "id": tweet.id,
                "text": tweet.text,
                "author_id": tweet.author_id,
                "note_tweet": None,
                "entities": None,
                "external_urls": extract_urls(tweet.text)
            })
        tweets_grouped.append({
            "explanation": group.explanation,
            "tweets": tweets_in_group
        })
    return {"tweetsGroupedByContent": tweets_grouped}

async def reflect_on_tweet_groups(state: CurateDataState) -> dict:
    """Mock node for reflecting on tweet groups."""
    print("---(MOCK) Reflecting on Tweet Groups---")
    return {"similarGroupIndices": []} # Assume no changes needed

async def re_group_tweets(state: CurateDataState) -> dict:
    """Mock node for re-grouping tweets."""
    print("---(MOCK) Re-grouping Tweets---")
    return {} # No changes

async def format_data(state: CurateDataState) -> dict:
    """Final node to format the curated data object."""
    curated_data = {
        "tweetsGroupedByContent": state.get("tweetsGroupedByContent"),
        "redditPosts": state.get("redditPosts"),
        "generalContents": [{
            "pageContent": pc,
            "relevantLinks": (state.get("relevantLinks") or [])
        } for pc in state.get("pageContents", [])],
        "githubTrendingData": state.get("githubTrendingData"),
    }
    return {"curatedData": curated_data}