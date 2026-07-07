from datetime import datetime, timezone

from hardcopy.models import Event, Priority
from hardcopy.rules import decide

RULES = [
    {"match": {"source": "github", "kind": "review_requested"}, "action": "print", "priority": "high"},
    {"match": {"source": "github", "kind": "mention", "repo": "org/*"}, "action": "print"},
    {"match": {}, "action": "drop"},
]


def ev(kind: str, repo: str = "org/app") -> Event:
    return Event(
        id=f"github:thread:1:{kind}", source="github", kind=kind, title="t",
        repo=repo, created_at=datetime.now(timezone.utc),
    )


def test_review_request_prints_high():
    assert decide(ev("review_requested"), RULES) == Priority.HIGH


def test_mention_repo_glob():
    assert decide(ev("mention", "org/app"), RULES) == Priority.NORMAL
    assert decide(ev("mention", "other/app"), RULES) is None


def test_default_drop():
    assert decide(ev("ci_activity"), RULES) is None
