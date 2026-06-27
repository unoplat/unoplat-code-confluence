from __future__ import annotations


class CliError(RuntimeError):
    """Base exception for CLI application errors."""


class ConfigurationError(CliError):
    """Raised when CLI configuration is invalid."""


class RepositoryUrlError(CliError):
    """Raised when a repository git URL cannot be parsed or normalized."""


class NetworkError(CliError):
    """Raised when an HTTP dependency cannot be reached or returns an error."""


class ServiceReadinessError(CliError):
    """Raised when a local service does not become ready before timeout."""


class ReleaseError(CliError):
    """Raised when release metadata or release assets are invalid/unavailable."""


class DockerRuntimeError(CliError):
    """Raised when Docker or Docker Compose operations fail."""


class SetupRequiredError(CliError):
    """Raised when setup/credentials are required before continuing."""
