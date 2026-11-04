# syntax=docker/dockerfile:1.7
# Build from the repository root so uv can resolve the sibling commons package:
#   docker build -f unoplat-code-confluence-ingestion/code-confluence-flow-bridge/Dockerfile .

########################################
# ------------ builder stage ----------
########################################
FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.10.9 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Only tools required to compile native wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Keep the repository layout for uv's relative commons path. Non-editable installs
# leave no reference to it, so the runtime image ships only /app.
WORKDIR /workspace/unoplat-code-confluence-ingestion/code-confluence-flow-bridge

# Install dependency layer first so source changes do not invalidate it.
COPY unoplat-code-confluence-ingestion/code-confluence-flow-bridge/pyproject.toml unoplat-code-confluence-ingestion/code-confluence-flow-bridge/uv.lock unoplat-code-confluence-ingestion/code-confluence-flow-bridge/README.md ./
COPY unoplat-code-confluence-commons/pyproject.toml unoplat-code-confluence-commons/README.md /workspace/unoplat-code-confluence-commons/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-install-package unoplat-code-confluence-commons --no-editable --no-dev

# Copy source after dependency install and sync project into the venv.
COPY unoplat-code-confluence-commons/src /workspace/unoplat-code-confluence-commons/src
COPY unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev

COPY unoplat-code-confluence-ingestion/code-confluence-flow-bridge/ /app/

########################################
# ------------ runtime stage ----------
########################################
FROM python:3.13-slim

# Create non-root runtime user and standard data directory
ARG APP_USER=app
ARG APP_UID=10001
RUN useradd --uid ${APP_UID} --create-home --shell /usr/sbin/nologin ${APP_USER}

ENV UNOPLAT_DATA_DIR=/opt/unoplat/repositories \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

# Prepare data dir and set permissions so the non-root user can write to it
RUN mkdir -p "$UNOPLAT_DATA_DIR" && chown -R ${APP_USER}:${APP_USER} /opt/unoplat

# Make it a named volume for convenient host mounting
VOLUME ["/opt/unoplat/repositories"]

# Keep git only if the running service needs it
RUN apt-get update && \
    apt-get install -y --no-install-recommends git ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the image-built virtual environment and application code.
COPY --from=builder --chown=${APP_USER}:${APP_USER} /app /app

# Drop privileges to non-root user
USER ${APP_USER}

EXPOSE 8000
CMD ["uvicorn", "code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"]
