"""Utilities for canonical engineering workflow normalization and assembly."""

from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import Iterable

from loguru import logger

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
    EngineeringWorkflowCommand,
    EngineeringWorkflowStage,
)

_STAGE_ORDER: dict[EngineeringWorkflowStage, int] = {
    EngineeringWorkflowStage.INSTALL: 0,
    EngineeringWorkflowStage.BUILD: 1,
    EngineeringWorkflowStage.DEV: 2,
    EngineeringWorkflowStage.TEST: 3,
    EngineeringWorkflowStage.LINT: 4,
    EngineeringWorkflowStage.TYPE_CHECK: 5,
}

_STAGE_ALIASES: dict[str, str] = {
    "setup": "install",
    "bootstrap": "install",
    "dependency_install": "install",
    "dependencies": "install",
    "deps": "install",
    "typecheck": "type_check",
    "type-check": "type_check",
    "typing": "type_check",
}

CONFIDENCE_THRESHOLD: float = 0.35


def _normalize_path(path: str) -> str:
    candidate = (path or "").strip().replace("\\", "/")
    candidate = re.sub(r"^[A-Za-z]:/", "", candidate)

    if not candidate:
        raise ValueError("config path must be non-empty")

    # Best-effort strip of absolute prefixes while preserving repo-relative tail.
    if candidate.startswith("/"):
        marker = "/opt/unoplat/repositories/"
        marker_index = candidate.find(marker)
        if marker_index != -1:
            tail = candidate[marker_index + len(marker) :]
            candidate_parts = [p for p in tail.split("/") if p]
            candidate = "/".join(candidate_parts[1:]) if len(candidate_parts) > 1 else tail
        else:
            candidate = candidate.lstrip("/")

    normalized = PurePosixPath(candidate).as_posix()
    if normalized == "." or normalized.startswith("../") or "/../" in normalized:
        raise ValueError(f"invalid repo-relative path: {path}")

    return normalized


def normalize_commands(commands: Iterable[dict[str, object]]) -> list[EngineeringWorkflowCommand]:
    dedup: dict[tuple[EngineeringWorkflowStage, str], EngineeringWorkflowCommand] = {}

    for raw in commands:
        stage_value = raw.get("stage", "")
        if isinstance(stage_value, EngineeringWorkflowStage):
            stage_raw = stage_value.value
        else:
            stage_raw = str(stage_value).strip().lower()
            stage_raw = _STAGE_ALIASES.get(stage_raw, stage_raw)
        command = str(raw.get("command", "")).strip()
        if not stage_raw or not command:
            logger.warning("Skipping invalid command entry with stage='{}' command='{}'", stage_raw, command)
            continue

        try:
            stage = EngineeringWorkflowStage(stage_raw)
        except ValueError:
            logger.warning("Skipping command with unsupported stage '{}'", stage_raw)
            continue

        # Normalize config_file: fallback to "unknown" on ValueError or empty
        raw_config_file = str(raw.get("config_file", "")).strip()
        if raw_config_file:
            try:
                config_file = _normalize_path(raw_config_file)
            except ValueError:
                logger.warning(
                    "Invalid config_file '{}' for command '{}', falling back to 'unknown'",
                    raw_config_file,
                    command,
                )
                config_file = "unknown"
        else:
            config_file = "unknown"

        # Parse confidence as float, clamp to [0.0, 1.0]
        raw_confidence = raw.get("confidence", 0.0)
        try:
            confidence = float(str(raw_confidence))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        key = (stage, command)
        existing = dedup.get(key)
        # Dedupe on (stage, command) retaining highest confidence
        if existing is None or confidence > existing.confidence:
            dedup[key] = EngineeringWorkflowCommand(
                command=command,
                stage=stage,
                config_file=config_file,
                confidence=confidence,
            )

    # Filter by confidence threshold
    filtered = [cmd for cmd in dedup.values() if cmd.confidence >= CONFIDENCE_THRESHOLD]

    return sorted(
        filtered,
        key=lambda item: (_STAGE_ORDER[item.stage], item.command.lower()),
    )


def _extract_command_dicts(payload: dict[str, object]) -> list[dict[str, object]]:
    """Extract command dicts from a raw JSON payload with type narrowing."""
    raw_commands = payload.get("commands")
    if not isinstance(raw_commands, list):
        return []
    result: list[dict[str, object]] = []
    for entry in raw_commands:
        if isinstance(entry, dict):
            result.append(entry)
    return result


def normalize_engineering_workflow(payload: dict[str, object]) -> EngineeringWorkflow:
    commands = normalize_commands(_extract_command_dicts(payload))
    return EngineeringWorkflow(commands=commands)
