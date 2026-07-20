"""Focused contracts for CallExpression operation discovery."""

from __future__ import annotations

from unoplat_code_confluence_commons.base_models import Concept, ValidationStatus

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_framework_repository import (
    LOW_CONFIDENCE_DISCOVERY_THRESHOLD,
    _should_include_in_app_interface_mapping,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionDiscoveryExistingSpan,
    CallExpressionDiscoveryOperation,
    CallExpressionDiscoveryTarget,
    CallExpressionFeatureDefinition,
    DiscoveredFrameworkFeatureUsageSpan,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_discoverer import (
    build_call_expression_discoverer_prompt,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.catalog import (
    AGENT_BUILDERS,
    AgentType,
)


def _target() -> CallExpressionDiscoveryTarget:
    definition = CallExpressionFeatureDefinition(
        concept=Concept.CALL_EXPRESSION,
        description="Fetch a resource",
        base_confidence=0.69,
    )
    return CallExpressionDiscoveryTarget(
        feature_language="python",
        feature_library="httpx",
        feature_capability_key="http_client",
        operations=[
            CallExpressionDiscoveryOperation(
                feature_operation_key="get",
                definition=definition,
                absolute_paths=["httpx.Client"],
            ),
            CallExpressionDiscoveryOperation(
                feature_operation_key="post",
                definition=definition,
                existing_spans=[
                    CallExpressionDiscoveryExistingSpan(
                        file_path="/repo/client.py",
                        start_line=8,
                        end_line=8,
                        match_confidence=0.2,
                        validation_status=ValidationStatus.PENDING,
                    )
                ],
            ),
        ],
    )


def test_target_groups_multiple_operations_and_keeps_empty_span_operation() -> None:
    target = _target()
    assert [operation.feature_operation_key for operation in target.operations] == [
        "get",
        "post",
    ]
    assert target.operations[0].existing_spans == []
    assert LOW_CONFIDENCE_DISCOVERY_THRESHOLD == 0.70


def test_prompt_isolated_to_one_operation_and_keeps_existing_hints() -> None:
    target = _target()
    prompt = build_call_expression_discoverer_prompt(
        "/repo", target, target.operations[1]
    )
    assert "'feature_operation_key': 'post'" in prompt
    assert '"feature_operation_key": "get"' not in prompt
    assert "/repo/client.py" in prompt


def test_discovered_span_requires_exact_final_confidence() -> None:
    span = DiscoveredFrameworkFeatureUsageSpan(
        file_path="/repo/client.py",
        start_line=3,
        end_line=3,
        match_text="client.get('/')",
        final_confidence=0.91,
    )
    assert span.final_confidence == 0.91


def test_call_expression_interface_inclusion_is_completed_only() -> None:
    assert not _should_include_in_app_interface_mapping(
        concept=Concept.CALL_EXPRESSION.value,
        validation_status=ValidationStatus.PENDING,
    )
    assert _should_include_in_app_interface_mapping(
        concept=Concept.CALL_EXPRESSION.value,
        validation_status=ValidationStatus.COMPLETED,
    )


def test_call_expression_discoverer_is_assembled_without_validator() -> None:
    agent_values = {agent.value for agent in AgentType}
    assert "call_expression_discoverer" in agent_values
    assert "call_expression_validator" not in agent_values
    assert all("validator" not in builder.__name__ for builder in AGENT_BUILDERS.values())
