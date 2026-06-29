# ── TrendScanner AI — Docker image (Python 3.11 + Streamlit) ─────────────────
# Build:  docker compose build
# Run:    docker compose up   (or start from Docker Desktop)

# ── Stage 1: dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=120 --retries 5 \
    --prefix=/install -r requirements.txt


# ── Stage 2: slim runtime image ───────────────────────────────────────────────
FROM python:3.11-slim

LABEL org.opencontainers.image.title="TrendScanner AI"
LABEL org.opencontainers.image.description="Market analytics UI — agents, Groq summary, export, WhatsApp share"
LABEL org.opencontainers.image.source="https://github.com/local/trendscanner-ai"

WORKDIR /app

COPY --from=builder /install /usr/local

# Application source (agents, core, llm, ui, scripts, streamlit config)
COPY agents/ agents/
COPY core/ core/
COPY llm/ llm/
COPY ui/ ui/
COPY scripts/ scripts/
COPY .streamlit/ .streamlit/
COPY run_app.py .
COPY requirements.txt .
COPY .env.example .

# Demo CSV baked in for quick Docker trials (override by uploading your own in the UI)
COPY test_trendscanner_fashion_inr.csv samples/demo_fashion_inr.csv

RUN mkdir -p reports samples && chmod 777 reports

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=25s --retries=3 \
    CMD python -c "import urllib.request; r=urllib.request.Request('http://127.0.0.1:8501/_stcore/health', headers={'User-Agent': 'TrendScannerAI/1.0'}); urllib.request.urlopen(r, timeout=5)" \
    || exit 1

CMD ["python", "-m", "streamlit", "run", "ui/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
