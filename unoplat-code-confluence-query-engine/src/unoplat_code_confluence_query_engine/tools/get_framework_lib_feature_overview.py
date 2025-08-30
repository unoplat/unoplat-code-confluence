"""Tool for retrieving framework and library feature overview from Neo4j knowledge graph."""

from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_ai import ModelRetry, RunContext
from unoplat_code_confluence_commons.base_models.engine_models import TargetLevel

from unoplat_code_confluence_query_engine.db.neo4j.framework_overview_repository import (
    db_check_codebase_exists,
    db_get_framework_with_features,
    db_list_framework_libraries,
)
from unoplat_code_confluence_query_engine.models.agent_dependencies import (
    AgentDependencies,
)


class FeatureUsageLocation(BaseModel):
    """Represents a single location where a framework feature is used."""

    file_path: str = Field(
        ..., description="Absolute path to the file using the feature"
    )
    # start_line: int = Field(..., description="Starting line number (1-indexed)")
    # end_line: int = Field(..., description="Ending line number (1-indexed)")


class FeatureDetail(BaseModel):
    """Complete information about a framework feature including all its usage locations."""

    feature_key: str = Field(
        ..., description="Unique identifier for the feature (e.g., 'fastapi.APIRouter')"
    )
    # target_level: TargetLevel = Field(
    #     ..., description="Granularity level (function or class)"
    # )
    description: Optional[str] = Field(
        None, description="Human-readable description of the feature"
    )
    startpoint: bool = Field(
        default=False,
        description="Whether this feature represents an application entry point",
    )
    usages: List[FeatureUsageLocation] = Field(
        default_factory=list, description="All locations where this feature is used"
    )


class FrameworkSummary(BaseModel):
    """Summary of a framework/library with all its detected features."""

    library: str = Field(..., description="Library/framework name (e.g., 'fastapi')")
    total_usages: int = Field(
        default=0, description="Total count of feature usages across all files"
    )
    features: List[FeatureDetail] = Field(
        default_factory=list, description="All features detected for this framework"
    )


def _transform_framework_data(framework_data: dict) -> FrameworkSummary:
    """Transform raw Neo4j data into FrameworkSummary model.

    Args:
        framework_data: Dictionary containing framework data from Neo4j query.

    Returns:
        FrameworkSummary object with transformed usage data and feature details.
    """
    features = []
    total_usages = 0

    for feat_data in framework_data.get("features", []):
        # Parse target_level enum
        target_level_str = feat_data.get("target_level", "function")
        try:
            target_level = TargetLevel(target_level_str.lower())
        except (ValueError, AttributeError):
            target_level = TargetLevel.FUNCTION

        # Transform usage locations
        usages = [
            FeatureUsageLocation(
                file_path=usage["file_path"],
            )
            for usage in feat_data.get("usages", [])
            if usage.get("file_path")
        ]

        total_usages += len(usages)

        features.append(
            FeatureDetail(
                feature_key=feat_data["feature_key"],
                description=feat_data.get("description"),
                startpoint=bool(feat_data.get("startpoint", False)),
                usages=usages,
            )
        )

    return FrameworkSummary(
        library=framework_data["library"],
        total_usages=total_usages,
        features=features,
    )


async def get_framework_lib_feature_overview(
    ctx: RunContext[AgentDependencies],
    # framework_filter: Optional[str] = None,
) -> List[FrameworkSummary]:
    """Get framework and library feature overview for the current codebase.

    This tool retrieves comprehensive information about frameworks/libraries used in the codebase,
    including their features and exact usage locations with line numbers.

    Returns:
        List of FrameworkSummary objects containing framework features and usage locations.

    Raises:
        ModelRetry: If codebase not found in knowledge graph or other retrieval errors.
    """
    # Get codebase path from agent dependencies
    codebase_path = ctx.deps.codebase_metadata.codebase_path

    try:
        # Check if codebase exists (db-layer)
        exists = await db_check_codebase_exists(
            ctx.deps.neo4j_conn_manager, codebase_path
        )

        if not exists:
            raise ModelRetry(
                f"Codebase not found in knowledge graph: {codebase_path}. "
                "Please ensure the codebase has been ingested."
            )

        # If filtering for specific framework
        # if framework_filter:
        #     framework_data = await db_get_framework_with_features(
        #         ctx.deps.neo4j_conn_manager,
        #         codebase_path,
        #         framework_filter,
        #     )
        #     if not framework_data.get("features"):
        #         return []
        #     return [_transform_framework_data(framework_data)]

        # Get all frameworks (db-layer)
        frameworks = await db_list_framework_libraries(
            ctx.deps.neo4j_conn_manager, codebase_path
        )

        if not frameworks:
            return []

        # Fetch details for each framework
        results: List[FrameworkSummary] = []
        for library in frameworks:
            framework_data = await db_get_framework_with_features(
                ctx.deps.neo4j_conn_manager,
                codebase_path,
                library,
            )
            summary = _transform_framework_data(framework_data)
            if summary.total_usages > 0:
                results.append(summary)

        return results

    except ModelRetry:
        raise
    except Exception as e:
        raise ModelRetry(
            f"Unexpected error retrieving framework overview for {codebase_path}: {str(e)}. "
            "Please check the Neo4j connection and try again."
        )
    finally:
        await ctx.deps.neo4j_conn_manager.close()
