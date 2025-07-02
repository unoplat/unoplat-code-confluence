########################################
# ---------- builder stage ------------
########################################
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Only tools required to COMPILE wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install runtime tools now – they'll be copied later
RUN pip install --no-cache-dir uv ruff

WORKDIR /app
COPY pyproject.toml ./
COPY README.md ./
COPY src ./src
RUN uv sync --no-cache
COPY . /app

########################################
# ---------- runtime stage ------------
########################################
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Keep git only if the running service needs it
RUN apt-get update && \
    apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ⬇️  This single line brings in uv, ruff *and* all project deps
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"] 