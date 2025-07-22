
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

# --- Schema for Routing Supervisor Feedback ---

class RouteSupervisorFeedback(BaseModel):
    """
    A model to represent the decision on how to handle supervisor feedback.
    """
    route: Literal[
        "rewrite_post", 
        "update_date", 
        "rewrite_with_split_url", 
        "accept", 
        "unknown_response"
    ] = Field(
        description="The chosen route based on the supervisor's feedback."
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="A brief explanation for why a particular route was chosen."
    )


# --- Schemas for Image Validation and Reranking (from placeholders) ---

class VotableImage(BaseModel):
    """
    A model to represent a single image being evaluated for relevance.
    """
    index: int = Field(description="The index of the image being evaluated.")
    is_relevant: bool = Field(description="Whether the image is relevant to the post and report.")
    reasoning: str = Field(description="A brief reason for the relevance decision.")

class ImageValidationResponse(BaseModel):
    """
    A model to hold the list of validated images from a vision model.
    """
    validated_images: List[VotableImage] = Field(
        description="A list of evaluations for each image provided."
    )

class RerankedImages(BaseModel):
    """
    A model to hold the reranked order of images.
    """
    reranked_indices: List[int] = Field(
        description="A list of image indices, sorted from most to least relevant."
    )

# --- You could also add other schemas here as needed, for example: ---

class GeneratedPost(BaseModel):
    """
    A structured representation of a generated social media post.
    Useful if you want the LLM to return more than just the text.
    """
    post_text: str = Field(description="The main text content of the social media post.")
    suggested_emojis: Optional[List[str]] = Field(
        default=None, 
        description="A list of suggested emojis to accompany the post."
    )