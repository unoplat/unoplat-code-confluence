########################################
# ---------- builder stage ------------
########################################
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Only tools required to COMPILE wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git build-essential libpq-dev ripgrep \
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
FROM python:3.13-slim

# Create non-root runtime user and standard data directory
ARG APP_USER=app
ARG APP_UID=10001
RUN useradd --uid ${APP_UID} --create-home --shell /usr/sbin/nologin ${APP_USER}

# Standard data dir used by the app (works across Debian/Alpine images)
ENV UNOPLAT_DATA_DIR=/opt/unoplat/repositories

# Prepare data dir and set permissions so the non-root user can write to it
RUN mkdir -p "$UNOPLAT_DATA_DIR" && chown -R ${APP_USER}:${APP_USER} /opt/unoplat

# Make it a named volume for convenient host mounting
VOLUME ["/opt/unoplat/repositories"]

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Keep git only if the running service needs it
RUN apt-get update && \
    apt-get install -y --no-install-recommends git ripgrep \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ⬇️  This single line brings in uv, ruff *and* all project deps
# Copy with proper ownership using --chown flag
COPY --from=builder --chown=${APP_USER}:${APP_USER} /usr/local /usr/local
COPY --from=builder --chown=${APP_USER}:${APP_USER} /app /app

# Drop privileges to non-root user
USER ${APP_USER}

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"]