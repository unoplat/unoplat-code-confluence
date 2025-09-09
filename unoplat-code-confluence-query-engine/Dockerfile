########################################
# ---------- bun stage ---------------
########################################
FROM oven/bun:1 AS bun-stage

# Set working directory for any potential Bun operations
WORKDIR /bun-workspace

# Copy any bun-related files if they exist (package.json, bun.lockb)
# This stage can be extended later for Bun dependency management
COPY package*.json bun.lockb* ./
# Ensure node_modules directory exists even if no install happens
RUN mkdir -p /bun-workspace/node_modules
# Install dependencies if package.json exists
RUN if [ -f package.json ]; then bun install --frozen-lockfile; else echo "No package.json found, skipping bun install"; fi

########################################
# ---------- builder stage ------------
########################################
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git build-essential curl unzip \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY README.md ./
COPY src ./src
RUN uv sync --no-cache --frozen
COPY . /app

########################################
# ---------- runtime stage ------------
########################################
FROM python:3.13-slim

# Create non-root runtime user
ARG APP_USER=app
ARG APP_UID=10001
RUN useradd --uid ${APP_UID} --create-home --shell /usr/sbin/nologin ${APP_USER}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install minimal runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl unzip git ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Bun binary from official image to system location
COPY --from=bun-stage /usr/local/bin/bun /usr/local/bin/bun
COPY --from=bun-stage /usr/local/bin/bunx /usr/local/bin/bunx

# Copy Python application and dependencies
COPY --from=builder --chown=${APP_USER}:${APP_USER} /usr/local /usr/local
COPY --from=builder --chown=${APP_USER}:${APP_USER} /app /app

# Copy Bun dependencies; directory always exists from bun-stage
COPY --from=bun-stage --chown=${APP_USER}:${APP_USER} /bun-workspace/node_modules ./node_modules

# Ensure Bun is accessible to non-root user
RUN chmod +x /usr/local/bin/bun /usr/local/bin/bunx

# Drop privileges to non-root user
USER ${APP_USER}

# Set environment variables
ENV PYTHONPATH=/app/src
ENV UV_SYSTEM_PYTHON=1

EXPOSE 8000
CMD ["uv", "run", "--frozen", "fastapi", "run", "src/unoplat_code_confluence_query_engine/main.py", "--host", "0.0.0.0", "--port", "8000"]
