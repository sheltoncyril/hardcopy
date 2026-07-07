FROM python:3.12-slim

# libusb for USB ESC/POS printers (harmless if using network printer)
RUN apt-get update && apt-get install -y --no-install-recommends libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock* ./
COPY src ./src
RUN uv pip install --system --no-cache .

VOLUME /app/data
CMD ["python", "-m", "hardcopy"]
