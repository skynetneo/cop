
import re
import logging

logger = logging.getLogger(__name__)

def _extract_tag_content(tag: str, text: str) -> str:
    """A helper to extract content from within a given XML tag."""
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    logger.warning(f"Could not find <{tag}> tag in the following text:\n{text}")
    return text # Fallback to returning the original text if parsing fails

def parse_report(llm_output: str) -> str:
    """Extracts the report content from the <report> tag."""
    return _extract_tag_content("report", llm_output)

def parse_post(llm_output: str) -> str:
    """Extracts the post content from the <post> tag."""
    return _extract_tag_content("post", llm_output)

def parse_schedule_date(llm_output: str) -> str:
    """A simple placeholder for parsing a scheduled date from LLM output."""
    # The original TS code did not show a complex parser here, so we assume
    # the LLM is good at formatting. A real implementation would be more robust.
    # We could use `_extract_tag_content` if the LLM wraps the date in a tag.
    return llm_output.strip()
