"""Utilities for canonical engineering workflow normalization and assembly."""

from __future__ import annotations

import re
from pathlib import PurePosixPath
from typing import Iterable

from loguru import logger

from unoplat_code_confluence_query_engine.models.output.engineering_workflow_output import (
    EngineeringWorkflow,
    EngineeringWorkflowCommand,
    EngineeringWorkflowConfig,
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


def _slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value or "item"


def build_config_id(path: str) -> str:
    return f"cfg-{_slug(path)}"


def build_command_id(stage: EngineeringWorkflowStage, command: str) -> str:
    return f"cmd-{stage.value}-{_slug(command)}"


def normalize_configs(configs: Iterable[dict]) -> list[EngineeringWorkflowConfig]:
    dedup: dict[str, EngineeringWorkflowConfig] = {}

    for raw in configs:
        raw_path = str(raw.get("path", ""))
        try:
            path = _normalize_path(raw_path)
        except ValueError as exc:
            logger.warning("Skipping config with invalid path '{}': {}", raw_path, exc)
            continue

        purpose = str(raw.get("purpose", "")).strip()
        required_for = raw.get("required_for") or []
        if not isinstance(required_for, list):
            required_for = []

        existing = dedup.get(path)
        merged_required_for = sorted(
            set((existing.required_for if existing else []) + [str(x) for x in required_for if str(x).strip()])
        )
        dedup[path] = EngineeringWorkflowConfig(
            id=build_config_id(path),
            path=path,
            purpose=purpose or (existing.purpose if existing else "Configuration for engineering workflow"),
            required_for=merged_required_for,
        )

    return sorted(dedup.values(), key=lambda item: (item.path, item.id))


def normalize_commands(commands: Iterable[dict]) -> list[EngineeringWorkflowCommand]:
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

        config_refs_raw = raw.get("config_refs") or []
        if not isinstance(config_refs_raw, list):
            config_refs_raw = []

        key = (stage, command)
        existing = dedup.get(key)
        merged_refs = sorted(
            set((existing.config_refs if existing else []) + [str(x) for x in config_refs_raw if str(x).strip()])
        )

        dedup[key] = EngineeringWorkflowCommand(
            id=build_command_id(stage, command),
            stage=stage,
            command=command,
            description=(
                str(raw.get("description")).strip()
                if raw.get("description") is not None and str(raw.get("description")).strip()
                else (existing.description if existing else None)
            ),
            config_refs=merged_refs,
        )

    return sorted(
        dedup.values(),
        key=lambda item: (_STAGE_ORDER[item.stage], item.command.lower(), item.id),
    )


def resolve_config_refs(
    commands: list[EngineeringWorkflowCommand], configs: list[EngineeringWorkflowConfig]
) -> list[EngineeringWorkflowCommand]:
    valid_ids = {cfg.id for cfg in configs}
    path_to_id = {cfg.path: cfg.id for cfg in configs}

    resolved: list[EngineeringWorkflowCommand] = []
    for cmd in commands:
        mapped: list[str] = []
        for ref in cmd.config_refs:
            if ref in valid_ids:
                mapped.append(ref)
                continue

            try:
                normalized_ref = _normalize_path(ref)
            except ValueError:
                logger.warning("Dropping invalid config_ref '{}' in command '{}'.", ref, cmd.command)
                continue

            mapped_id = path_to_id.get(normalized_ref)
            if mapped_id:
                mapped.append(mapped_id)
            else:
                logger.warning(
                    "Dropping unresolved config_ref '{}' in command '{}'.", ref, cmd.command
                )

        resolved.append(
            cmd.model_copy(update={"config_refs": sorted(set(mapped))})
        )

    return resolved


def normalize_engineering_workflow(payload: dict) -> EngineeringWorkflow:
    configs = normalize_configs(payload.get("configs") or [])
    commands = normalize_commands(payload.get("commands") or [])
    commands = resolve_config_refs(commands, configs)
    return EngineeringWorkflow(configs=configs, commands=commands)
