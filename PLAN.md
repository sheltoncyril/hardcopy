# Plan

## Phase 1 — MVP on paper (console)
- [ ] GitHubPoller against `GET /notifications` (PAT, `X-Poll-Interval`, 304 handling)
- [ ] Event model, SQLite dedupe, minimal rules (print review_requested + mention)
- [ ] ConsolePrinter output
- **Done when:** a review request prints to the terminal within ~60 s.

## Phase 2 — Real ink
- [ ] EscposPrinter (USB + network via python-escpos)
- [ ] Receipt template: header, wrapped title, repo/actor, QR of URL, cut
- [ ] Spooler retry/backoff when printer is off
- **Done when:** unplugging the printer for 10 min loses nothing.

## Phase 3 — Rules & comfort
- [ ] Full YAML rules (repo globs, priorities, drop-by-default)
- [ ] Quiet hours with morning batch flush
- [ ] `/healthz` endpoint + structured logs

## Phase 4 — Cluster service
- [ ] Dockerfile + compose.yaml (network-printer path first)
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
