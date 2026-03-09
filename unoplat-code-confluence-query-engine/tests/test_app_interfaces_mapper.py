"""Unit tests for app interface feature-key mapping."""

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    InboundKind,
    OutboundKind,
)
from unoplat_code_confluence_query_engine.services.repository.app_interfaces_mapper import (
    build_interfaces_from_features,
)


def test_build_interfaces_maps_new_inbound_and_outbound_feature_keys() -> None:
    features = [
        {
            "library": "celery",
            "feature_key": "task_definition",
            "file_path": "/repo/tasks.py",
            "start_line": 10,
            "end_line": 12,
            "match_text": "@shared_task",
        },
        {
            "library": "fastmcp",
            "feature_key": "mcp_tool",
            "file_path": "/repo/mcp_server.py",
            "start_line": 5,
            "end_line": 8,
            "match_text": "@mcp.tool()",
        },
        {
            "library": "litellm",
            "feature_key": "llm_completion",
            "file_path": "/repo/llm.py",
            "start_line": 20,
            "end_line": 20,
            "match_text": "completion(model='gpt-4o-mini')",
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

    assert ("celery", InboundKind.SCHEDULE) in inbound_pairs
    assert ("fastmcp", InboundKind.MCP_SERVER) in inbound_pairs
    assert ("litellm", OutboundKind.LLM_INFERENCE) in outbound_pairs


def test_build_interfaces_keeps_unmapped_feature_as_internal() -> None:
    features = [
        {
            "library": "custom",
            "feature_key": "unknown_feature",
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
    assert interfaces.internal_constructs[0].kind == "unknown_feature"
