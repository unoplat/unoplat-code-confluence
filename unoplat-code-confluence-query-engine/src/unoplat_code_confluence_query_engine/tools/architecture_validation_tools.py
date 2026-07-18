"""Agent-invoked validation for the repository Architecture artifact."""

from __future__ import annotations

import hashlib
from pathlib import Path
import re
import shutil
import subprocess
from xml.etree import ElementTree

from markdown_it import MarkdownIt
from markdown_it.token import Token
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
    ArchitectureAgentDependencies,
)

ARCHITECTURE_ARTIFACT = "architecture.md"
DEFAULT_MMDC_EXECUTABLE = "mmdc"
DEFAULT_PUPPETEER_CONFIG_PATH = Path("/app/puppeteer-config.json")
MAX_ARCHITECTURE_MARKDOWN_BYTES = 256 * 1024
MMDC_TIMEOUT_SECONDS = 30
MAX_RENDER_DIAGNOSTIC_CHARACTERS = 600
BUILTIN_ARCHITECTURE_ICONS = frozenset(
    {"cloud", "database", "disk", "internet", "server"}
)

_ARCHITECTURE_DIRECTIVE = "architecture-beta"
_ARCHITECTURE_NODE_ICON_PATTERN = re.compile(
    r"^\s*(?:group|service)\s+[^\s(]+\s*\(\s*([^)]*?)\s*\)", re.MULTILINE
)
_MERMAID_SYNTAX_ERROR_MARKERS = (
    "syntax error in text",
    "mermaid syntax error",
)


def validate_architecture(ctx: RunContext[ArchitectureAgentDependencies]) -> str:
    """Validate the current repository-root architecture artifact with Mermaid.

    Returns:
        A success confirmation containing the SHA-256 digest of the exact
        ``architecture.md`` content that passed structural and render checks.

    Raises:
        ModelRetry: If the artifact contract or rendered SVG validation fails.
    """
    repository_root = Path(ctx.deps.repository_root)
    artifact_path = repository_root / ARCHITECTURE_ARTIFACT

    markdown_bytes = _read_bounded_artifact(
        artifact_path,
        max_markdown_bytes=MAX_ARCHITECTURE_MARKDOWN_BYTES,
    )
    try:
        markdown_text = markdown_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ModelRetry("architecture.md must be valid UTF-8 Markdown.") from exc

    diagram_text = _extract_architecture_diagram(markdown_text)
    _validate_builtin_icons(diagram_text)
    _render_and_validate_svg(
        diagram_text,
        artifact_directory=artifact_path.parent,
        mmdc_executable=DEFAULT_MMDC_EXECUTABLE,
        puppeteer_config_path=DEFAULT_PUPPETEER_CONFIG_PATH,
        timeout_seconds=MMDC_TIMEOUT_SECONDS,
    )

    content_digest = hashlib.sha256(markdown_bytes).hexdigest()
    return (
        "architecture.md validation passed for the current on-disk content "
        f"(sha256={content_digest})."
    )


def _read_bounded_artifact(
    artifact_path: Path,
    *,
    max_markdown_bytes: int,
) -> bytes:
    if max_markdown_bytes <= 0:
        raise ValueError("max_markdown_bytes must be positive")

    try:
        if not artifact_path.is_file():
            raise ModelRetry(
                "architecture.md was not found as a regular file at the repository "
                "root. Create or update it before validation."
            )
        with artifact_path.open("rb") as artifact_file:
            markdown_bytes = artifact_file.read(max_markdown_bytes + 1)
    except ModelRetry:
        raise
    except OSError as exc:
        raise ModelRetry(
            f"architecture.md could not be read: {exc.strerror or exc}."
        ) from exc

    if len(markdown_bytes) > max_markdown_bytes:
        raise ModelRetry(
            "architecture.md is too large "
            f"(maximum {max_markdown_bytes} UTF-8 bytes)."
        )
    return markdown_bytes


def _extract_architecture_diagram(markdown_text: str) -> str:
    mermaid_fences = [
        token
        for token in MarkdownIt("commonmark").parse(markdown_text)
        if _is_mermaid_fence(token)
    ]
    if len(mermaid_fences) != 1:
        raise ModelRetry(
            "architecture.md must contain exactly one fenced ```mermaid diagram."
        )

    diagram_text = mermaid_fences[0].content
    first_content_line = next(
        (line.strip() for line in diagram_text.splitlines() if line.strip()), ""
    )
    if first_content_line != _ARCHITECTURE_DIRECTIVE:
        raise ModelRetry(
            "The Mermaid fence must begin with exactly 'architecture-beta'; "
            "flowcharts and other diagram types are not allowed."
        )
    return diagram_text


def _is_mermaid_fence(token: Token) -> bool:
    return token.type == "fence" and token.info.strip() == "mermaid"


def _validate_builtin_icons(diagram_text: str) -> None:
    unsupported_icons = sorted(
        {
            icon.strip()
            for icon in _ARCHITECTURE_NODE_ICON_PATTERN.findall(diagram_text)
            if icon.strip() not in BUILTIN_ARCHITECTURE_ICONS
        }
    )
    if unsupported_icons:
        raise ModelRetry(
            "Unsupported architecture icon(s): "
            + ", ".join(unsupported_icons)
            + ". Only built-in cloud, database, disk, internet, and server icons "
            "are allowed."
        )


def _render_and_validate_svg(
    diagram_text: str,
    *,
    artifact_directory: Path,
    mmdc_executable: str,
    puppeteer_config_path: Path,
    timeout_seconds: int,
) -> None:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if not puppeteer_config_path.is_file():
        raise ModelRetry(
            "Mermaid renderer configuration is unavailable at "
            f"{puppeteer_config_path}."
        )

    resolved_mmdc = shutil.which(mmdc_executable)
    if resolved_mmdc is None:
        raise ModelRetry(
            f"Mermaid CLI '{mmdc_executable}' is unavailable. Install the packaged "
            "mmdc executable."
        )

    command = [
        resolved_mmdc,
        "--input",
        "-",
        "--output",
        "-",
        "--outputFormat",
        "svg",
        "--puppeteerConfigFile",
        str(puppeteer_config_path),
        "--quiet",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=artifact_directory,
            check=False,
            input=diagram_text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        diagnostic = _concise_diagnostic(exc.stderr)
        message = f"Mermaid render timed out after {timeout_seconds} seconds."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message) from exc
    except OSError as exc:
        raise ModelRetry(
            f"Mermaid renderer could not start: {exc.strerror or exc}."
        ) from exc

    if result.returncode != 0:
        diagnostic = _concise_diagnostic(result.stderr or result.stdout)
        message = f"Mermaid render failed (exit {result.returncode})."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message)

    _validate_svg_output(result.stdout, stderr=result.stderr)


def _validate_svg_output(svg_bytes: bytes, *, stderr: bytes = b"") -> None:
    if not svg_bytes.strip():
        diagnostic = _concise_diagnostic(stderr)
        message = "Mermaid exited successfully without returning SVG output."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message)

    try:
        svg_root = ElementTree.fromstring(svg_bytes)
    except ElementTree.ParseError as exc:
        diagnostic = _concise_diagnostic(svg_bytes)
        message = "Mermaid returned malformed XML instead of a valid SVG."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message) from exc

    if _local_name(svg_root.tag).lower() != "svg":
        raise ModelRetry(
            "Mermaid returned XML whose root element is not <svg> "
            f"(found <{_local_name(svg_root.tag)}>)."
        )

    error_role_found = any(
        element.attrib.get("aria-roledescription", "").strip().lower() == "error"
        for element in svg_root.iter()
    )
    rendered_text = " ".join("".join(svg_root.itertext()).split())
    syntax_error_found = any(
        marker in rendered_text.lower() for marker in _MERMAID_SYNTAX_ERROR_MARKERS
    )
    if error_role_found or syntax_error_found:
        diagnostic = _concise_diagnostic(rendered_text or svg_bytes)
        message = "Mermaid returned an SVG error render despite exit code 0."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _concise_diagnostic(diagnostic: str | bytes | None) -> str:
    if isinstance(diagnostic, bytes):
        diagnostic = diagnostic.decode("utf-8", errors="replace")
    normalized = " ".join((diagnostic or "").split())
    if len(normalized) > MAX_RENDER_DIAGNOSTIC_CHARACTERS:
        return normalized[:MAX_RENDER_DIAGNOSTIC_CHARACTERS].rstrip() + "…"
    return normalized
