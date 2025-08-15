
from urllib.parse import urlparse

def get_url_type(url: str) -> str:
    """
    Determines the type of a URL based on its domain.
    """
    try:
        hostname = urlparse(url).hostname
        if not hostname:
            return "unknown"

        if "youtube.com" in hostname or "youtu.be" in hostname:
            return "youtube"
        if "github.com" in hostname:
            return "github"
        if "x.com" in hostname or "twitter.com" in hostname:
            return "twitter"
        if "reddit.com" in hostname:
            return "reddit"
        if "luma.com" in hostname or "lu.ma" in hostname:
            return "luma"
        return "general"
    except Exception:
        return "unknown"
