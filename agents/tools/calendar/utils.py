"""Google Calendar tool utils."""
from __future__ import annotations
import logging
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

if TYPE_CHECKING:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import Resource

logger = logging.getLogger(__name__)


def build_calendar_service(token_path="token.json", credentials_path="creds.json", scopes=None):
    scopes = scopes or ["https://www.googleapis.com/auth/calendar"]
    creds = Credentials.from_authorized_user_file(token_path, scopes)
    return build("calendar", "v3", credentials=creds)

def build_resouce_service(
    credentials: Optional[Credentials] = None,
    service_name: str = "calendar",
    service_version: str = "v3",
) -> Resource:
    warnings.warn(
        "build_resource_service is deprecated and will be removed in a future version."
        "Use build_calendar_service instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return build_calendar_service(credentials, service_name, service_version)

def is_all_day_event(start_datetime: str, end_datetime: str) -> bool:
    """Check if the event is all day."""
    try:
        datetime.strptime(start_datetime, "%Y-%m-%d")
        datetime.strptime(end_datetime, "%Y-%m-%d")
        return True
    except ValueError:
        return False
