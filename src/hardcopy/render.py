"""Render an Event into a Receipt (plain-text lines + optional QR payload)."""
import textwrap
from dataclasses import dataclass, field

from hardcopy.models import Event

KIND_LABELS = {
    "review_requested": "REVIEW REQUESTED",
    "mention": "MENTIONED",
    "assign": "ASSIGNED",
    "ci_activity": "CI",
}


@dataclass
class Receipt:
    lines: list[str] = field(default_factory=list)
    qr: str | None = None  # URL to encode; scan -> open on phone


def render(event: Event, width: int = 32) -> Receipt:
    r = Receipt()
    label = KIND_LABELS.get(event.kind, event.kind.upper())
    r.lines.append(f"[{event.source.upper()}] {label}".center(width))
    r.lines.append("-" * width)
    r.lines.extend(textwrap.wrap(event.title, width))
    if event.repo:
        r.lines.append(textwrap.shorten(event.repo, width))
    if event.actor:
        r.lines.append(f"by {event.actor}"[:width])
    r.lines.append(event.created_at.strftime("%a %d %b %H:%M"))
    r.qr = event.url
    return r
