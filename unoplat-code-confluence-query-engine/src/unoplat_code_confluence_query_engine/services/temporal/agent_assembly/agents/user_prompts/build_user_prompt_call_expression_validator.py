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
        "Available local repository inspection tools in this run: ls, read_file, glob, grep.\n"
        "Use ls/glob to discover relevant files, read_file to inspect exact spans and nearby context, and grep to trace symbols/imports/usages across the codebase.\n\n"
        "Candidate payload fields provided to you:\n"
        f"- Top-level fields: {candidate_fields}.\n"
        f"- identity fields: {identity_fields}.\n"
        "- evidence_json contains detector/runtime evidence and may be absent or partial.\n"
        f"- When evidence_json comes from CallExpression detection, it may include: {evidence_fields}.\n"
        "- Treat detector metadata as hints to verify, not as proof by itself.\n\n"
        "<local_provenance_validation>\n"
        "Your primary task is to validate the candidate's local provenance and span.\n"
        "Use the readonly console capability to inspect the repository filesystem with ls, read_file, glob, and grep.\n"
        "Confirm that the reported file_path exists, that start_line/end_line bracket a real call expression, and that the match_text aligns with what is actually at that location.\n"
        "Check import bindings and alias chains to verify the call resolves to the claimed library/capability/operation. If it appears to resolve to a different feature identity, do not rewrite capability/operation keys here; choose reject or needs_review instead.\n"
        "</local_provenance_validation>\n\n"
        "<docs_as_supporting_evidence>\n"
        "After establishing local provenance, verify the claimed framework API usage against official documentation using the available external search tools.\n"
        "If Exa toolsets are present in this run, prefer Exa for broad discovery. Still use web search and web fetch for targeted lookup and page retrieval even when Exa is absent.\n"
        "Prefer official or vendor-authored sources.\n"
        "Use documentation to confirm API shape, argument expectations, and expected behavior — not as the primary decision driver.\n"
        "Record gaps, mismatches, and uncertainty explicitly.\n"
        "Only choose confirm, reject, or correct when the combined evidence supports that decision with confidence > 0.70.\n"
        "If local provenance is weak or documentation cannot be verified, choose the conservative path: set decision=needs_review and target_status=needs_review.\n"
        "</docs_as_supporting_evidence>\n\n"
        "Required process:\n"
        "1. Validate local provenance.\n"
        "2. Expand nearby symbol/object evidence from the local codebase.\n"
        f"3. {required_docs_instruction}\n"
        f"{docs_workflow_block}"
        "4. Compare your findings against candidate metadata and evidence_json.\n"
        "5. Identify gaps and mismatches explicitly before deciding.\n"
        "6. Persist evidence/confidence with upsert_framework_feature_validation_evidence.\n"
        "7. Persist status transition with set_framework_feature_validation_status.\n"
        "8. Return output contract only after write operations complete.\n\n"
        "Evidence payload expectations for upsert_framework_feature_validation_evidence:\n"
        "- Include structured findings for local provenance review (file existence, span accuracy, import resolution), documentation review, metadata review, gap analysis, and final rationale.\n"
        "- Record which metadata fields were present/missing and whether they aligned with local code and official docs.\n"
        "- Record why provenance is sufficient or insufficient for confirm/reject/correct/needs_review.\n"
        "- Record span rationale: does the detected span (start_line..end_line) correspond to the actual call expression? If not, explain the mismatch.\n"
        "- If correcting location: explain why the corrected file_path/start_line/end_line is trustworthy (e.g., verified by reading the file at the corrected span).\n"
        "- If providing corrected_match_text: explain why it is the right source snippet (e.g., actual source text read from the corrected span).\n\n"
        "Tool workflow example (confirm path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='confirm', final_confidence, evidence_json}.\n"
        "- Use the returned current_identity when calling set_framework_feature_validation_status with request {identity=current_identity, target_status='completed'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Tool workflow example (correct path — correcting source location and/or match text on the same feature row):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='correct', final_confidence, evidence_json, corrected_file_path (if location differs), corrected_start_line (if location differs), corrected_end_line (if location differs), corrected_match_text (if source text differs)}.\n"
        "- The capability key, operation key, language, and library must stay the same; correct is only for better source pinpointing on the existing usage row.\n"
        "- Use the returned current_identity when calling set_framework_feature_validation_status with request {identity=current_identity, target_status='completed'}.\n"
        "- Return CallExpressionValidationAgentOutput with the source identity plus any corrected fields.\n\n"
        "Tool workflow example (needs_review path):\n"
        "- Call upsert_framework_feature_validation_evidence with request {identity, decision='needs_review', final_confidence, evidence_json}.\n"
        "- Use the returned current_identity when calling set_framework_feature_validation_status with request {identity=current_identity, target_status='needs_review'}.\n"
        "- Return CallExpressionValidationAgentOutput for the same identity.\n\n"
        "Decision policy:\n"
        "- confirm/reject/correct => target_status must be completed\n"
        "- needs_review => target_status must be needs_review\n"
        "- correct is only for correcting file_path/start_line/end_line and/or match_text for the same claimed feature identity\n"
        "- if the usage appears to belong to a different capability/operation/library than the row claims, do not rewrite keys; use reject or needs_review instead"
    )


def build_call_expression_validator_prompt(
    codebase_path: str,
    candidate: FrameworkFeatureValidationCandidate,
) -> str:
    return (
        "Validate this low-confidence CallExpression candidate for app-interface mapping.\n"
        "Apply the validator instructions to this candidate.\n\n"
        f"Codebase path: {codebase_path}\n"
        "Any filesystem inspection and any corrected_file_path must stay within this codebase path.\n"
        "If evidence appears to point to a different codebase, do not retarget the row there; use reject or needs_review instead.\n\n"
        "Candidate payload JSON:\n"
        f"{candidate.model_dump_json(indent=2)}"
    )
