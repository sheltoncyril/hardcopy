"""Ordered rules; first match wins. Unmatched events drop."""
from fnmatch import fnmatch

from hardcopy.models import Event, Priority


def decide(event: Event, rules: list[dict]) -> Priority | None:
    """Return a Priority to print with, or None to drop."""
    for rule in rules:
        if _matches(event, rule.get("match", {})):
            if rule.get("action") == "print":
                return Priority(rule.get("priority", "normal"))
            return None
    return None


def _matches(event: Event, match: dict) -> bool:
    if "source" in match and event.source != match["source"]:
        return False
    if "kind" in match and event.kind != match["kind"]:
        return False
    if "repo" in match and not fnmatch(event.repo or "", match["repo"]):
        return False
    return True
