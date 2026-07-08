"""Polls the GitHub Notifications API. No inbound network access required.

API notes:
- GET https://api.github.com/notifications (classic PAT, `notifications` scope)
- Send If-Modified-Since from the previous Last-Modified; a 304 costs no rate limit
- Respect max(config.poll_interval, X-Poll-Interval header)
- Thread `reason` maps directly to Event.kind:
  review_requested, mention, assign, author, ci_activity, subscribed, ...
"""
import asyncio
import logging
import os
from collections.abc import AsyncIterator
from datetime import datetime, timezone

import httpx

log = logging.getLogger("hardcopy")

from hardcopy.models import Event
from hardcopy.sources.base import Source

API = "https://api.github.com/notifications"


class GitHubPoller(Source):
    name = "github"

    def __init__(self, poll_interval: int = 60) -> None:
        self.poll_interval = poll_interval
        self._last_modified: str | None = None

    async def events(self) -> AsyncIterator[Event]:
        token = os.environ["GITHUB_TOKEN"]
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        async with httpx.AsyncClient(headers=headers, timeout=30) as client:
            while True:
                req_headers = {}
                if self._last_modified:
                    req_headers["If-Modified-Since"] = self._last_modified

                interval = self.poll_interval
                try:
                    resp = await client.get(API, headers=req_headers)
                    interval = max(interval, int(resp.headers.get("X-Poll-Interval", 0)))
                    if resp.status_code == 200:
                        self._last_modified = resp.headers.get("Last-Modified")
                        for thread in resp.json():
                            if await self._is_closed(client, thread):
                                continue
                            yield self._to_event(thread)
                    # 304: nothing new; anything else: log and retry next tick
                except httpx.HTTPError:
                    pass  # transient; next poll will retry

                await asyncio.sleep(interval)

    @staticmethod
    async def _is_closed(client: httpx.AsyncClient, thread: dict) -> bool:
        """Return True if the subject (PR/issue) is merged or closed."""
        subject = thread.get("subject", {})
        if subject.get("type") not in ("PullRequest", "Issue"):
            return False
        api_url = subject.get("url")
        if not api_url:
            return False
        try:
            resp = await client.get(api_url)
            if resp.status_code == 200:
                data = resp.json()
                state = data.get("state", "open")
                if state == "closed" or data.get("merged"):
                    log.debug("skip closed/merged: %s", subject.get("title"))
                    return True
        except httpx.HTTPError:
            pass
        return False

    @staticmethod
    def _to_event(thread: dict) -> Event:
        subject = thread.get("subject", {})
        # API url -> human url (best effort; QR falls back to repo page)
        html_url = (subject.get("url") or "").replace(
            "api.github.com/repos", "github.com"
        ).replace("/pulls/", "/pull/")
        return Event(
            id=f"github:thread:{thread['id']}:{thread.get('updated_at', '')}",
            source="github",
            kind=thread.get("reason", "unknown"),
            title=subject.get("title", "(no title)"),
            repo=thread.get("repository", {}).get("full_name"),
            url=html_url or thread.get("repository", {}).get("html_url"),
            created_at=datetime.fromisoformat(
                thread.get("updated_at", datetime.now(timezone.utc).isoformat())
            ),
        )
