"""Wire it all together: sources -> dedupe -> rules -> render -> print."""
import asyncio
import logging
import os

import yaml
from dotenv import load_dotenv

from hardcopy.printers.console import ConsolePrinter
from hardcopy.printers.escpos_printer import EscposPrinter
from hardcopy.render import render
from hardcopy.rules import decide
from hardcopy.sources.github_poller import GitHubPoller
from hardcopy.store import Store

log = logging.getLogger("hardcopy")


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
        log.info("print %s %s", event.kind, event.title)
        try:
            printer.print(render(event, width))
        except Exception:
            log.exception("print failed — Phase 2 spooler will add retry/backoff")


if __name__ == "__main__":
    asyncio.run(main())
