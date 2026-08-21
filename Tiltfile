# Tiltfile — local hot-reload dev environment.
#
# Usage:
#   tilt up              # start everything, open UI at http://localhost:10350
#   tilt down            # stop and remove containers + volumes
#
# What it does:
# 1. Loads services from tilt-docker-compose.yml (infra + three dev services).
# 2. Wraps the three dev services' image builds with live_update so that
#    editing source on the host syncs into the running container in ~1s
#    instead of triggering a full rebuild. `fastapi dev` and Vite handle
#    in-process reload once files land in the container.
# 3. Uses fall_back_on(...) for dependency manifests so dependency changes
#    rebuild the dev image instead of trying to mutate dependencies in-place.
# 4. Groups services in the Tilt UI by role (infra vs app).
#
# Docs: https://docs.tilt.dev/tiltfile_concepts.html

docker_compose("tilt-docker-compose.yml")

# ---------------------------------------------------------------------------
# code-confluence-flow-bridge (FastAPI, Python)
# ---------------------------------------------------------------------------
docker_build(
    "unoplat/code-confluence-flow-bridge-dev",
    context="./unoplat-code-confluence-ingestion/code-confluence-flow-bridge",
    dockerfile="./unoplat-code-confluence-ingestion/code-confluence-flow-bridge/Dockerfile.dev",
    only=[
        "./src",
        "./framework-definitions",
        "./pyproject.toml",
        "./uv.lock",
        "./README.md",
    ],
    live_update=[
        fall_back_on([
            "./unoplat-code-confluence-ingestion/code-confluence-flow-bridge/pyproject.toml",
            "./unoplat-code-confluence-ingestion/code-confluence-flow-bridge/uv.lock",
        ]),
        sync("./unoplat-code-confluence-ingestion/code-confluence-flow-bridge/src", "/app/src"),
        sync(
            "./unoplat-code-confluence-ingestion/code-confluence-flow-bridge/framework-definitions",
            "/app/framework-definitions",
        ),
    ],
)

# ---------------------------------------------------------------------------
# unoplat-code-confluence-query-engine (FastAPI, Python)
# ---------------------------------------------------------------------------
docker_build(
    "unoplat/code-confluence-query-engine-dev",
    context="./unoplat-code-confluence-query-engine",
    dockerfile="./unoplat-code-confluence-query-engine/Dockerfile.dev",
    only=[
        "./src",
        "./mcp-servers.json",
        "./pyproject.toml",
        "./uv.lock",
        "./README.md",
    ],
    live_update=[
        fall_back_on([
            "./unoplat-code-confluence-query-engine/pyproject.toml",
            "./unoplat-code-confluence-query-engine/uv.lock",
        ]),
        sync("./unoplat-code-confluence-query-engine/src", "/app/src"),
    ],
)

# ---------------------------------------------------------------------------
# unoplat-code-confluence-frontend (Vite + React, Bun)
# ---------------------------------------------------------------------------
docker_build(
    "unoplat/code-confluence-frontend-dev",
    context="./unoplat-code-confluence-frontend",
    dockerfile="./unoplat-code-confluence-frontend/Dockerfile.dev",
    only=[
        "./src",
        "./public",
        "./index.html",
        "./vite.config.ts",
        "./tsconfig.json",
        "./tsconfig.app.json",
        "./tsconfig.node.json",
        "./tsr.config.json",
        "./components.json",
        "./eslint.config.js",
        "./eslint-plugin-use-no-memo.d.ts",
        "./package.json",
        "./bun.lock",
        "./.env.dev",
        "./.env.prod",
    ],
    live_update=[
        fall_back_on([
            "./unoplat-code-confluence-frontend/package.json",
            "./unoplat-code-confluence-frontend/bun.lock",
        ]),
        sync("./unoplat-code-confluence-frontend/src", "/app/src"),
        sync("./unoplat-code-confluence-frontend/public", "/app/public"),
        sync("./unoplat-code-confluence-frontend/index.html", "/app/index.html"),
        sync("./unoplat-code-confluence-frontend/vite.config.ts", "/app/vite.config.ts"),
    ],
)

# ---------------------------------------------------------------------------
# Resource grouping in the Tilt UI (http://localhost:10350)
# ---------------------------------------------------------------------------
dc_resource("postgresql", labels=["infra"])
dc_resource("electric", labels=["infra"])
dc_resource("temporal", labels=["infra"])
dc_resource("temporal-admin-tools", labels=["infra"])
dc_resource("temporal-ui", labels=["infra"])

dc_resource("code-confluence-flow-bridge", labels=["app"])
dc_resource("unoplat-code-confluence-query-engine", labels=["app"])
dc_resource("unoplat-code-confluence-frontend", labels=["app"])
