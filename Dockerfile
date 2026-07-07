FROM python:3.12-slim

# libusb for USB ESC/POS printers (harmless if using network printer)
RUN apt-get update && apt-get install -y --no-install-recommends libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

VOLUME /app/data
CMD ["python", "-m", "hardcopy"]
