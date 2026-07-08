"""Wire it all together: sources -> dedupe -> rules -> render -> print."""
import asyncio
import logging
import os
from datetime import datetime, time

import yaml
from dotenv import load_dotenv

from hardcopy.models import Event
from hardcopy.printers.console import ConsolePrinter
from hardcopy.printers.escpos_printer import EscposPrinter
from hardcopy.render import render
from hardcopy.rules import decide
from hardcopy.sources.github_poller import GitHubPoller
from hardcopy.store import Store

log = logging.getLogger("hardcopy")


def is_quiet(cfg: dict) -> bool:
    """Return True if current local time falls within the quiet-hours window."""
    qh = cfg.get("quiet_hours", {})
    if not qh.get("enabled"):
        return False
    now = datetime.now().time()
    start = time.fromisoformat(qh["start"])
    end = time.fromisoformat(qh["end"])
    if start <= end:
        return start <= now <= end
    # Midnight crossing (e.g. 22:00 -> 08:00)
    return now >= start or now <= end


async def drain_queue(store: Store, printer, width: int) -> None:
    """Print all queued events. Stop on first failure (printer still down)."""
    queued = store.dequeue_all()
    for event_id, event_json in queued:
        try:
            event = Event.model_validate_json(event_json)
            printer.print(render(event, width))
            store.remove_queued(event_id)
            log.info("drain %s %s", event.kind, event.title)
        except Exception:
            log.warning("drain failed — printer still offline, %d remain", len(queued))
            break


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()  # local dev; no-op in Docker where env_file injects vars
    if not os.environ.get("GITHUB_TOKEN"):
        raise SystemExit("GITHUB_TOKEN not set — copy .env.example to .env and add your PAT")
    cfg = yaml.safe_load(open("config.yaml"))

    store = Store(cfg["store"]["path"])
    printer = (
        ConsolePrinter()
        if cfg["printer"]["type"] == "console"
        else EscposPrinter(cfg["printer"])
    )
    width = cfg["printer"].get("width", 32)
    consecutive_failures = 0

    # Phase 1: single source. Later: asyncio.gather over all enabled sources.
    source = GitHubPoller(cfg["sources"]["github"]["poll_interval"])
    log.info("hardcopy up — polling %s", source.name)

    async for event in source.events():
        if not store.is_new(event.id):
            continue
        priority = decide(event, cfg["rules"])
        if priority is None:
            log.info("drop  %s %s", event.kind, event.title)
            continue

        if is_quiet(cfg):
            store.enqueue(event.id, event.model_dump_json())
            log.info("queue %s %s (quiet hours)", event.kind, event.title)
            continue

        log.info("print %s %s", event.kind, event.title)
        try:
            printer.print(render(event, width))
            consecutive_failures = 0
            # After a successful print, drain any queued events
            await drain_queue(store, printer, width)
        except Exception:
            consecutive_failures += 1
            backoff = min(2**consecutive_failures * 5, 300)
            log.exception("print failed — queuing, retry in %ds", backoff)
            store.enqueue(event.id, event.model_dump_json())
            await asyncio.sleep(backoff)


if __name__ == "__main__":
    asyncio.run(main())
