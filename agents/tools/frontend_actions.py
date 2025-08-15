from typing import Optional, Dict, Any
from langchain_core.tools import tool


@tool
def show_resume_builder(prefill_data: Optional[Dict[str, Any]] = None) -> str:
    """Display the resume builder form to the user."""
    return "Displayed resume builder form"


@tool
def update_resume_data(section: str, data: Dict[str, Any], item_id: Optional[str] = None, action: str = "update") -> str:
    """Update or modify sections of the resume builder form."""
    return f"Updated resume section {section}"


@tool
def show_cover_letter_builder(job_title: Optional[str] = None, company_name: Optional[str] = None) -> str:
    """Display the cover letter builder form to the user."""
    return "Displayed cover letter builder form"
