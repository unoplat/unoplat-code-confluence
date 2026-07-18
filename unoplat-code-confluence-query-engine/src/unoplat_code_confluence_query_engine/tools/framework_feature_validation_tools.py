from __future__ import annotations

from loguru import logger
from pydantic_ai import ModelRetry, RunContext

from unoplat_code_confluence_query_engine.db.postgres.code_confluence_framework_repository import (
    db_upsert_discovered_framework_feature_usages,
)
from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    DiscoveredFrameworkFeatureUsagesUpsertRequest,
    DiscoveredFrameworkFeatureUsagesUpsertResult,
)
from unoplat_code_confluence_query_engine.models.runtime.agent_dependencies import (
    AgentDependencies,
)


async def upsert_discovered_framework_feature_usages(
    ctx: RunContext[AgentDependencies],
    request: DiscoveredFrameworkFeatureUsagesUpsertRequest,
) -> DiscoveredFrameworkFeatureUsagesUpsertResult:
    """Persist proven usage spans for one exact catalog framework operation.

    Args:
        request: Proven usage spans and final confidences for the target operation.

    Returns:
        Counts of usage rows created and updated.
    """
    try:
        result = await db_upsert_discovered_framework_feature_usages(
            codebase_path=ctx.deps.codebase_metadata.codebase_path,
            request=request,
        )
    except ValueError as exc:
        raise ModelRetry(str(exc)) from exc
    logger.info(
        "[framework_feature_validation_tools] Persisted discovered usages for {}:{}:{} created={} updated={}",
        request.target_feature_identity.feature_language,
        request.target_feature_identity.feature_library,
        request.target_feature_identity.feature_key,
        result.created_count,
        result.updated_count,
    )
    return result
