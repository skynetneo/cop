import re
from typing import List
from urllib.parse import urlparse, urlunparse

def extract_urls(text: str) -> List[str]:
    """Extracts all URLs from a given string."""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)

def remove_urls(text: str) -> str:
    """Removes all URLs from a given string."""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.sub(url_pattern, '', text).strip()

def remove_tracking_params(url: str) -> str:
    """Removes common tracking parameters from a URL."""
    parsed = urlparse(url)
    # This list can be expanded
    tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'}
    
    # Filter out tracking parameters
    filtered_query = '&'.join(
        [f"{k}={v}" for k, v in [p.split('=') for p in parsed.query.split('&')] if k not in tracking_params]
    )
    
    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path, parsed.params, filtered_query, parsed.fragment)
    )

def filter_links_for_post_content(links: List[str]) -> str:
    """Prepares a list of links for inclusion in a prompt."""
    cleaned_links = [remove_tracking_params(link) for link in links]
    return "\n".join(f"- {link}" for link in cleaned_links)