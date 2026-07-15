from __future__ import annotations

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    CallExpressionDiscoveryOperation,
    CallExpressionDiscoveryTarget,
)


def build_call_expression_discoverer_instructions() -> str:
    """Build instructions for one operation-scoped provenance discovery run."""
    return (
        "Inspect the repository for this one supplied catalog CallExpression operation only.\n"
        "Absolute paths, construct-query metadata, and existing spans are optional hints; an empty span list must not skip discovery.\n\n"
        "Rules\n"
        "- Search only inside the supplied codebase path. Trace related instances through assignments, exports, imports, aliases, attributes, and dependency injection.\n"
        "- Accept only proven final calls whose receiver resolves to the configured framework value and whose callee matches this operation. Reject constructors, factories, configuration calls, lookalike receivers, mocks, repositories, routers, maps, caches, and helpers.\n"
        "- Set final_confidence for every proven file/span. Do not write or infer evidence_json.\n"
        "- Call upsert_discovered_framework_feature_usages at most once, with the supplied exact FrameworkFeatureIdentity and all distinct proven spans. Do not use sibling operations.\n"
        "- Supplied spans that cannot be proven remain unchanged (pending/needs_review).\n"
        "- If no span is proven, do not call the tool and return created_count=0 and updated_count=0. Otherwise return the exact tool result."
    )


def build_call_expression_discoverer_prompt(
    codebase_path: str,
    capability: CallExpressionDiscoveryTarget,
    operation: CallExpressionDiscoveryOperation,
) -> str:
    """Build an isolated discovery request for one catalog operation."""
    target = {
        "feature_language": capability.feature_language,
        "feature_library": capability.feature_library,
        "feature_capability_key": capability.feature_capability_key,
        "feature_operation_key": operation.feature_operation_key,
    }
    return (
        "Discover proven final CallExpression usages for exactly this operation.\n\n"
        f"Codebase path: {codebase_path}\n"
        "All repository inspection must stay inside this codebase path.\n\n"
        "Exact target FrameworkFeatureIdentity JSON:\n"
        f"{target}\n\n"
        "Operation metadata and optional hints JSON:\n"
        f"{operation.model_dump_json(indent=2)}"
    )
