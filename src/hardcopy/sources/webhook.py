"""Webhook receiver — Phase 5. Same Source interface, push instead of poll.

Sketch: FastAPI app with POST /webhook/github, HMAC-SHA256 signature check
(X-Hub-Signature-256), payload -> Event, pushed onto an asyncio.Queue that
`events()` drains. Expose via Tailscale Funnel or Cloudflare Tunnel.
Requires the [webhook] extra: pip install -e ".[webhook]"
"""
