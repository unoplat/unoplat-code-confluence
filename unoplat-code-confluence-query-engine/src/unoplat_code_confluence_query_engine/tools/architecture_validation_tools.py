"""Agent-invoked validation for repository-root Architecture D2/SVG artifacts."""

from __future__ import annotations

import os
from functools import lru_cache
import hashlib
from importlib.resources import files
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from xml.etree import ElementTree

from pydantic_ai import BinaryContent, ModelRetry, RunContext, ToolReturn

from unoplat_code_confluence_query_engine.models.runtime.architecture_agent_dependencies import (
    ArchitectureAgentDependencies,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    ARCHITECTURE_RENDER_ARTIFACT,
    ARCHITECTURE_SOURCE_ARTIFACT,
)

REQUIRED_D2_VERSION = "v0.7.1"
DEFAULT_D2_EXECUTABLE = "d2"
D2_LAYOUT_ENGINE = "elk"
D2_PAD_PIXELS = 40
D2_ELK_NODE_NODE_BETWEEN_LAYERS = 70
D2_ELK_EDGE_NODE_BETWEEN_LAYERS = 45
D2_ELK_PADDING = "[top=40,left=40,bottom=40,right=40]"

MAX_ARCHITECTURE_D2_BYTES = 256 * 1024
MAX_ARCHITECTURE_SVG_BYTES = 5 * 1024 * 1024
MAX_ARCHITECTURE_PNG_BYTES = 2 * 1024 * 1024
D2_TIMEOUT_SECONDS = 120
D2_VERSION_TIMEOUT_SECONDS = 10
CHROMIUM_TIMEOUT_SECONDS = 30
MAX_RENDER_DIAGNOSTIC_CHARACTERS = 600
PREVIEW_MIN_WIDTH = 640
PREVIEW_MIN_HEIGHT = 480
PREVIEW_MAX_WIDTH = 4096
PREVIEW_MAX_HEIGHT = 4096
PREVIEW_DEFAULT_WIDTH = 1600
PREVIEW_DEFAULT_HEIGHT = 1200
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
HOSTED_ICON_URL_MARKER = "https://icons.d2lang.com/"

_ICON_CATALOG_CATEGORIES: tuple[str, ...] = (
    "development",
    "technology",
    "infrastructure",
)
# D2 properties may be assigned through a dotted object path (for example,
# ``api.icon: ...``) instead of only within an object block as bare ``icon``.
# Match every path whose final property is ``icon`` so the source allowlist
# cannot be bypassed by choosing the dotted form.
_D2_PATH_SEGMENT = r'(?:"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[^\s.:;{}#]+)'
_ICON_PROPERTY_PATTERN = re.compile(
    rf"(?m)^[ \t]*(?:(?:{_D2_PATH_SEGMENT})[ \t]*\.[ \t]*)*"
    r"icon[ \t]*:[ \t]*(?P<value>.+?)[ \t]*(?:#.*)?$"
)
_SVG_EMBEDDED_IMAGE_PREFIX = "data:image/"
_SVG_IMAGE_ELEMENTS = frozenset(("image", "feimage"))
_CHROMIUM_CANDIDATES: tuple[str, ...] = (
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def validate_architecture(
    ctx: RunContext[ArchitectureAgentDependencies],
) -> ToolReturn[list[str | BinaryContent]]:
    """Validate repository-root architecture.d2 and publish architecture.svg.

    Reads the current on-disk D2 source, enforces the hosted-icon allowlist and
    pinned D2 v0.7.1 + ELK contract, validates a temporary PNG preview of the
    exact SVG, then atomically writes the canonical SVG render only after the
    full preview-backed pair is valid. Returns source/render digests plus that
    temporary PNG preview.

    Returns:
        A ``ToolReturn`` whose return value is a list containing the SHA-256
        digest confirmation for the validated ``architecture.d2`` and
        ``architecture.svg`` pair, plus the temporary diagram PNG as native
        tool-result multimodal content.

    Raises:
        ModelRetry: If the D2/SVG contract, icon policy, renderer, or preview
            validation fails.
    """
    repository_root = Path(ctx.deps.repository_root)
    source_path = repository_root / ARCHITECTURE_SOURCE_ARTIFACT
    render_path = repository_root / ARCHITECTURE_RENDER_ARTIFACT

    d2_bytes = _read_bounded_text_file(
        source_path,
        max_bytes=MAX_ARCHITECTURE_D2_BYTES,
        missing_message=(
            f"{ARCHITECTURE_SOURCE_ARTIFACT} was not found as a regular file at "
            "the repository root. Create or update it before validation."
        ),
        unreadable_label=ARCHITECTURE_SOURCE_ARTIFACT,
        oversized_label=ARCHITECTURE_SOURCE_ARTIFACT,
    )
    try:
        d2_text = d2_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ModelRetry(
            f"{ARCHITECTURE_SOURCE_ARTIFACT} must be valid UTF-8 D2 source."
        ) from exc
    if not d2_text.strip():
        raise ModelRetry(f"{ARCHITECTURE_SOURCE_ARTIFACT} is empty.")

    _validate_hosted_icon_references(d2_text)
    resolved_d2 = _resolve_d2_executable(DEFAULT_D2_EXECUTABLE)

    with tempfile.TemporaryDirectory(prefix="unoplat-architecture-d2-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_svg_path = temp_root / ARCHITECTURE_RENDER_ARTIFACT
        temp_png_path = temp_root / "architecture-preview.png"

        _run_d2_command(
            [resolved_d2, "validate", str(source_path)],
            working_directory=repository_root,
            timeout_seconds=D2_TIMEOUT_SECONDS,
            failure_label="D2 validate",
        )
        _run_d2_command(
            [
                resolved_d2,
                f"--layout={D2_LAYOUT_ENGINE}",
                f"--elk-nodeNodeBetweenLayers={D2_ELK_NODE_NODE_BETWEEN_LAYERS}",
                f"--elk-edgeNodeBetweenLayers={D2_ELK_EDGE_NODE_BETWEEN_LAYERS}",
                f"--elk-padding={D2_ELK_PADDING}",
                f"--pad={D2_PAD_PIXELS}",
                str(source_path),
                str(temp_svg_path),
            ],
            working_directory=repository_root,
            timeout_seconds=D2_TIMEOUT_SECONDS,
            failure_label="D2 ELK SVG render",
        )

        svg_bytes = _read_bounded_binary_file(
            temp_svg_path,
            max_bytes=MAX_ARCHITECTURE_SVG_BYTES,
            missing_message=(
                "D2 ELK SVG render completed without producing an output SVG."
            ),
            unreadable_label="D2 SVG output",
            oversized_label="D2 SVG render",
        )
        svg_root = _validate_svg_output(svg_bytes)
        preview_width, preview_height = _preview_viewport_from_svg(svg_root)

        # Preview the exact temporary SVG before mutating repository artifacts so
        # Chromium/preview failures preserve any prior architecture.svg.
        png_bytes = _render_png_preview(
            svg_path=temp_svg_path,
            png_path=temp_png_path,
            window_width=preview_width,
            window_height=preview_height,
            timeout_seconds=CHROMIUM_TIMEOUT_SECONDS,
            max_png_bytes=MAX_ARCHITECTURE_PNG_BYTES,
        )

        try:
            _atomic_write_bytes(render_path, svg_bytes)
        except OSError as exc:
            raise ModelRetry(
                f"{ARCHITECTURE_RENDER_ARTIFACT} could not be written: "
                f"{exc.strerror or exc}."
            ) from exc

    d2_digest = hashlib.sha256(d2_bytes).hexdigest()
    svg_digest = hashlib.sha256(svg_bytes).hexdigest()
    confirmation = (
        f"{ARCHITECTURE_SOURCE_ARTIFACT} / {ARCHITECTURE_RENDER_ARTIFACT} "
        "validation passed for the current on-disk content "
        f"(d2_sha256={d2_digest}, svg_sha256={svg_digest})."
    )
    return ToolReturn(
        return_value=[
            confirmation,
            BinaryContent(data=png_bytes, media_type="image/png"),
        ],
    )


def _read_bounded_text_file(
    path: Path,
    *,
    max_bytes: int,
    missing_message: str,
    unreadable_label: str,
    oversized_label: str,
) -> bytes:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    try:
        if path.exists() and not path.is_file():
            raise ModelRetry(
                f"{unreadable_label} must be a regular file at the repository root."
            )
        if not path.is_file():
            raise ModelRetry(missing_message)
        with path.open("rb") as handle:
            payload = handle.read(max_bytes + 1)
    except ModelRetry:
        raise
    except OSError as exc:
        raise ModelRetry(
            f"{unreadable_label} could not be read: {exc.strerror or exc}."
        ) from exc

    if len(payload) > max_bytes:
        raise ModelRetry(
            f"{oversized_label} is too large (maximum {max_bytes} UTF-8 bytes)."
        )
    return payload


def _read_bounded_binary_file(
    path: Path,
    *,
    max_bytes: int,
    missing_message: str,
    unreadable_label: str,
    oversized_label: str,
) -> bytes:
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    try:
        if not path.is_file():
            raise ModelRetry(missing_message)
        with path.open("rb") as handle:
            payload = handle.read(max_bytes + 1)
    except ModelRetry:
        raise
    except OSError as exc:
        raise ModelRetry(
            f"{unreadable_label} could not be read: {exc.strerror or exc}."
        ) from exc

    if not payload:
        raise ModelRetry(f"{unreadable_label} is empty.")
    if len(payload) > max_bytes:
        raise ModelRetry(
            f"{oversized_label} exceeded the safe size cap ({max_bytes} bytes)."
        )
    return payload


@lru_cache(maxsize=1)
def _load_allowed_hosted_icon_urls() -> frozenset[str]:
    icons_root = (
        files("unoplat_code_confluence_query_engine")
        / "skills"
        / "architecture-diagrams"
        / "icons"
    )
    allowed: set[str] = set()
    for category in _ICON_CATALOG_CATEGORIES:
        catalog = icons_root / category / "catalog.json"
        try:
            catalog_text = catalog.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError, UnicodeDecodeError) as exc:
            raise ModelRetry(
                "Packaged D2 icon catalogs are unavailable "
                f"({category}/catalog.json): {exc}."
            ) from exc
        try:
            payload = json.loads(catalog_text)
        except json.JSONDecodeError as exc:
            raise ModelRetry(
                f"Packaged D2 icon catalog {category}/catalog.json is invalid JSON."
            ) from exc
        icons = payload.get("icons")
        if not isinstance(icons, list):
            raise ModelRetry(
                f"Packaged D2 icon catalog {category}/catalog.json is missing icons."
            )
        for entry in icons:
            if not isinstance(entry, dict):
                continue
            url = entry.get("url")
            if isinstance(url, str) and url.startswith(HOSTED_ICON_URL_MARKER):
                allowed.add(url)

    if not allowed:
        raise ModelRetry("Packaged D2 icon catalogs did not provide any allowed URLs.")
    return frozenset(allowed)


def _extract_icon_references(d2_text: str) -> list[str]:
    references: list[str] = []
    for match in _ICON_PROPERTY_PATTERN.finditer(d2_text):
        raw_value = match.group("value").strip()
        if not raw_value:
            continue
        if len(raw_value) >= 2 and (
            (raw_value[0] == raw_value[-1] == '"')
            or (raw_value[0] == raw_value[-1] == "'")
        ):
            raw_value = raw_value[1:-1].strip()
        if raw_value:
            references.append(raw_value)
    return references


def _validate_hosted_icon_references(d2_text: str) -> None:
    allowed_urls = _load_allowed_hosted_icon_urls()
    unsupported = sorted(
        {
            reference
            for reference in _extract_icon_references(d2_text)
            if reference not in allowed_urls
        }
    )
    if unsupported:
        preview = ", ".join(unsupported[:8])
        if len(unsupported) > 8:
            preview += ", …"
        raise ModelRetry(
            "Unsupported architecture icon reference(s): "
            f"{preview}. Use only exact HTTPS URLs from the packaged "
            "development/technology/infrastructure catalogs, or omit icons."
        )


def _normalize_d2_version(raw_version: str) -> str:
    first_line = next(
        (line.strip() for line in raw_version.splitlines() if line.strip()),
        "",
    )
    if not first_line:
        return ""
    # Accept both "v0.7.1" and "0.7.1".
    if first_line[0].isdigit():
        return f"v{first_line}"
    return first_line


def _resolve_d2_executable(d2_executable: str) -> str:
    if D2_VERSION_TIMEOUT_SECONDS <= 0:
        raise ValueError("D2_VERSION_TIMEOUT_SECONDS must be positive")

    resolved_d2 = shutil.which(d2_executable)
    if resolved_d2 is None:
        raise ModelRetry(
            f"D2 executable '{d2_executable}' is unavailable. Install pinned "
            f"D2 {REQUIRED_D2_VERSION}."
        )

    try:
        result = subprocess.run(
            [resolved_d2, "--version"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=D2_VERSION_TIMEOUT_SECONDS,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ModelRetry(
            f"D2 version check timed out after {D2_VERSION_TIMEOUT_SECONDS} seconds."
        ) from exc
    except OSError as exc:
        raise ModelRetry(
            f"D2 version check could not start: {exc.strerror or exc}."
        ) from exc

    version_text = _concise_diagnostic(result.stdout or result.stderr)
    if result.returncode != 0:
        message = f"D2 version check failed (exit {result.returncode})."
        if version_text:
            message += f" {version_text}"
        raise ModelRetry(message)

    normalized = _normalize_d2_version(
        (result.stdout or b"").decode("utf-8", errors="replace")
    )
    if normalized != REQUIRED_D2_VERSION:
        found = normalized or version_text or "unknown"
        raise ModelRetry(
            f"D2 {REQUIRED_D2_VERSION} is required for architecture validation; "
            f"found {found}."
        )
    return resolved_d2


def _run_d2_command(
    command: list[str],
    *,
    working_directory: Path,
    timeout_seconds: int,
    failure_label: str,
) -> subprocess.CompletedProcess[bytes]:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    try:
        result = subprocess.run(
            command,
            cwd=working_directory,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        diagnostic = _concise_diagnostic(exc.stderr or exc.stdout)
        message = f"{failure_label} timed out after {timeout_seconds} seconds."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message) from exc
    except OSError as exc:
        raise ModelRetry(
            f"{failure_label} could not start: {exc.strerror or exc}."
        ) from exc

    if result.returncode != 0:
        diagnostic = _concise_diagnostic(result.stderr or result.stdout)
        message = f"{failure_label} failed (exit {result.returncode})."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message)
    return result


def _validate_svg_output(svg_bytes: bytes) -> ElementTree.Element:
    if not svg_bytes.strip():
        raise ModelRetry("D2 exited successfully without returning SVG output.")

    try:
        svg_root = ElementTree.fromstring(svg_bytes)
    except ElementTree.ParseError as exc:
        diagnostic = _concise_diagnostic(svg_bytes)
        message = "D2 returned malformed XML instead of a valid SVG."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message) from exc

    if _local_name(svg_root.tag).lower() != "svg":
        raise ModelRetry(
            "D2 returned XML whose root element is not <svg> "
            f"(found <{_local_name(svg_root.tag)}>)."
        )

    svg_text = svg_bytes.decode("utf-8", errors="replace")
    if HOSTED_ICON_URL_MARKER in svg_text:
        raise ModelRetry(
            "Rendered architecture.svg still contains unresolved hosted icon URL "
            f"references under {HOSTED_ICON_URL_MARKER}. Icons must be embedded "
            "during the canonical D2 render."
        )

    _validate_svg_image_references(svg_root)
    return svg_root


def _validate_svg_image_references(svg_root: ElementTree.Element) -> None:
    """Require rendered SVG images to be embedded before Chromium opens the file.

    D2 normally turns icon URLs into ``data:image/...`` references. Any other
    ``href`` on an SVG image (including ``http(s)``, protocol-relative, file,
    and relative paths) could make headless Chromium perform I/O while creating
    the preview, so fail closed instead of attempting to classify URL schemes.
    """
    unsupported: set[str] = set()
    for element in svg_root.iter():
        if _local_name(element.tag).lower() not in _SVG_IMAGE_ELEMENTS:
            continue
        for attribute, raw_value in element.attrib.items():
            if _local_name(attribute).lower() != "href":
                continue
            reference = raw_value.strip()
            if not reference.lower().startswith(_SVG_EMBEDDED_IMAGE_PREFIX):
                unsupported.add(reference or "<empty>")

    if unsupported:
        preview = ", ".join(sorted(unsupported)[:8])
        if len(unsupported) > 8:
            preview += ", …"
        raise ModelRetry(
            "Rendered architecture.svg contains unembedded image reference(s): "
            f"{preview}. All SVG images must use embedded data:image/ references "
            "before Chromium preview rendering."
        )


def _parse_svg_dimension(raw_value: str | None) -> float | None:
    if raw_value is None:
        return None
    normalized = raw_value.strip().lower()
    if not normalized or normalized.endswith("%"):
        return None
    for suffix in ("px", "pt", "pc", "mm", "cm", "in"):
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)].strip()
            break
    try:
        value = float(normalized)
    except ValueError:
        return None
    if value <= 0:
        return None
    return value


def _dimensions_from_view_box(raw_view_box: str | None) -> tuple[float, float] | None:
    if raw_view_box is None:
        return None
    parts = raw_view_box.replace(",", " ").split()
    if len(parts) != 4:
        return None
    try:
        width = float(parts[2])
        height = float(parts[3])
    except ValueError:
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height


def _clamp_preview_dimension(value: float, *, minimum: int, maximum: int) -> int:
    rounded = int(round(value))
    if rounded < minimum:
        return minimum
    if rounded > maximum:
        return maximum
    return rounded


def _preview_viewport_from_svg(svg_root: ElementTree.Element) -> tuple[int, int]:
    """Derive a Chromium viewport that fits the SVG within safe bounds."""
    width = _parse_svg_dimension(svg_root.attrib.get("width"))
    height = _parse_svg_dimension(svg_root.attrib.get("height"))
    if width is None or height is None:
        view_box_dimensions = _dimensions_from_view_box(svg_root.attrib.get("viewBox"))
        if view_box_dimensions is not None:
            width, height = view_box_dimensions

    if width is None or height is None:
        return PREVIEW_DEFAULT_WIDTH, PREVIEW_DEFAULT_HEIGHT

    return (
        _clamp_preview_dimension(
            width,
            minimum=PREVIEW_MIN_WIDTH,
            maximum=PREVIEW_MAX_WIDTH,
        ),
        _clamp_preview_dimension(
            height,
            minimum=PREVIEW_MIN_HEIGHT,
            maximum=PREVIEW_MAX_HEIGHT,
        ),
    )


def _atomic_write_bytes(target_path: Path, payload: bytes) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{target_path.name}.",
        suffix=".tmp",
        dir=str(target_path.parent),
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target_path)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _resolve_chromium_executable() -> str:
    for candidate in _CHROMIUM_CANDIDATES:
        if os.path.isabs(candidate):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
            continue
        resolved = shutil.which(candidate)
        if resolved is not None:
            return resolved
    raise ModelRetry(
        "Chromium is unavailable for temporary architecture SVG preview rendering."
    )


def _render_png_preview(
    *,
    svg_path: Path,
    png_path: Path,
    window_width: int,
    window_height: int,
    timeout_seconds: int,
    max_png_bytes: int,
) -> bytes:
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if max_png_bytes <= 0:
        raise ValueError("max_png_bytes must be positive")
    if window_width <= 0 or window_height <= 0:
        raise ValueError("preview window dimensions must be positive")

    chromium = _resolve_chromium_executable()
    resolved_svg = svg_path.resolve()
    resolved_png = png_path.resolve()
    if not resolved_svg.is_file():
        raise ModelRetry(
            "Temporary validated SVG is missing; cannot create architecture preview."
        )

    command = [
        chromium,
        "--headless=new",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={window_width},{window_height}",
        f"--screenshot={resolved_png}",
        resolved_svg.as_uri(),
    ]

    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        diagnostic = _concise_diagnostic(exc.stderr or exc.stdout)
        message = (
            f"Chromium architecture preview timed out after {timeout_seconds} seconds."
        )
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message) from exc
    except OSError as exc:
        raise ModelRetry(
            f"Chromium architecture preview could not start: {exc.strerror or exc}."
        ) from exc

    try:
        return _read_bounded_png(resolved_png, max_png_bytes=max_png_bytes)
    except ModelRetry as exc:
        diagnostic = _concise_diagnostic(result.stderr or result.stdout)
        if result.returncode != 0:
            message = (
                f"Chromium architecture preview failed (exit {result.returncode})."
            )
            if diagnostic:
                message += f" {diagnostic}"
            raise ModelRetry(message) from exc
        if diagnostic:
            raise ModelRetry(f"{exc} {diagnostic}") from exc
        raise


def _read_bounded_png(png_path: Path, *, max_png_bytes: int) -> bytes:
    try:
        if not png_path.is_file():
            raise ModelRetry(
                "Chromium architecture preview completed without producing an "
                "output image."
            )
        with png_path.open("rb") as png_file:
            png_bytes = png_file.read(max_png_bytes + 1)
    except ModelRetry:
        raise
    except OSError as exc:
        raise ModelRetry(
            f"Chromium architecture preview could not be read: {exc.strerror or exc}."
        ) from exc

    if not png_bytes:
        raise ModelRetry("Chromium architecture preview produced an empty image file.")
    if len(png_bytes) > max_png_bytes:
        raise ModelRetry(
            "Chromium architecture preview exceeded the safe size cap "
            f"({max_png_bytes} bytes)."
        )
    if not png_bytes.startswith(PNG_SIGNATURE):
        diagnostic = _concise_diagnostic(png_bytes)
        message = "Chromium architecture preview did not produce a valid PNG signature."
        if diagnostic:
            message += f" {diagnostic}"
        raise ModelRetry(message)
    return png_bytes


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _concise_diagnostic(diagnostic: str | bytes | None) -> str:
    if isinstance(diagnostic, bytes):
        diagnostic = diagnostic.decode("utf-8", errors="replace")
    normalized = " ".join((diagnostic or "").split())
    if len(normalized) > MAX_RENDER_DIAGNOSTIC_CHARACTERS:
        return normalized[:MAX_RENDER_DIAGNOSTIC_CHARACTERS].rstrip() + "…"
    return normalized
