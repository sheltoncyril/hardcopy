# hardcopy

Prints your important GitHub notifications on a thermal receipt printer.
Review request comes in, receipt comes out.

```
 ┌──────────────────────────────┐
 │   [GITHUB] REVIEW REQUESTED  │
 │  ──────────────────────────  │
 │  fix(auth): token refresh    │
 │  race condition              │
 │  acme/backend                │
 │  Tue 07 Jul 14:32            │
 │                              │
 │         [  QR CODE  ]        │
 │        scan to open PR       │
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
- **SQLite dedupe** -- never prints the same notification twice, survives restarts
- **Docker ready** -- single-container deployment with Compose

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

If your receipt printer is Ethernet-only, you can use a WT32-ETH01
(ESP32 + LAN8720A) as a transparent L2 WiFi-to-Ethernet bridge.
The printer appears directly on your WiFi network with its own MAC and IP.
See [wt32-eth01-wifi-bridge](https://github.com/sheltoncyril/wt32-eth01-wifi-bridge)
for firmware and setup instructions.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details and data flow.

## Stack

Python 3.12+, httpx, python-escpos, SQLite, Pydantic, Docker Compose
