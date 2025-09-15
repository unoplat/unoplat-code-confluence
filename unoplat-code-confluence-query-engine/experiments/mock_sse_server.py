"""Mock SSE server that replays events from docs/sse-agent-results.txt.

This standalone FastAPI app exposes an endpoint compatible with the real
`/v1/codebase-agent-rules` route and streams Server-Sent Events in the exact
order captured in the reference log file. Useful for UI/dev testing without
running the full agent pipeline or external services.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from sse_starlette.sse import EventSourceResponse

APP_TITLE: str = "Mock Codebase Agent Rules SSE Server"
DEFAULT_DELAY_SECONDS: float = 0.05

# Resolve repository root and reference SSE log file
REPO_ROOT: Path = Path(__file__).resolve().parents[1]
SSE_LOG_PATH: Path = REPO_ROOT / "docs" / "sse-agent-results.txt"


# In-memory cache of parsed SSE events
LOADED_EVENTS: List[Dict[str, str]] = []


def parse_sse_log_file(file_path: Path) -> List[Dict[str, str]]:
    """Parse a newline-delimited SSE capture file into event dicts.

    The expected format mirrors what `curl -N` would show:
      id: 1\n
      event: repo:agent:event_type\n
      data: {"json": "object"}\n
      \n
    - Blank line separates events
    - Lines starting with "::" are treated as comments/keepalive pings and skipped

    Returns a list of dicts each containing keys: "id", "event", "data".
    Data is preserved as a raw JSON string to match the real endpoint behavior.
    """
    events: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    try:
        raw_text: str = file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        logger.error("SSE log file not found at {}", file_path)
        raise exc

    for raw_line in raw_text.splitlines():
        line: str = raw_line.strip()

        if not line:
            if "event" in current and "data" in current:
                if "id" not in current:
                    current["id"] = str(len(events))
                events.append(current)
            current = {}
            continue

        if line.startswith("::"):
            # Skip comment/ping lines
            continue

        if line.startswith("id:"):
            current["id"] = line.partition("id:")[2].strip()
            continue

        if line.startswith("event:"):
            current["event"] = line.partition("event:")[2].strip()
            continue

        if line.startswith("data:"):
            # Preserve raw JSON string as-is
            current["data"] = line.partition("data:")[2].strip()
            continue

    # Finalize trailing event if file doesn't end with a blank line
    if current and "event" in current and "data" in current:
        if "id" not in current:
            current["id"] = str(len(events))
        events.append(current)

    return events


async def stream_mock_events(
    request: Request, *, delay_seconds: float
) -> AsyncGenerator[Dict[str, str], None]:
    """Yield parsed SSE events to the client with an optional delay between them.

    The yielded dicts follow sse-starlette's expected structure: keys "id",
    "event", and "data". `data` remains a JSON string, matching the real
    endpoint which serializes payloads prior to emission.
    """
    for event in LOADED_EVENTS:
        if await request.is_disconnected():
            logger.info("Mock SSE client disconnected early")
            break

        yield event

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)


app: FastAPI = FastAPI(title=APP_TITLE)

# Add CORS middleware to allow cross-origin requests (matches main.py configuration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Important for SSE headers
)


@app.on_event("startup")
async def on_startup() -> None:
    """Load and cache SSE events from the reference file on startup."""
    global LOADED_EVENTS
    LOADED_EVENTS = parse_sse_log_file(SSE_LOG_PATH)
    logger.info("Loaded {} mock SSE events from {}", len(LOADED_EVENTS), SSE_LOG_PATH)


@app.get("/v1/codebase-agent-rules")
async def get_mock_codebase_agent_rules(
    request: Request,
    owner_name: str = Query(..., description="Repository owner name"),
    repo_name: str = Query(..., description="Repository name"),
    delay_seconds: Optional[float] = Query(
        default=DEFAULT_DELAY_SECONDS,
        ge=0.0,
        le=2.0,
        description="Artificial delay between events to simulate streaming",
    ),
) -> EventSourceResponse:
    """Stream mock SSE events in the same order as the captured session.

    Query params are accepted for API compatibility, but do not affect the
    mocked stream content.
    """
    headers: Dict[str, str] = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return EventSourceResponse(
        stream_mock_events(request, delay_seconds=delay_seconds or 0.0),
        ping=10,
        headers=headers,
    )


