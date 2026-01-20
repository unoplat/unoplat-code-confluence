"""
Environment detection utilities for determining runtime environment.

This module provides utilities to detect whether the application is running
in development mode (locally) or in a Docker container, and constructs
appropriate file paths based on the environment configuration.
"""

import os
from pathlib import Path
from typing import Union

from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)

# Singleton instance for environment settings
_settings_instance: EnvironmentSettings | None = None


def get_environment_settings() -> EnvironmentSettings:
    """
    Get the singleton instance of EnvironmentSettings.

    Returns:
        EnvironmentSettings: The singleton settings instance
    """
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = EnvironmentSettings()
    return _settings_instance


def is_running_in_docker() -> bool:
    """
    Detect if the application is running inside a Docker container.

    Uses environment variables to determine the runtime environment:
    - In Docker: DB_HOST points to service names like "postgresql"
    - In local dev: DB_HOST points to "localhost" or is unset

    Returns:
        bool: True if running in Docker, False if running locally
    """
    db_host = os.getenv("DB_HOST", "localhost")
    return db_host != "localhost"


def get_runtime_environment() -> str:
    """
    Get a string representation of the current runtime environment.

    Returns:
        str: "docker" if running in container, "development" if running locally
    """
    return "docker" if is_running_in_docker() else "development"


def construct_local_repository_path(folder_name: str) -> str:
    """
    Construct the appropriate local repository path using configuration settings.

    Args:
        folder_name: The name of the repository folder (e.g., "dspy")

    Returns:
        str: Full path to the repository based on REPOSITORIES_BASE_PATH setting

    Examples:
        >>> # With default development setting
        >>> construct_local_repository_path("dspy")
        "/Users/username/.unoplat/repositories/dspy"

        >>> # With custom setting REPOSITORIES_BASE_PATH=/custom/path
        >>> construct_local_repository_path("dspy")
        "/custom/path/dspy"
    """
    settings = get_environment_settings()
    base_path = os.path.expanduser(settings.repositories_base_path)
    return f"{base_path}/{folder_name}"


def ensure_local_repository_base_path() -> Path:
    """
    Ensure the base repositories directory exists using configuration settings.

    Creates the directory structure if it doesn't exist based on the
    REPOSITORIES_BASE_PATH setting.

    Returns:
        Path: The base repositories directory path

    Raises:
        OSError: If directory creation fails
    """
    settings = get_environment_settings()
    base_path = Path(os.path.expanduser(settings.repositories_base_path))

    # Create directory if it doesn't exist
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


def get_environment_info() -> dict[str, Union[str, bool]]:
    """
    Get comprehensive environment information for debugging.

    Returns:
        dict: Environment information including:
            - runtime_environment: "docker" or "development"
            - is_docker: boolean flag
            - db_host: database host setting
            - home_directory: current home directory
            - repositories_base_path: configured base repository path
            - base_repo_path: actual resolved base repository path
    """
    env = get_runtime_environment()
    is_docker = is_running_in_docker()
    settings = get_environment_settings()

    return {
        "runtime_environment": env,
        "is_docker": is_docker,
        "db_host": os.getenv("DB_HOST", "localhost"),
        "home_directory": str(Path.home()),
        "repositories_base_path": settings.repositories_base_path,
        "base_repo_path": str(ensure_local_repository_base_path()),
    }
