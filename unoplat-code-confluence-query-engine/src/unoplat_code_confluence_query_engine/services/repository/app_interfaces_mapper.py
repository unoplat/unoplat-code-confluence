"""Mapper for converting framework features to app interface constructs."""

from __future__ import annotations

from collections import defaultdict
from typing import Optional

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    InboundConstruct,
    InboundKind,
    Interfaces,
    InternalConstruct,
    OutboundConstruct,
    OutboundKind,
)

# Mapping from feature_key to InboundKind
INBOUND_FEATURE_MAPPING: dict[str, InboundKind] = {
    "rest_api": InboundKind.HTTP,
    "http_endpoint": InboundKind.HTTP,
    "api_router": InboundKind.HTTP,
    "graphql_resolver": InboundKind.GRAPHQL,
    "grpc_service": InboundKind.GRPC,
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

# Mapping from feature_key to OutboundKind
OUTBOUND_FEATURE_MAPPING: dict[str, OutboundKind] = {
    "http_client": OutboundKind.HTTP,
    "db_sql": OutboundKind.DB_SQL,
    "db_nosql": OutboundKind.DB_NOSQL,
    "message_producer": OutboundKind.MSG_PRODUCER,
    "cache_operation": OutboundKind.CACHE,
    "task_queue_enqueue": OutboundKind.QUEUE_TASK,
    "graphql_client": OutboundKind.GRAPHQL,
    "grpc_client": OutboundKind.GRPC,
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


def convert_to_relative_path(absolute_path: str, codebase_path: str) -> str:
    """Convert absolute file path to codebase-relative path.

    Args:
        absolute_path: Absolute file path from database
        codebase_path: Root path of the codebase

    Returns:
        Relative path from codebase root
    """
    if not absolute_path or not codebase_path:
        return absolute_path

    # Normalize paths by removing trailing slashes
    normalized_codebase = codebase_path.rstrip("/")

    if absolute_path.startswith(normalized_codebase):
        # Remove codebase prefix and leading slash
        relative = absolute_path[len(normalized_codebase) :]
        return relative.lstrip("/")

    return absolute_path


def get_match_identifier(
    feature_key: str,
    match_text: Optional[str],
    start_line: int,
    end_line: int,
) -> str:
    """Get a match identifier preferring match_text, falling back to line span.

    Args:
        feature_key: The feature key for context
        match_text: Optional match text from database
        start_line: Start line number
        end_line: End line number

    Returns:
        Match identifier string
    """
    if match_text and match_text.strip():
        return f"L{start_line}: {match_text.strip()}"

    # Fallback to line span format
    if start_line == end_line:
        return f"L{start_line}"
    return f"L{start_line}-L{end_line}"


def build_interfaces_from_features(
    features: list[dict[str, object]],
    codebase_path: str,
) -> Interfaces:
    """Build Interfaces model from framework features.

    Args:
        features: List of feature dicts from database query
        codebase_path: Root path of the codebase for relative path conversion

    Returns:
        Interfaces model with inbound, outbound, and internal constructs
    """
    # Group features by classification and (library, kind)
    # Use sets for deduplication per file
    inbound_groups: dict[tuple[str, InboundKind], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    outbound_groups: dict[tuple[str, OutboundKind], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    internal_groups: dict[tuple[str, str], dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for feature in features:
        feature_key = str(feature.get("feature_key", ""))
        library = str(feature.get("library", "")) if feature.get("library") else None
        file_path = str(feature.get("file_path", ""))
        start_line = int(feature.get("start_line", 0))  # type: ignore[arg-type]
        end_line = int(feature.get("end_line", 0))  # type: ignore[arg-type]
        match_text_raw = feature.get("match_text")
        match_text = str(match_text_raw) if match_text_raw else None

        # Convert to relative path
        relative_path = convert_to_relative_path(file_path, codebase_path)

        # Get match identifier
        match_identifier = get_match_identifier(
            feature_key, match_text, start_line, end_line
        )

        # Classify and group
        if feature_key in INBOUND_FEATURE_MAPPING:
            kind = INBOUND_FEATURE_MAPPING[feature_key]
            key = (library or "", kind)
            inbound_groups[key][relative_path].add(match_identifier)
        elif feature_key in OUTBOUND_FEATURE_MAPPING:
            kind = OUTBOUND_FEATURE_MAPPING[feature_key]
            key = (library or "", kind)
            outbound_groups[key][relative_path].add(match_identifier)
        else:
            # Internal construct (unmapped feature_key)
            key = (library or "", feature_key)
            internal_groups[key][relative_path].add(match_identifier)

    # Build construct lists
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
