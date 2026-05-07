"""Mapper for converting framework features to app interface constructs."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import AsyncIterable
from typing import Optional

from pydantic import BaseModel, ConfigDict

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    InboundConstruct,
    InboundKind,
    Interfaces,
    InternalConstruct,
    OutboundConstruct,
    OutboundKind,
)

_DATA_MODEL_CAPABILITY_KEYS: frozenset[str] = frozenset(
    {
        "data_model",
        "relational_database",
        "data_validation",
    }
)
_DATA_MODEL_OPERATION_KEYS: frozenset[str] = frozenset({"data_model", "db_data_model"})

# Mapping from structured capability/operation values to InboundKind
INBOUND_FEATURE_MAPPING: dict[str, InboundKind] = {
    "rest_api": InboundKind.HTTP,
    "http_endpoint": InboundKind.HTTP,
    "api_router": InboundKind.HTTP,
    "graphql_resolver": InboundKind.GRAPHQL,
    "rpc_service": InboundKind.RPC_GENERIC,
    "websocket_endpoint": InboundKind.WEBSOCKET,
    "webhook_receiver": InboundKind.WEBHOOK,
    "message_consumer": InboundKind.MSG_CONSUMER,
    "scheduler": InboundKind.SCHEDULE,
    "scheduler_trigger": InboundKind.SCHEDULE,
    "task_definition": InboundKind.SCHEDULE,
    "cli_command": InboundKind.CLI,
    "sse_endpoint": InboundKind.SSE,
    "mqtt_iot_endpoint": InboundKind.MQTT_IOT_ENDPOINT,
    "udp_server": InboundKind.UDP_SERVER,
    "tcp_raw_server": InboundKind.TCP_RAW_SERVER,
    "file_watcher": InboundKind.FILE_WATCHER,
    "mcp_tool": InboundKind.MCP_SERVER,
    "mcp_resource": InboundKind.MCP_SERVER,
}

# Mapping from structured capability/operation values to OutboundKind
OUTBOUND_FEATURE_MAPPING: dict[str, OutboundKind] = {
    "http_client": OutboundKind.HTTP,
    "db_sql": OutboundKind.DB_SQL,
    "db_nosql": OutboundKind.DB_NOSQL,
    "message_producer": OutboundKind.MSG_PRODUCER,
    "cache_operation": OutboundKind.CACHE,
    "task_queue_enqueue": OutboundKind.QUEUE_TASK,
    "graphql_client": OutboundKind.GRAPHQL,
    "rpc_client": OutboundKind.RPC_GENERIC,
    "mcp_client": OutboundKind.MCP_CLIENT,
    "websocket_client": OutboundKind.WEBSOCKET_CLIENT,
    "file_storage": OutboundKind.FILE_STORAGE,
    "email_service": OutboundKind.EMAIL,
    "telemetry_emit": OutboundKind.TELEMETRY,
    "llm_completion": OutboundKind.LLM_INFERENCE,
    "llm_embedding": OutboundKind.LLM_INFERENCE,
    "db_timeseries": OutboundKind.DB_TSDB,
    "db_vector": OutboundKind.DB_VECTOR,
    "db_search_index": OutboundKind.DB_SEARCH_INDEX,
}


class AppInterfaceFeatureRow(BaseModel):
    """Minimal app-interface feature usage row consumed by the mapper."""

    model_config = ConfigDict(frozen=True)

    library: str | None
    feature_capability_key: str
    feature_operation_key: str
    file_path: str
    start_line: int
    end_line: int
    match_text: str | None


InboundGroups = dict[tuple[str, InboundKind], dict[str, set[str]]]
OutboundGroups = dict[tuple[str, OutboundKind], dict[str, set[str]]]
InternalGroups = dict[tuple[str, str], dict[str, set[str]]]


def _compose_feature_key(capability_key: str, operation_key: str) -> str:
    return f"{capability_key}.{operation_key}"


def _is_data_model_feature_family(
    capability_key: str,
    operation_key: str,
) -> bool:
    return (
        capability_key in _DATA_MODEL_CAPABILITY_KEYS
        and operation_key in _DATA_MODEL_OPERATION_KEYS
    )


def convert_to_relative_path(absolute_path: str, codebase_path: str) -> str:
    """Convert absolute file path to codebase-relative path."""
    if not absolute_path or not codebase_path:
        return absolute_path

    normalized_codebase = codebase_path.rstrip("/")

    if absolute_path.startswith(normalized_codebase):
        relative = absolute_path[len(normalized_codebase) :]
        return relative.lstrip("/")

    return absolute_path


def get_match_identifier(
    match_text: Optional[str],
    start_line: int,
    end_line: int,
) -> str:
    """Get a match identifier preferring match_text, falling back to line span."""
    if match_text and match_text.strip():
        return f"L{start_line}: {match_text.strip()}"

    if start_line == end_line:
        return f"L{start_line}"
    return f"L{start_line}-L{end_line}"


def _resolve_inbound_kind(
    capability_key: str,
    operation_key: str,
) -> InboundKind | None:
    for candidate in (capability_key, operation_key):
        kind = INBOUND_FEATURE_MAPPING.get(candidate)
        if kind is not None:
            return kind
    return None


def _resolve_outbound_kind(
    capability_key: str,
    operation_key: str,
) -> OutboundKind | None:
    for candidate in (operation_key, capability_key):
        kind = OUTBOUND_FEATURE_MAPPING.get(candidate)
        if kind is not None:
            return kind
    return None


def _new_inbound_groups() -> InboundGroups:
    return defaultdict(lambda: defaultdict(set))


def _new_outbound_groups() -> OutboundGroups:
    return defaultdict(lambda: defaultdict(set))


def _new_internal_groups() -> InternalGroups:
    return defaultdict(lambda: defaultdict(set))


def _add_feature_row_to_groups(
    *,
    row: AppInterfaceFeatureRow,
    codebase_path: str,
    inbound_groups: InboundGroups,
    outbound_groups: OutboundGroups,
    internal_groups: InternalGroups,
) -> None:
    capability_key = row.feature_capability_key.strip()
    operation_key = row.feature_operation_key.strip()
    if not capability_key or not operation_key:
        return
    if _is_data_model_feature_family(capability_key, operation_key):
        return

    relative_path = convert_to_relative_path(row.file_path, codebase_path)
    match_identifier = get_match_identifier(
        row.match_text,
        row.start_line,
        row.end_line,
    )

    inbound_kind = _resolve_inbound_kind(capability_key, operation_key)
    if inbound_kind is not None:
        key = (row.library or "", inbound_kind)
        inbound_groups[key][relative_path].add(match_identifier)
        return

    outbound_kind = _resolve_outbound_kind(capability_key, operation_key)
    if outbound_kind is not None:
        key = (row.library or "", outbound_kind)
        outbound_groups[key][relative_path].add(match_identifier)
        return

    feature_key = _compose_feature_key(capability_key, operation_key)
    key = (row.library or "", feature_key)
    internal_groups[key][relative_path].add(match_identifier)


def _build_interfaces_from_groups(
    *,
    inbound_groups: InboundGroups,
    outbound_groups: OutboundGroups,
    internal_groups: InternalGroups,
) -> Interfaces:
    inbound_constructs: list[InboundConstruct] = []
    for (library, kind), file_matches in inbound_groups.items():
        match_pattern: dict[str, list[str]] = {
            path: sorted(matches) for path, matches in file_matches.items()
        }
        inbound_constructs.append(
            InboundConstruct(
                kind=kind,
                library=library if library else None,
                match_pattern=match_pattern,
            )
        )

    outbound_constructs: list[OutboundConstruct] = []
    for (library, kind), file_matches in outbound_groups.items():
        match_pattern = {
            path: sorted(matches) for path, matches in file_matches.items()
        }
        outbound_constructs.append(
            OutboundConstruct(
                kind=kind,
                library=library if library else None,
                match_pattern=match_pattern,
            )
        )

    internal_constructs: list[InternalConstruct] = []
    for (library, feature_key), file_matches in internal_groups.items():
        match_pattern = {
            path: sorted(matches) for path, matches in file_matches.items()
        }
        internal_constructs.append(
            InternalConstruct(
                kind=feature_key,
                library=library if library else None,
                match_pattern=match_pattern,
            )
        )

    return Interfaces(
        inbound_constructs=inbound_constructs,
        outbound_constructs=outbound_constructs,
        internal_constructs=internal_constructs,
    )


async def build_interfaces_from_feature_rows(
    feature_rows: AsyncIterable[AppInterfaceFeatureRow],
    codebase_path: str,
) -> Interfaces:
    """Build Interfaces by consuming streamed framework feature rows once."""
    inbound_groups = _new_inbound_groups()
    outbound_groups = _new_outbound_groups()
    internal_groups = _new_internal_groups()

    async for row in feature_rows:
        _add_feature_row_to_groups(
            row=row,
            codebase_path=codebase_path,
            inbound_groups=inbound_groups,
            outbound_groups=outbound_groups,
            internal_groups=internal_groups,
        )

    return _build_interfaces_from_groups(
        inbound_groups=inbound_groups,
        outbound_groups=outbound_groups,
        internal_groups=internal_groups,
    )


def build_interfaces_from_features(
    features: list[dict[str, object]],
    codebase_path: str,
) -> Interfaces:
    """Build Interfaces model from already-materialized framework features."""
    inbound_groups = _new_inbound_groups()
    outbound_groups = _new_outbound_groups()
    internal_groups = _new_internal_groups()

    for feature in features:
        match_text_raw = feature.get("match_text")
        _add_feature_row_to_groups(
            row=AppInterfaceFeatureRow(
                library=(
                    str(feature.get("library")) if feature.get("library") else None
                ),
                feature_capability_key=str(
                    feature.get("feature_capability_key", "")
                ),
                feature_operation_key=str(feature.get("feature_operation_key", "")),
                file_path=str(feature.get("file_path", "")),
                start_line=int(feature.get("start_line", 0)),  # type: ignore[arg-type]
                end_line=int(feature.get("end_line", 0)),  # type: ignore[arg-type]
                match_text=str(match_text_raw) if match_text_raw else None,
            ),
            codebase_path=codebase_path,
            inbound_groups=inbound_groups,
            outbound_groups=outbound_groups,
            internal_groups=internal_groups,
        )

    return _build_interfaces_from_groups(
        inbound_groups=inbound_groups,
        outbound_groups=outbound_groups,
        internal_groups=internal_groups,
    )
