"""The Event is the single contract between sources and the core."""
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Event(BaseModel):
    """One normalized notification, regardless of origin."""

    id: str            # stable, source-scoped dedupe key, e.g. "github:thread:12345"
    source: str        # "github" | "slack" | "email" | ...
    kind: str          # "review_requested" | "mention" | "assign" | ...
    title: str
    repo: str | None = None    # or channel/mailbox for other sources
    actor: str | None = None
    url: str | None = None
    body: str | None = None
    priority: Priority = Priority.NORMAL
    created_at: datetime
