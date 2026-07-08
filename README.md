# hardcopy

Prints your important GitHub notifications on a thermal receipt printer.
Review request comes in, receipt comes out.

```
 ┌──────────────────────────────┐
 │  REVIEW REQUESTED            │
 │  ──────────────────────────  │
 │  fix(auth): token refresh    │
 │  race condition              │
 │                              │
 │  repo: acme/backend          │
 │  from: @alice                │
 │                              │
 │  ┌────────────┐              │
 │  │ ▄▄▄ ▄▄▄▄▄ │  scan to     │
 │  │ █▀█ █   █ │  open PR     │
 │  │ ▀▀▀ ▀▀▀▀▀ │              │
 │  └────────────┘              │
 │  2026-07-07 14:32            │
 └──────────────────────────────┘
```

## Why

Notifications get buried in inboxes and tabs. A receipt on your desk doesn't.
Hardcopy polls the GitHub Notifications API, filters by configurable rules,
and prints only what matters: review requests, mentions, and assignments.
Everything else gets dropped silently.

## Features

- **Poll-based** -- no inbound network access, no webhooks needed
- **Smart filtering** -- skip merged/closed PRs automatically, YAML rules for everything else
- **Network or USB printers** -- anything ESC/POS compatible (most thermal receipt printers)
- **WiFi bridge support** -- includes firmware for WT32-ETH01 to put Ethernet-only printers on WiFi
- **Quiet hours** -- queue overnight, flush as a morning batch
- **SQLite dedupe** -- never prints the same notification twice, survives restarts

## Quick start

```bash
cp .env.example .env          # add your GitHub PAT (notifications scope)
cp config.example.yaml config.yaml
uv sync
uv run python -m hardcopy     # console printer by default
```

## Configuration

Edit `config.yaml` to set your printer and notification rules:

```yaml
printer:
  type: network               # console | usb | network
  network:
    host: 192.168.1.50
    port: 9100

rules:
  - match: {source: github, kind: review_requested}
    action: print
    priority: high
  - match: {source: github, kind: mention}
    action: print
  - match: {}
    action: drop               # drop everything unmatched
```

See [config.example.yaml](config.example.yaml) for all options.

## Docker

```bash
docker compose up -d
```

Network printer: set `printer.network.host` in `config.yaml`.
USB printer: uncomment the `devices:` block in `compose.yaml` and pin to the node with the printer.

## WiFi bridge (optional)

If your receipt printer is Ethernet-only, the `bridge/` directory contains
firmware for a WT32-ETH01 (ESP32 + LAN8720A) that acts as a transparent
L2 WiFi-to-Ethernet bridge. The printer appears directly on your WiFi network
with its own MAC and IP. See [BRIDGE_AGENT_BRIEF.md](BRIDGE_AGENT_BRIEF.md)
for setup instructions.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details and data flow.

## Stack

Python 3.12+, httpx, python-escpos, SQLite, Pydantic, Docker Compose

## License

MIT
