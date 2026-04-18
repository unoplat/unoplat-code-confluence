from __future__ import annotations

CALL_EXPRESSION_VALIDATOR_CANDIDATE_FIELDS: tuple[str, ...] = (
    "identity",
    "concept",
    "match_confidence",
    "validation_status",
    "match_text",
    "evidence_json",
    "base_confidence",
    "notes",
    "construct_query",
    "absolute_paths",
)

CALL_EXPRESSION_VALIDATOR_IDENTITY_FIELDS: tuple[str, ...] = (
    "file_path",
    "feature_language",
    "feature_library",
    "feature_capability_key",
    "feature_operation_key",
    "start_line",
    "end_line",
)

CALL_EXPRESSION_VALIDATOR_EVIDENCE_FIELDS: tuple[str, ...] = (
    "concept",
    "source",
    "match_confidence",
    "call_match_kind",
    "matched_absolute_path",
    "matched_alias",
    "call_match_policy_version",
    "callee",
    "args_text",
    "validator",
)

DEPENDENCY_OVERVIEW_ARTIFACT = "dependencies_overview.md"
BUSINESS_LOGIC_REFERENCES_ARTIFACT = "business_logic_references.md"
APP_INTERFACES_ARTIFACT = "app_interfaces.md"

DEVELOPMENT_WORKFLOW_CONSOLE_TOOLSET_ID = "console__development_workflow_guide"
DEVELOPMENT_WORKFLOW_EXA_TOOLSET_ID = "exa__development_workflow_guide"
DEPENDENCY_GUIDE_EXA_TOOLSET_ID = "exa__dependency_guide"
CALL_EXPRESSION_VALIDATOR_EXA_TOOLSET_ID = "exa__call_expression_validator"

TS_MONOREPO_DYNAMIC_TOOLSET_ID = "ts_monorepo_dynamic__development_workflow_guide"
TS_MONOREPO_TOOLSET_ID = "ts_monorepo__development_workflow_guide"
