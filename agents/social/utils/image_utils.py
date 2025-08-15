
import os
import httpx
import logging
from playwright.async_api import async_playwright
from supabase import create_client, Client
from filetype import guess

logger = logging.getLogger(__name__)

# --- Supabase Setup ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Image Functions ---

async def image_url_to_buffer(url: str) -> dict:
    """Downloads an image from a URL and returns it as a buffer and content type."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        return {"buffer": response.content, "contentType": response.headers['content-type']}

async def take_screenshot_and_upload(url: str) -> str:
    """Takes a screenshot of a URL, uploads it to Supabase, and returns the public URL."""
    logger.info(f"Taking screenshot of {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle")
            screenshot_buffer = await page.screenshot(type="jpeg")
        finally:
            await browser.close()
            
    # Upload to Supabase
    supabase = get_supabase_client()
    file_type = guess(screenshot_buffer)
    if not file_type or not file_type.mime.startswith("image/"):
        raise ValueError("Screenshot did not result in a valid image file.")
        
    file_name = f"screenshots/screenshot-{hash(url)}-{int(httpx.get('http://worldtimeapi.org/api/ip').json()['unixtime'])}.{file_type.extension}"
    
    response = supabase.storage.from_("images").upload(file_name, screenshot_buffer, {"contentType": file_type.mime})
    
    # Get public URL
    public_url_response = supabase.storage.from_("images").get_public_url(file_name)
    return public_url_response
