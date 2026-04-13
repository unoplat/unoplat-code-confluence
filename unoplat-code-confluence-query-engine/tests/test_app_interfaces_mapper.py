"""Unit tests for app interface structured feature mapping."""

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    InboundKind,
    OutboundKind,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    build_interfaces_from_features,
)


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
    assert ("fastmcp", OutboundKind.MCP_CLIENT) in outbound_pairs
    assert ("litellm", OutboundKind.LLM_INFERENCE) in outbound_pairs
    assert ("httpx", OutboundKind.HTTP) in outbound_pairs


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
