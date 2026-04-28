from __future__ import annotations

from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_framework_repository import (
    db_set_framework_feature_validation_status,
    db_upsert_framework_feature_validation_evidence,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureValidationEvidenceUpsertRequest,
    FrameworkFeatureValidationEvidenceUpsertResult,
    FrameworkFeatureValidationStatusTransitionRequest,
    FrameworkFeatureValidationStatusTransitionResult,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


async def upsert_framework_feature_validation_evidence(
    ctx: RunContext[AgentDependencies],
    request: FrameworkFeatureValidationEvidenceUpsertRequest,
) -> FrameworkFeatureValidationEvidenceUpsertResult:
    """Persist validator evidence and confidence for one framework-usage row.

    Args:
        request: Typed validation payload containing usage-row identity,
            validator decision, final confidence, evidence payload, and optional
            corrected file/span location and match_text for `correct`
            decisions on the same usage row.

    Returns:
        Typed summary describing whether the source row was updated and what
        the row's current identity is after any in-place location correction.
    """
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    try:
        result = await db_upsert_framework_feature_validation_evidence(
            codebase_path=codebase_path,
            request=request,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc

    logger.info(
        "[framework_feature_validation_tools] Evidence upserted for {}:{}:{}:{}:{}-{} decision={}",
        request.identity.feature_language,
        request.identity.feature_library,
        request.identity.feature_key,
        request.identity.file_path,
        request.identity.start_line,
        request.identity.end_line,
        request.decision.value,
    )

    return result


async def set_framework_feature_validation_status(
    ctx: RunContext[AgentDependencies],
    request: FrameworkFeatureValidationStatusTransitionRequest,
) -> FrameworkFeatureValidationStatusTransitionResult:
    """Apply a guarded validation-status transition for one usage row.

    Args:
        request: Typed transition request containing usage-row identity,
            target status, and optional expected current status for optimistic
            concurrency checks.

    Returns:
        Typed transition result with previous/current status and update mode
        (`updated` vs `no_op`).
    """
    codebase_path = ctx.deps.codebase_metadata.codebase_path
    try:
        result = await db_set_framework_feature_validation_status(
            codebase_path=codebase_path,
            request=request,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc

    logger.info(
        "[framework_feature_validation_tools] Status transition {} -> {} for {}:{}:{}:{}:{}-{}",
        result.previous_status.value,
        result.current_status.value,
        request.identity.feature_language,
        request.identity.feature_library,
        request.identity.feature_key,
        request.identity.file_path,
        request.identity.start_line,
        request.identity.end_line,
    )

    return result
