
import os
import httpx
import logging
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_owner_repo_from_url(url: str) -> tuple[str, str]:
    """Extracts owner and repo name from a GitHub URL."""
    path_parts = urlparse(url).path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL")
    return path_parts[0], path_parts[1]

async def get_readme_content(repo_url: str) -> str:
    """Fetches the content of the README file for a given GitHub repo."""
    if not GITHUB_TOKEN:
        logger.warning("GITHUB_TOKEN not set. GitHub API requests may be rate-limited.")
    
    owner, repo = get_owner_repo_from_url(repo_url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(api_url, headers=HEADERS)
            response.raise_for_status()
            readme_data = response.json()
            # The content is base64 encoded
            import base64
            return base64.b64decode(readme_data['content']).decode('utf-8')
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch README for {repo_url}: {e}")
            return f"Error: Could not fetch README. Status code: {e.response.status_code}"