"""Codebase detection orchestration and Protocol definition."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from fastapi import HTTPException
from unoplat_code_confluence_commons.configuration_models import CodebaseConfig

if TYPE_CHECKING:
    from loguru import Logger


@runtime_checkable
class CodebaseDetector(Protocol):
    """Structural interface satisfied by every language-specific detector.

    Both ``PythonRipgrepDetector`` and ``TypeScriptRipgrepDetector`` conform
    to this protocol without explicitly inheriting it.
    """

    async def initialize_rules(self) -> None: ...
    async def detect_codebases(
        self, git_url: str, github_token: str
    ) -> list[CodebaseConfig]: ...


async def detect_codebases_multi_language(
    git_url: str,
    github_token: str,
    detectors: dict[str, CodebaseDetector],
    request_logger: "Logger",
) -> list[CodebaseConfig]:
    """
    Detect codebases using all configured language detectors.

    This function runs detection across all supported programming languages
    (Python, TypeScript, etc.) and aggregates the results. It handles errors
    gracefully by logging failures per language and continuing with other
    detectors.

    Args:
        git_url: GitHub repository URL or local filesystem path
        github_token: GitHub personal access token for authentication
        detectors: Dictionary mapping language names to detector instances
        request_logger: Logger instance for tracking detection progress

    Returns:
        List of detected CodebaseConfig across all languages

    Raises:
        HTTPException: If all detectors fail to find any codebases
    """
    aggregated_codebases: list[CodebaseConfig] = []
    errors: dict[str, str] = {}

    for language, detector in detectors.items():
        try:
            request_logger.info(
                "Running {} codebase detection for {}", language, git_url
            )
            codebases = await detector.detect_codebases(git_url, github_token)
            aggregated_codebases.extend(codebases)
            request_logger.info(
                "{} detection completed - found {} codebases",
                language.capitalize(),
                len(codebases),
            )
        except Exception as exc:
            errors[language] = str(exc)
            request_logger.error(
                "Codebase detection failed | language={} | repo={} | error={}",
                language,
                git_url,
                exc,
            )

    # If all detectors failed, raise error
    if not aggregated_codebases and errors:
        error_details = "; ".join(f"{lang}: {err}" for lang, err in errors.items())
        raise HTTPException(
            status_code=500, detail=f"All codebase detectors failed: {error_details}"
        )

    return aggregated_codebases
