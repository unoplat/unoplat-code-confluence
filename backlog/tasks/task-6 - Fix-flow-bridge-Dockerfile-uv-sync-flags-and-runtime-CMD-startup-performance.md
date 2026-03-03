---
id: TASK-6
title: 'Fix flow-bridge Dockerfile: uv sync flags and runtime CMD startup performance'
status: To Do
assignee: []
created_date: '2026-03-03 06:07'
labels: []
dependencies: []
references:
  - unoplat-code-confluence-ingestion/code-confluence-flow-bridge/Dockerfile
  - unoplat-code-confluence-ingestion/code-confluence-flow-bridge/pyproject.toml
documentation:
  - 'https://docs.astral.sh/uv/guides/integration/fastapi/'
  - 'https://docs.astral.sh/uv/guides/integration/docker/'
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The `code-confluence-flow-bridge` Docker container re-downloads packages from GitHub on every startup because `CMD ["uv", "run", ...]` triggers uv's environment sync check. Since `pyproject.toml` declares `unoplat-code-confluence-commons` as a git source dependency, uv performs a network fetch to GitHub on every container start.

A secondary issue is that `uv sync --no-cache` disables uv's HTTP wheel cache (wastes bandwidth on rebuilds) and lacks `--locked` which is the official reproducibility flag.

Official FastAPI + uv documentation explicitly recommends against `uv run` in production and prescribes `--locked --no-dev` with BuildKit cache mounts for the build stage.

**Two targeted changes to `Dockerfile`:**

1. Builder stage line 22 — replace `RUN uv sync --no-cache` with:
   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/uv \
       UV_LINK_MODE=copy uv sync --locked --no-dev
   ```
   - `--locked`: fail if uv.lock is out of sync with pyproject.toml (reproducibility)
   - `--no-dev`: exclude test/dev groups (mypy, basedpyright, pytest, testcontainers) from production image
   - Cache mount + `UV_LINK_MODE=copy`: reuse uv HTTP/wheel cache across builds

2. Runtime CMD line 63 — add `--frozen`:
   ```dockerfile
   CMD ["uv", "run", "--frozen", "uvicorn", "src.code_confluence_flow_bridge.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
   - `--frozen`: use the already-installed environment as-is; no sync or network access on startup
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Container starts without downloading any packages or making network requests to GitHub
- [ ] #2 Running `docker build` a second time with no source changes reuses the uv cache and is significantly faster than the first build
- [ ] #3 Dev and test packages (mypy, basedpyright, pytest, testcontainers) are NOT present in the final image
- [ ] #4 `uv sync` in the builder stage fails (non-zero exit) if uv.lock is not in sync with pyproject.toml — verifiable by temporarily modifying pyproject.toml without updating the lockfile
- [ ] #5 The FastAPI app starts and serves requests correctly after the changes
<!-- AC:END -->
