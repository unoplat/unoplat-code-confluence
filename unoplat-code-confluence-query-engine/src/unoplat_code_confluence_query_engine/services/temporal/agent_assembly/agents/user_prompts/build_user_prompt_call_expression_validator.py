from __future__ import annotations

from unoplat_code_confluence_query_engine.models.repository.framework_feature_validation_models import (
    FrameworkFeatureValidationCandidate,
)
from unoplat_code_confluence_query_engine.services.temporal.agent_assembly.constants import (
    CALL_EXPRESSION_VALIDATOR_CANDIDATE_FIELDS,
    CALL_EXPRESSION_VALIDATOR_EVIDENCE_FIELDS,
    CALL_EXPRESSION_VALIDATOR_IDENTITY_FIELDS,
)


def format_validator_field_list(fields: tuple[str, ...]) -> str:
    return ", ".join(fields)


def build_call_expression_validator_instructions(
    docs_instruction: str | None = None,
    docs_workflow: str | None = None,
) -> str:
    candidate_fields = format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_CANDIDATE_FIELDS
    )
    identity_fields = format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_IDENTITY_FIELDS
    )
    evidence_fields = format_validator_field_list(
        CALL_EXPRESSION_VALIDATOR_EVIDENCE_FIELDS
    )
    required_docs_instruction = (
        docs_instruction
        or "Verify the claimed API behavior against official documentation."
    )
    docs_workflow_block = ""
    if docs_workflow:
        docs_workflow_block = f"{docs_workflow}\n"

    return (
        "You validate one low-confidence CallExpression usage candidate at a time.\n"
        "Return a strict structured decision with auditable evidence.\n\n"
        "Candidate payload fields provided to you:\n"
        f"- Top-level fields: {candidate_fields}.\n"
        f"- identity fields: {identity_fields}.\n"
        "- evidence_json contains detector/runtime evidence and may be absent or partial.\n"
        f"- When evidence_json comes from CallExpression detection, it may include: {evidence_fields}.\n"
        "- Treat detector metadata as hints to verify, not as proof by itself.\n\n"
        "<official_docs_validation>\n"
        "Verify the claimed framework API usage against official documentation using the available documentation/search capability, then compare that evidence with the candidate metadata and the local code context.\n"
        "Prefer official or vendor-authored sources.\n"
        "Record gaps, mismatches, and uncertainty explicitly.\n"
        "Only choose confirm, reject, or correct when the combined evidence supports that decision with confidence > 0.70.\n"
        "If official documentation cannot be verified, remains ambiguous, or confidence is <= 0.70, choose the conservative unresolved path: set decision=needs_review and target_status=needs_review.\n"
        "</official_docs_validation>\n\n"
        "Required process:\n"
        f"1. {required_docs_instruction}\n"
        f"{docs_workflow_block}"
        "2. Read local file context around the candidate span using read_file_content.\n"
        "3. Expand nearby symbol/object evidence using search_across_codebase.\n"
        "4. Compare official docs expectations against candidate metadata, evidence_json, and local code evidence.\n"
        "5. Explicitly identify gaps/mismatches before deciding (for example: import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance, unsupported argument shape, or docs mismatch).\n"
        "6. Persist evidence/confidence with upsert_framework_feature_validation_evidence.\n"
        "7. Persist status transition with set_framework_feature_validation_status.\n"
        "8. Return output contract only after write operations complete.\n\n"
        "Evidence payload expectations for upsert_framework_feature_validation_evidence:\n"
        "- Include structured findings for documentation review, metadata review, local code review, gap analysis, and final rationale.\n"
        "- Record which metadata fields were present/missing and whether they aligned with official docs.\n"
        "- Record why provenance is sufficient or insufficient for confirm/reject/correct/needs_review.\n\n"
        "Tool workflow example (confirm path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='confirm', final_confidence, evidence_json}.\n"
        "- Then call set_framework_feature_validation_status with request {identity, target_status='completed'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Tool workflow example (needs_review path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='needs_review', final_confidence, evidence_json}.\n"
        "- Then call set_framework_feature_validation_status with request {identity, target_status='needs_review'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Decision policy:\n"
        "- confirm/reject/correct => target_status must be completed\n"
        "- needs_review => target_status must be needs_review\n"
        "- correct requires updated_feature_capability_key and updated_feature_operation_key different from the source identity"
    )


def build_call_expression_validator_prompt(
    candidate: FrameworkFeatureValidationCandidate,
) -> str:
    candidate_fields = (
        "identity, concept, match_confidence, validation_status, match_text, "
        "evidence_json, base_confidence, notes, construct_query, absolute_paths"
    )
    identity_fields = (
        "file_path, feature_language, feature_library, feature_capability_key, "
        "feature_operation_key, start_line, end_line"
    )
    evidence_fields = (
        "concept, source, match_confidence, call_match_kind, matched_absolute_path, "
        "matched_alias, call_match_policy_version, callee, args_text, validator"
    )
    return (
        "Validate this low-confidence CallExpression candidate for app-interface mapping.\n"
        "You are given candidate metadata plus detector evidence to verify against official documentation and local code.\n"
        "You MUST persist writes using both validator write tools in order.\n\n"
        "Candidate payload guide:\n"
        f"- top-level fields: {candidate_fields}\n"
        f"- identity fields: {identity_fields}\n"
        "- evidence_json may be partial or absent; when present for CallExpression it commonly contains detector metadata and parsed call evidence.\n"
        f"- expected CallExpression evidence_json keys: {evidence_fields}\n\n"
        "Required review order:\n"
        "1) Review official framework documentation first and determine what the claimed API usage should look like.\n"
        "2) Compare docs expectations against candidate metadata/evidence_json and note present vs missing fields.\n"
        "3) Read local file context with read_file_content.\n"
        "4) Expand nearby symbol/object evidence with search_across_codebase.\n"
        "5) Record gaps/mismatches before deciding (for example: import-binding mismatch, alias/path mismatch, API-shape mismatch, insufficient provenance, unsupported args, or docs mismatch).\n"
        "6) Persist evidence/confidence, then persist status, then return output.\n\n"
        "Required write sequence:\n"
        "1) upsert_framework_feature_validation_evidence(request=...)\n"
        "2) set_framework_feature_validation_status(request=...)\n"
        "3) return output for the same identity\n\n"
        "When you upsert evidence_json, include documentation findings, metadata review, local code findings, gap analysis, and final rationale.\n\n"
        "Candidate payload JSON:\n"
        f"{candidate.model_dump_json(indent=2)}"
    )
