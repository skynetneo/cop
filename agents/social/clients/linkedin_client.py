import os
import httpx
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class LinkedInClient:
    """
    A client for interacting with the LinkedIn API v2.
    """
    BASE_URL = "https://api.linkedin.com/v2"

    def __init__(self, access_token: str, person_urn: Optional[str] = None, organization_id: Optional[str] = None):
        """
        Initializes the LinkedIn client.
        
        Args:
            access_token: The OAuth 2.0 access token.
            person_urn: The URN of the person posting (e.g., 'urn:li:person:xxxx').
            organization_id: The ID of the organization to post as.
        """
        if not access_token:
            raise ValueError("LinkedIn access token must be provided.")
        if not person_urn and not organization_id:
            raise ValueError("Either person_urn or organization_id must be provided.")
            
        self.access_token = access_token
        self.person_urn = person_urn
        self.organization_id = organization_id
        self.client = httpx.AsyncClient(headers={
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202405" # Use a recent, fixed API version
        })

    @classmethod
    def from_env(cls) -> "LinkedInClient":
        """
        Creates a LinkedInClient instance from environment variables.
        """
        access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        person_urn = os.environ.get("LINKEDIN_PERSON_URN")
        organization_id = os.environ.get("LINKEDIN_ORGANIZATION_ID")
        
        return cls(access_token, person_urn, organization_id)

    def _get_author_string(self, post_to_organization: bool = False) -> str:
        """Determines the author URN based on the posting preference."""
        if post_to_organization:
            if not self.organization_id:
                raise ValueError("Organization ID is required to post to an organization.")
            return f"urn:li:organization:{self.organization_id}"
        
        if not self.person_urn:
            raise ValueError("Person URN is required to post as a person.")
        return self.person_urn

    async def create_text_post(self, text: str, post_to_organization: bool = False) -> Dict[str, Any]:
        """
        Creates a text-only post on LinkedIn.
        """
        author = self._get_author_string(post_to_organization)
        post_data = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        
        try:
            response = await self.client.post(f"{self.BASE_URL}/ugcPosts", json=post_data)
            response.raise_for_status() # Raises an exception for 4xx/5xx responses
            logger.info("Successfully created LinkedIn text post.")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create LinkedIn text post: {e.response.status_code} - {e.response.text}")
            raise

    async def _register_upload(self, author: str) -> Dict[str, Any]:
        """Step 1: Register an image upload request."""
        register_url = f"{self.BASE_URL}/assets?action=registerUpload"
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": author,
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }
        response = await self.client.post(register_url, json=payload)
        response.raise_for_status()
        return response.json()

    async def _upload_image(self, upload_url: str, image_buffer: bytes) -> None:
        """Step 2: Upload the image to the provided URL."""
        # Use a separate client for upload as it requires a different content type and no auth header
        async with httpx.AsyncClient() as upload_client:
            response = await upload_client.put(
                upload_url, 
                content=image_buffer, 
                headers={"Content-Type": "application/octet-stream"}
            )
            response.raise_for_status()

    async def create_image_post(self, text: str, image_buffer: bytes, post_to_organization: bool = False) -> Dict[str, Any]:
        """
        Creates a post with an image on LinkedIn.
        """
        author = self._get_author_string(post_to_organization)
        
        try:
            # Step 1 & 2: Register and upload the image
            register_response = await self._register_upload(author)
            asset_urn = register_response['value']['asset']
            upload_url = register_response['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            await self._upload_image(upload_url, image_buffer)

            # Step 3: Create the post with the uploaded image asset
            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "IMAGE",
                        "media": [{
                            "status": "READY",
                            "media": asset_urn
                        }]
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }

            response = await self.client.post(f"{self.BASE_URL}/ugcPosts", json=post_data)
            response.raise_for_status()
            logger.info("Successfully created LinkedIn image post.")
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to create LinkedIn image post: {e.response.status_code} - {e.response.text}")
            raise
