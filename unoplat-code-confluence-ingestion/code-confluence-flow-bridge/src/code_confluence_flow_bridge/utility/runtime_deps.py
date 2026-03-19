"""FastAPI dependency functions for runtime resources stored on ``app.state``."""

from fastapi import Request
from temporalio.client import Client

from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.utility.detection import CodebaseDetector


def get_env_settings(request: Request) -> EnvironmentSettings:
    """Retrieve ``EnvironmentSettings`` from ``app.state``."""
    env_settings: EnvironmentSettings = request.app.state.code_confluence_env
    return env_settings


def get_temporal_client_dep(request: Request) -> Client:
    """Retrieve the Temporal ``Client`` from ``app.state``."""
    temporal_client: Client = request.app.state.temporal_client
    return temporal_client


def get_codebase_detectors(request: Request) -> dict[str, CodebaseDetector]:
    """Retrieve the codebase detector registry from ``app.state``."""
    detectors: dict[str, CodebaseDetector] = request.app.state.codebase_detectors
    return detectors
