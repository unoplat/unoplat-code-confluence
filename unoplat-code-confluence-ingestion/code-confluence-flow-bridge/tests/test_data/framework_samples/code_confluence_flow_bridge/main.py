"""Minimal FastAPI app sample for framework detection tests."""

from typing import Dict

from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/echo")
async def echo_payload(payload: Dict[str, str]) -> Dict[str, str]:
    """Echo back a payload for test detection."""
    return payload
