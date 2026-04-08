from __future__ import annotations

from unoplat_code_confluence_commons.base_models import ValidationStatus

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureUsageIdentity,
    FrameworkFeatureValidationCandidate,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.agents.user_prompts.build_user_prompt_call_expression_validator import (
    build_call_expression_validator_instructions,
    build_call_expression_validator_prompt,
)


def _build_candidate() -> FrameworkFeatureValidationCandidate:
    return FrameworkFeatureValidationCandidate(
        identity=FrameworkFeatureUsageIdentity(
            file_path="/tmp/repo/src/app.ts",
            feature_language="typescript",
            feature_library="zustand",
            feature_key="store_definition",
            start_line=10,
            end_line=12,
        ),
        concept="CallExpression",
        match_confidence=0.69,
        validation_status=ValidationStatus.PENDING,
        match_text="createStore(() => ({}))",
        evidence_json={
            "concept": "CallExpression",
            "source": "tree_sitter",
            "match_confidence": 0.69,
            "call_match_kind": "symbol_exact",
            "matched_absolute_path": "zustand/vanilla.createStore",
            "matched_alias": "createStore",
            "call_match_policy_version": "v1_import_bound",
            "callee": "createStore",
            "args_text": "() => ({})",
        },
        base_confidence=0.69,
        notes="Confirm the call resolves to a zustand import, not an unrelated local helper.",
        construct_query={"call_name_regex": "^(create|createStore)$"},
        absolute_paths=["zustand.create", "zustand/vanilla.createStore"],
    )


def test_call_expression_validator_instructions_are_metadata_aware() -> None:
    instructions = build_call_expression_validator_instructions(
        docs_instruction="Read official docs first.",
        docs_workflow="- Search docs\n- Verify API shape",
    )

    assert "Candidate payload fields provided to you" in instructions
    assert "identity, concept, match_confidence, validation_status" in instructions
    assert "call_match_kind" in instructions
    assert "matched_absolute_path" in instructions
    assert "matched_alias" in instructions
    assert "call_match_policy_version" in instructions
    assert "1. Read official docs first." in instructions
    assert (
        "Compare official docs expectations against candidate metadata" in instructions
    )
    assert "gap analysis" in instructions


def test_call_expression_validator_prompt_describes_docs_first_review_order() -> None:
    prompt = build_call_expression_validator_prompt(_build_candidate())

    assert "Candidate payload guide:" in prompt
    assert "expected CallExpression evidence_json keys" in prompt
    assert "Review official framework documentation first" in prompt
    assert (
        "Compare docs expectations against candidate metadata/evidence_json" in prompt
    )
    assert "Record gaps/mismatches before deciding" in prompt
    assert (
        "documentation findings, metadata review, local code findings, gap analysis"
        in prompt
    )
    assert '"call_match_kind": "symbol_exact"' in prompt
    assert '"matched_absolute_path": "zustand/vanilla.createStore"' in prompt
