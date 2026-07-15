"""Unit tests for app interface structured feature mapping."""

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    BidirectionalConstruct,
    BidirectionalKind,
    InboundKind,
    Interfaces,
    OutboundKind,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    build_interfaces_from_features,
)


def test_interfaces_defaults_bidirectional_constructs_for_legacy_payloads() -> None:
    interfaces = Interfaces.model_validate(
        {
            "inbound_constructs": [],
            "outbound_constructs": [],
            "internal_constructs": [],
        }
    )

    assert interfaces.bidirectional_constructs == []


def test_interfaces_serializes_bidirectional_construct_evidence() -> None:
    interfaces = Interfaces(
        bidirectional_constructs=[
            BidirectionalConstruct(
                kind=BidirectionalKind.REALTIME_SYNC,
                library="@tanstack/react-db",
                match_pattern={"src/hooks.ts": ["L20: useLiveQuery(...)"]},
            )
        ]
    )

    payload = interfaces.model_dump(mode="json")
    construct = payload["bidirectional_constructs"][0]
    assert construct["kind"] == "realtime_sync"
    assert construct["library"] == "@tanstack/react-db"
    assert construct["match_pattern"] == {
        "src/hooks.ts": ["L20: useLiveQuery(...)"]
    }
    assert "flows" not in construct
    assert "technology" not in construct


def test_build_interfaces_maps_structured_inbound_and_outbound_features() -> None:
    features = [
        {
            "library": "fastapi",
            "feature_capability_key": "rest_api",
            "feature_operation_key": "get",
            "file_path": "/repo/api/routes.py",
            "start_line": 10,
            "end_line": 12,
            "match_text": "@router.get('/health')",
        },
        {
            "library": "fastmcp",
            "feature_capability_key": "mcp_server",
            "feature_operation_key": "mcp_tool",
            "file_path": "/repo/mcp_server.py",
            "start_line": 5,
            "end_line": 8,
            "match_text": "@mcp.tool()",
        },
        {
            "library": "fastmcp",
            "feature_capability_key": "mcp_client",
            "feature_operation_key": "toolset_client",
            "file_path": "/repo/services/mcp/mcp_server_manager.py",
            "start_line": 125,
            "end_line": 125,
            "match_text": "FastMCPToolset(mcp_config, id=id_value)",
        },
        {
            "library": "litellm",
            "feature_capability_key": "llm_inference",
            "feature_operation_key": "llm_completion",
            "file_path": "/repo/llm.py",
            "start_line": 20,
            "end_line": 20,
            "match_text": "completion(model='gpt-4o-mini')",
        },
        {
            "library": "httpx",
            "feature_capability_key": "http_client",
            "feature_operation_key": "request",
            "file_path": "/repo/clients/http.py",
            "start_line": 31,
            "end_line": 31,
            "match_text": "await client.get('/api')",
        },
        {
            "library": "click",
            "feature_capability_key": "cli_command",
            "feature_operation_key": "command",
            "file_path": "/repo/cli.py",
            "start_line": 8,
            "end_line": 11,
            "match_text": "@click.command()",
        },
        {
            "library": "httpx2",
            "feature_capability_key": "http_client",
            "feature_operation_key": "http_request",
            "file_path": "/repo/clients/httpx2_client.py",
            "start_line": 20,
            "end_line": 20,
            "match_text": "httpx2.get('/api')",
        },
        {
            "library": "httpx2",
            "feature_capability_key": "websocket_client",
            "feature_operation_key": "websocket",
            "file_path": "/repo/clients/httpx2_client.py",
            "start_line": 25,
            "end_line": 25,
            "match_text": "httpx2.websocket('/events')",
        },
        {
            "library": "temporalio",
            "feature_capability_key": "job_queue",
            "feature_operation_key": "task_queue_enqueue",
            "file_path": "/repo/workflows/main.py",
            "start_line": 42,
            "end_line": 45,
            "match_text": "await workflow.execute_activity(run_activity)",
        },
    ]

    interfaces = build_interfaces_from_features(features, "/repo")

    inbound_pairs = {
        (construct.library, construct.kind)
        for construct in interfaces.inbound_constructs
    }
    outbound_pairs = {
        (construct.library, construct.kind)
        for construct in interfaces.outbound_constructs
    }

    assert ("fastapi", InboundKind.HTTP) in inbound_pairs
    assert ("fastmcp", InboundKind.MCP_SERVER) in inbound_pairs
    assert ("click", InboundKind.CLI) in inbound_pairs
    assert ("fastmcp", OutboundKind.MCP_CLIENT) in outbound_pairs
    assert ("litellm", OutboundKind.LLM_INFERENCE) in outbound_pairs
    assert ("httpx", OutboundKind.HTTP) in outbound_pairs
    assert ("httpx2", OutboundKind.HTTP) in outbound_pairs
    assert ("httpx2", OutboundKind.WEBSOCKET_CLIENT) in outbound_pairs
    assert ("temporalio", OutboundKind.QUEUE_TASK) in outbound_pairs


def test_build_interfaces_maps_axios_and_groups_live_queries_as_one_sync_boundary() -> (
    None
):
    features = [
        {
            "library": "axios",
            "feature_capability_key": "http_client",
            "feature_operation_key": "request",
            "file_path": "/repo/src/api.ts",
            "start_line": 8,
            "end_line": 8,
            "match_text": "apiClient.get('/users')",
        },
        {
            "library": "@tanstack/react-db",
            "feature_capability_key": "realtime_sync",
            "feature_operation_key": "live_query",
            "file_path": "/repo/src/hooks.ts",
            "start_line": 20,
            "end_line": 20,
            "match_text": "useLiveQuery(query)",
        },
        {
            "library": "@tanstack/react-db",
            "feature_capability_key": "realtime_sync",
            "feature_operation_key": "live_infinite_query",
            "file_path": "/repo/src/hooks.ts",
            "start_line": 30,
            "end_line": 30,
            "match_text": "useLiveInfiniteQuery(query)",
        },
        # Duplicate evidence must not produce duplicate references.
        {
            "library": "@tanstack/react-db",
            "feature_capability_key": "realtime_sync",
            "feature_operation_key": "live_query",
            "file_path": "/repo/src/hooks.ts",
            "start_line": 20,
            "end_line": 20,
            "match_text": "useLiveQuery(query)",
        },
        # Unknown realtime operations are omitted conservatively.
        {
            "library": "@tanstack/react-db",
            "feature_capability_key": "realtime_sync",
            "feature_operation_key": "unknown",
            "file_path": "/repo/src/hooks.ts",
            "start_line": 40,
            "end_line": 40,
            "match_text": "unknown()",
        },
    ]

    interfaces = build_interfaces_from_features(features, "/repo")

    assert len(interfaces.outbound_constructs) == 1
    assert interfaces.outbound_constructs[0].library == "axios"
    assert interfaces.outbound_constructs[0].kind == OutboundKind.HTTP
    assert len(interfaces.bidirectional_constructs) == 1
    sync = interfaces.bidirectional_constructs[0]
    assert sync.kind == BidirectionalKind.REALTIME_SYNC
    assert sync.library == "@tanstack/react-db"
    assert sync.match_pattern == {
        "src/hooks.ts": [
            "L20: useLiveQuery(query)",
            "L30: useLiveInfiniteQuery(query)",
        ]
    }
    assert interfaces.internal_constructs == []


def test_build_interfaces_maps_completed_relational_db_sql_to_outbound() -> None:
    features = [
        {
            "library": "sqlalchemy",
            "feature_capability_key": "relational_database",
            "feature_operation_key": "db_sql",
            "file_path": "/repo/db/writes.py",
            "start_line": 14,
            "end_line": 14,
            "match_text": "await session.execute(statement)",
            "validation_status": "completed",
        }
    ]

    interfaces = build_interfaces_from_features(features, "/repo")

    assert len(interfaces.outbound_constructs) == 1
    outbound = interfaces.outbound_constructs[0]
    assert outbound.library == "sqlalchemy"
    assert outbound.kind == OutboundKind.DB_SQL


def test_build_interfaces_drops_data_model_families() -> None:
    features = [
        {
            "library": "pydantic",
            "feature_capability_key": "data_model",
            "feature_operation_key": "data_model",
            "file_path": "/repo/models.py",
            "start_line": 3,
            "end_line": 11,
            "match_text": "class User(BaseModel)",
        },
        {
            "library": "sqlalchemy",
            "feature_capability_key": "relational_database",
            "feature_operation_key": "db_data_model",
            "file_path": "/repo/db/models.py",
            "start_line": 7,
            "end_line": 26,
            "match_text": "class User(SQLBase)",
        },
    ]

    interfaces = build_interfaces_from_features(features, "/repo")

    assert interfaces.inbound_constructs == []
    assert interfaces.outbound_constructs == []
    assert interfaces.internal_constructs == []


def test_build_interfaces_keeps_unmapped_feature_as_internal() -> None:
    features = [
        {
            "library": "custom",
            "feature_capability_key": "custom_capability",
            "feature_operation_key": "unknown_feature",
            "file_path": "/repo/custom.py",
            "start_line": 1,
            "end_line": 1,
            "match_text": "custom()",
        }
    ]

    interfaces = build_interfaces_from_features(features, "/repo")

    assert len(interfaces.inbound_constructs) == 0
    assert len(interfaces.outbound_constructs) == 0
    assert len(interfaces.internal_constructs) == 1
    assert interfaces.internal_constructs[0].kind == "custom_capability.unknown_feature"
