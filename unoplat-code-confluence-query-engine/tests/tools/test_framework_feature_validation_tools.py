"""Unit tests for framework feature validation tool wrappers."""

from __future__ import annotations

from unittest.mock import MagicMock

from pydantic_ai import ModelRetry
import pytest
from unoplat_code_confluence_commons.base_models import ValidationStatus

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureUsageIdentity,
    FrameworkFeatureValidationDecision,
    FrameworkFeatureValidationEvidenceUpsertRequest,
    FrameworkFeatureValidationEvidenceUpsertResult,
    FrameworkFeatureValidationStatusTransitionRequest,
    FrameworkFeatureValidationStatusTransitionResult,
)
from unoplat_code_confluence_query_engine.models.repository.repository_ruleset_metadata import (
    CodebaseMetadata,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)
from unoplat_code_confluence_query_engine.tools import (
    framework_feature_validation_tools,
)


def _make_run_context(codebase_path: str) -> MagicMock:
    metadata = CodebaseMetadata(
        codebase_name="validator-codebase",
        codebase_path=codebase_path,
        codebase_programming_language="python",
        codebase_package_manager="uv",
    )
    deps = AgentDependencies(
        repository_qualified_name="owner/repo",
        codebase_metadata=metadata,
        repository_workflow_run_id="workflow-run-001",
        codebase_workflow_run_id="codebase-workflow-run-001",
        agent_name="call_expression_validator",
    )
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


def _build_identity() -> FrameworkFeatureUsageIdentity:
    return FrameworkFeatureUsageIdentity(
        file_path="/tmp/test-codebase/app.py",
        feature_language="python",
        feature_library="validatorlib",
        feature_capability_key="database",
        feature_operation_key="db_sql",
        start_line=10,
        end_line=12,
    )


@pytest.mark.asyncio
async def test_upsert_tool_wraps_repository_errors_as_model_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _make_run_context("/tmp/test-codebase")

    async def fake_upsert(*, codebase_path, request):
        del codebase_path, request
        raise ValueError("row not found")

    monkeypatch.setattr(
        framework_feature_validation_tools,
        "db_upsert_framework_feature_validation_evidence",
        fake_upsert,
    )

    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_identity(),
        decision=FrameworkFeatureValidationDecision.CONFIRM,
        final_confidence=0.74,
        evidence_json={"reason": "validate"},
    )

    with pytest.raises(ModelRetry, match="row not found"):
        await framework_feature_validation_tools.upsert_framework_feature_validation_evidence(
            ctx=ctx,
            request=request,
        )


@pytest.mark.asyncio
async def test_status_tool_wraps_repository_errors_as_model_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _make_run_context("/tmp/test-codebase")

    async def fake_status(*, codebase_path, request):
        del codebase_path, request
        raise ValueError("invalid transition")

    monkeypatch.setattr(
        framework_feature_validation_tools,
        "db_set_framework_feature_validation_status",
        fake_status,
    )

    request = FrameworkFeatureValidationStatusTransitionRequest(
        identity=_build_identity(),
        target_status=ValidationStatus.COMPLETED,
    )

    with pytest.raises(ModelRetry, match="invalid transition"):
        await (
            framework_feature_validation_tools.set_framework_feature_validation_status(
                ctx=ctx,
                request=request,
            )
        )


@pytest.mark.asyncio
async def test_upsert_tool_returns_typed_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _make_run_context("/tmp/test-codebase")

    async def fake_upsert(*, codebase_path, request):
        assert codebase_path == "/tmp/test-codebase"
        assert request.identity.feature_capability_key == "database"
        assert request.identity.feature_operation_key == "db_sql"
        assert request.decision == FrameworkFeatureValidationDecision.CONFIRM
        return FrameworkFeatureValidationEvidenceUpsertResult(
            source_row_updated=True,
            current_identity=request.identity,
        )

    monkeypatch.setattr(
        framework_feature_validation_tools,
        "db_upsert_framework_feature_validation_evidence",
        fake_upsert,
    )

    request = FrameworkFeatureValidationEvidenceUpsertRequest(
        identity=_build_identity(),
        decision=FrameworkFeatureValidationDecision.CONFIRM,
        final_confidence=0.88,
        evidence_json={"reason": "match confirmed"},
    )

    result = await framework_feature_validation_tools.upsert_framework_feature_validation_evidence(
        ctx=ctx,
        request=request,
    )

    assert isinstance(result, FrameworkFeatureValidationEvidenceUpsertResult)
    assert result.source_row_updated is True
    assert result.current_identity == request.identity


@pytest.mark.asyncio
async def test_status_tool_returns_typed_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _make_run_context("/tmp/test-codebase")

    async def fake_status(*, codebase_path, request):
        assert codebase_path == "/tmp/test-codebase"
        assert request.target_status == ValidationStatus.COMPLETED
        return FrameworkFeatureValidationStatusTransitionResult(
            status="updated",
            previous_status=ValidationStatus.PENDING,
            current_status=ValidationStatus.COMPLETED,
        )

    monkeypatch.setattr(
        framework_feature_validation_tools,
        "db_set_framework_feature_validation_status",
        fake_status,
    )

    request = FrameworkFeatureValidationStatusTransitionRequest(
        identity=_build_identity(),
        target_status=ValidationStatus.COMPLETED,
    )

    result = await framework_feature_validation_tools.set_framework_feature_validation_status(
        ctx=ctx,
        request=request,
    )

    assert isinstance(result, FrameworkFeatureValidationStatusTransitionResult)
    assert result.status == "updated"
    assert result.current_status == ValidationStatus.COMPLETED
