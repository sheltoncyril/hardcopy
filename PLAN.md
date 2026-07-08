# Plan

## Phase 1 — MVP on paper (console)
- [x] GitHubPoller against `GET /notifications` (PAT, `X-Poll-Interval`, 304 handling)
- [x] Event model, SQLite dedupe, minimal rules (print review_requested + mention)
- [x] ConsolePrinter output
- [x] Skip closed/merged PRs before printing

## Phase 2 — Real ink
- [x] EscposPrinter (USB + network via python-escpos)
- [x] Receipt template: header, wrapped title, repo/actor, QR of URL, cut
- [ ] Spooler retry/backoff when printer is off

## Phase 3 — Rules & comfort
- [x] Full YAML rules (repo globs, priorities, drop-by-default)
- [ ] Quiet hours with morning batch flush
- [ ] `/healthz` endpoint + structured logs

## Phase 4 — Cluster service
- [x] Dockerfile + compose.yaml (network-printer path first)
- [ ] USB variant: device passthrough + udev rule doc
- [ ] Deploy on mini PC, `restart: unless-stopped`, volume for SQLite

## Phase 5 — Instant mode (webhooks)
- [ ] WebhookSource (FastAPI, HMAC verify)
- [ ] Tailscale Funnel or Cloudflare Tunnel in front
- [ ] Poller stays on as catch-all backstop

## Phase 6 — More sources
- [ ] SlackSource (Socket Mode — no inbound port)
- [ ] ImapSource (IMAP IDLE)
- [ ] Per-source receipt styling

## Decisions log
- 2026-07-07: Python + python-escpos; poll-first, webhook-ready; Docker Compose; SQLite for all state.
- 2026-07-07: WT32-ETH01 WiFi bridge for Ethernet receipt printer (ESP-IDF sta2eth, L2 forwarding).
- 2026-07-08: Added PR state check — skip merged/closed before printing to avoid wasting paper.
