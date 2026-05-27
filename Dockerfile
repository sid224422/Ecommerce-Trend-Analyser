# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools needed by some packages (reportlab, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: slim runtime image ───────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy project source
COPY . .

# reports/ is the only directory written at runtime — make it world-writable
# (volume mount will override this when using docker compose)
RUN mkdir -p reports && chmod 777 reports

# Streamlit runs on 8501 by default
EXPOSE 8501

# Health check — Streamlit exposes /_stcore/health
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" \
    || exit 1

# Run the Streamlit app
CMD ["python", "-m", "streamlit", "run", "ui/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
