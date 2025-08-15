
from datetime import datetime, timedelta, date, time
import pytz
from dateutil.parser import parse as dateutil_parse
from typing import Union, Literal

# Type hint for the date priorities
DateType = Union[date, Literal["p1", "p2", "p3", "r1", "r2", "r3"]]

def get_next_saturday_date(hour=12, minute=0) -> datetime:
    """
    Get a datetime for the next Saturday at a specified time in PST/PDT.
    """
    today = datetime.now(pytz.timezone('America/Los_Angeles'))
    days_ahead = 5 - today.weekday()  # Saturday is 5 in Python's weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_saturday = today + timedelta(days=days_ahead)
    return next_saturday.replace(hour=hour, minute=minute, second=0, microsecond=0)

def timezone_to_utc(tz_name: str) -> datetime:
    """Returns the current time in a given timezone."""
    return datetime.now(pytz.timezone(tz_name))

def parse_date_response(date_string: str) -> DateType:
    """
    Parses a string into a DateType, handling priority levels and date strings.
    """
    cleaned_date = date_string.lower().strip()
    priority_levels = ["p1", "p2", "p3", "r1", "r2", "r3"]
    if cleaned_date in priority_levels:
        return cleaned_date
    
    try:
        # dateutil.parser is very flexible
        parsed_date = dateutil_parse(date_string)
        return parsed_date.date()
    except (ValueError, TypeError):
        # Fallback for invalid date strings, could also raise an error
        return "p3"
