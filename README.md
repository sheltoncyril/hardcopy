# hardcopy

Prints your important GitHub notifications on a receipt printer. Review request comes in → receipt comes out.

- **Docs:** [ARCHITECTURE.md](ARCHITECTURE.md) · [PLAN.md](PLAN.md)
- **Stack:** Python 3.12, python-escpos, SQLite, Docker Compose

## Quick start (dev)

```bash
cp .env.example .env          # add your GitHub PAT (notifications scope)
cp config.example.yaml config.yaml
pip install -e .
python -m hardcopy            # console printer by default
```

## Run on the cluster

```bash
docker compose up -d
```

Network printer: set `printer.network.host` in config.yaml — done.
USB printer: uncomment the `devices:` block in compose.yaml and pin to the node with the printer.
