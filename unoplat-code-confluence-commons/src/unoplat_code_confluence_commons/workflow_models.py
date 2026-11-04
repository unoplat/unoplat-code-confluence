"""Workflow status and error models shared across ingestion and query engine."""

from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Dict, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class JobStatus(str, Enum):
    """Workflow execution status values matching DB CHECK constraint."""

    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    COMPLETED = "COMPLETED"
    RETRYING = "RETRYING"
    ERROR = "ERROR"  # Partial failures (some agents succeeded, some failed)
    CANCELLED = "CANCELLED"


class WorkflowErrorCode(str, Enum):
    """Stable failure codes that are safe to persist and display."""

    WORKFLOW_FAILED = "workflow_failed"
    EXECUTION_TIMED_OUT = "execution_timed_out"
    AGENT_EXECUTION_FAILED = "agent_execution_failed"
    CODEBASE_WORKFLOW_FAILED = "codebase_workflow_failed"
    MODEL_REQUEST_FAILED = "model_request_failed"
    CHECKOUT_ADMISSION_TIMED_OUT = "checkout_admission_timed_out"
    CHECKOUT_ADMISSION_DENIED = "checkout_admission_denied"
    GIT_OPERATION_FAILED = "git_operation_failed"
    GRAPH_INGESTION_FAILED = "graph_ingestion_failed"
    PACKAGE_METADATA_FAILED = "package_metadata_failed"
    PACKAGE_MANAGER_UNSUPPORTED = "package_manager_unsupported"
    WORKFLOW_STATE_INVALID = "workflow_state_invalid"
    STATUS_UPDATE_FAILED = "status_update_failed"
    AGENT_MD_TRIGGER_FAILED = "agent_md_trigger_failed"
    ARTIFACT_PUBLICATION_FAILED = "artifact_publication_failed"


WORKFLOW_ERROR_MESSAGES: Dict[WorkflowErrorCode, str] = {
    WorkflowErrorCode.WORKFLOW_FAILED: "The workflow failed.",
    WorkflowErrorCode.EXECUTION_TIMED_OUT: "A workflow step timed out.",
    WorkflowErrorCode.AGENT_EXECUTION_FAILED: "One or more agents failed.",
    WorkflowErrorCode.CODEBASE_WORKFLOW_FAILED: (
        "One or more codebase or repository agent executions failed."
    ),
    WorkflowErrorCode.MODEL_REQUEST_FAILED: "A model provider request failed.",
    WorkflowErrorCode.CHECKOUT_ADMISSION_TIMED_OUT: "Checkout admission timed out.",
    WorkflowErrorCode.CHECKOUT_ADMISSION_DENIED: "Checkout admission was denied.",
    WorkflowErrorCode.GIT_OPERATION_FAILED: "A Git operation failed.",
    WorkflowErrorCode.GRAPH_INGESTION_FAILED: "Code graph ingestion failed.",
    WorkflowErrorCode.PACKAGE_METADATA_FAILED: "Package metadata processing failed.",
    WorkflowErrorCode.PACKAGE_MANAGER_UNSUPPORTED: (
        "The package manager is missing or unsupported."
    ),
    WorkflowErrorCode.WORKFLOW_STATE_INVALID: "Required workflow state was not found.",
    WorkflowErrorCode.STATUS_UPDATE_FAILED: "A workflow status update failed.",
    WorkflowErrorCode.AGENT_MD_TRIGGER_FAILED: "Agent generation could not be started.",
    WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED: (
        "Generated artifacts could not be saved to Git."
    ),
}

# Runtime error types are only ever a lookup key. Unknown values stay generic.
WORKFLOW_ERROR_TYPE_CODES: Dict[str, WorkflowErrorCode] = {
    "TimeoutError": WorkflowErrorCode.EXECUTION_TIMED_OUT,
    "AgentExecutionError": WorkflowErrorCode.AGENT_EXECUTION_FAILED,
    "CodebaseWorkflowError": WorkflowErrorCode.CODEBASE_WORKFLOW_FAILED,
    "ModelHTTPError": WorkflowErrorCode.MODEL_REQUEST_FAILED,
    "ModelAPIError": WorkflowErrorCode.MODEL_REQUEST_FAILED,
    "FallbackExceptionGroup": WorkflowErrorCode.MODEL_REQUEST_FAILED,
    "UnexpectedModelBehavior": WorkflowErrorCode.MODEL_REQUEST_FAILED,
    "CheckoutAdmissionTimeout": WorkflowErrorCode.CHECKOUT_ADMISSION_TIMED_OUT,
    "CheckoutAdmissionDenied": WorkflowErrorCode.CHECKOUT_ADMISSION_DENIED,
    "CheckoutAdmissionError": WorkflowErrorCode.CHECKOUT_ADMISSION_DENIED,
    "GIT_ACTIVITY_ERROR": WorkflowErrorCode.GIT_OPERATION_FAILED,
    "GithubHelperError": WorkflowErrorCode.GIT_OPERATION_FAILED,
    "GRAPH_INGESTION_ERROR": WorkflowErrorCode.GRAPH_INGESTION_FAILED,
    "PACKAGE_METADATA_ERROR": WorkflowErrorCode.PACKAGE_METADATA_FAILED,
    "PACKAGE_METADATA_INGESTION_ERROR": WorkflowErrorCode.PACKAGE_METADATA_FAILED,
    "PACKAGE_PARSER_ERROR": WorkflowErrorCode.PACKAGE_METADATA_FAILED,
    "PACKAGE_MANAGER_NOT_SPECIFIED_ERROR": (
        WorkflowErrorCode.PACKAGE_MANAGER_UNSUPPORTED
    ),
    "UNSUPPORTED_PACKAGE_MANAGER_ERROR": WorkflowErrorCode.PACKAGE_MANAGER_UNSUPPORTED,
    "ParentWorkflowRunNotFound": WorkflowErrorCode.WORKFLOW_STATE_INVALID,
    "CodebaseConfigNotFound": WorkflowErrorCode.WORKFLOW_STATE_INVALID,
    "AgentMdPrMissingRunContextError": WorkflowErrorCode.WORKFLOW_STATE_INVALID,
    "CodebaseStatusUpdateError": WorkflowErrorCode.STATUS_UPDATE_FAILED,
    "AGENT_MD_TRIGGER_NETWORK_ERROR": WorkflowErrorCode.AGENT_MD_TRIGGER_FAILED,
    "AGENT_MD_TRIGGER_HTTP_ERROR": WorkflowErrorCode.AGENT_MD_TRIGGER_FAILED,
    "AgentMdPrError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrNotFoundError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrConfigurationError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrAuthError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrInternalError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrGithubError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrConflictError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrStaleArtifactError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
    "AgentMdPrMissingArtifactError": WorkflowErrorCode.ARTIFACT_PUBLICATION_FAILED,
}

MAX_REPORTED_FAILURES = 32
_MAX_CAUSE_DEPTH = 8
_MAX_AGENT_NAME_LENGTH = 80
_MAX_CODEBASE_NAME_LENGTH = 255
_AGENT_NAME_CHARACTERS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789_")
_CODEBASE_NAME_CHARACTERS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-/"
)


def _error_code_for_type(error_type: object) -> Optional[WorkflowErrorCode]:
    """Return the allowlisted code for a runtime error type, if there is one."""
    if not isinstance(error_type, str):
        return None
    return WORKFLOW_ERROR_TYPE_CODES.get(error_type)


def _is_safe_agent_name(value: str) -> bool:
    return (
        0 < len(value) <= _MAX_AGENT_NAME_LENGTH
        and value[0].isalpha()
        and _AGENT_NAME_CHARACTERS.issuperset(value)
    )


def _is_safe_codebase_name(value: str) -> bool:
    """Accept only a bounded repository-relative path with no traversal."""
    if not 0 < len(value) <= _MAX_CODEBASE_NAME_LENGTH:
        return False
    if not _CODEBASE_NAME_CHARACTERS.issuperset(value) or value.startswith("/"):
        return False
    return ".." not in value.split("/")


class WorkflowFailureEntry(BaseModel):
    """Identifies one failed unit. Invalid optional values are discarded."""

    model_config = ConfigDict(extra="ignore", frozen=True, hide_input_in_errors=True)

    agent: Optional[str] = None
    codebase: Optional[str] = None
    code: WorkflowErrorCode = WorkflowErrorCode.WORKFLOW_FAILED
    status_code: Optional[int] = Field(default=None, ge=100, le=599)

    @field_validator("agent", mode="before")
    @classmethod
    def _discard_invalid_agent(cls, value: object) -> Optional[str]:
        if isinstance(value, str) and _is_safe_agent_name(value):
            return value
        return None

    @field_validator("codebase", mode="before")
    @classmethod
    def _discard_invalid_codebase(cls, value: object) -> Optional[str]:
        if isinstance(value, str) and _is_safe_codebase_name(value):
            return value
        return None

    @field_validator("code", mode="before")
    @classmethod
    def _discard_unknown_code(cls, value: object) -> WorkflowErrorCode:
        if isinstance(value, str):
            try:
                return WorkflowErrorCode(value)
            except ValueError:
                pass
        return WorkflowErrorCode.WORKFLOW_FAILED

    @field_validator("status_code", mode="before")
    @classmethod
    def _discard_invalid_status_code(cls, value: object) -> Optional[int]:
        if isinstance(value, int) and not isinstance(value, bool):
            return value if 100 <= value <= 599 else None
        return None


class ErrorReportMetadata(BaseModel):
    """Allowlisted diagnostics stored with a workflow error report."""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    code: WorkflowErrorCode
    retryable: Optional[bool] = None
    failures: Tuple[WorkflowFailureEntry, ...] = Field(
        default=(), max_length=MAX_REPORTED_FAILURES
    )


def _failures_from_details(details: object) -> Tuple[WorkflowFailureEntry, ...]:
    """Keep allowlisted fields from failure entries, flattening one list level."""
    if not isinstance(details, Sequence) or isinstance(details, (str, bytes)):
        return ()
    candidates: list[object] = []
    for item in details:
        if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            candidates.extend(item)
        else:
            candidates.append(item)
    # Other error details, such as activity context, do not name a failed unit.
    entries = (
        WorkflowFailureEntry.model_validate(candidate)
        for candidate in candidates
        if isinstance(candidate, Mapping)
    )
    return tuple(entry for entry in entries if entry.agent or entry.codebase)[
        :MAX_REPORTED_FAILURES
    ]


def _metadata_from_untrusted(raw_metadata: object) -> ErrorReportMetadata:
    """Rebuild metadata from current or historical input, keeping allowlisted values."""
    source: Mapping[str, object] = (
        raw_metadata if isinstance(raw_metadata, Mapping) else {}
    )
    raw_code = source.get("code")
    code = _error_code_for_type(source.get("type")) or WorkflowErrorCode.WORKFLOW_FAILED
    if isinstance(raw_code, str):
        try:
            code = WorkflowErrorCode(raw_code)
        except ValueError:
            pass
    retryable = source.get("retryable")
    non_retryable = source.get("non_retryable")
    if not isinstance(retryable, bool):
        retryable = not non_retryable if isinstance(non_retryable, bool) else None
    raw_failures = source.get("failures")
    failures = raw_failures if raw_failures is not None else source.get("details")
    return ErrorReportMetadata(
        code=code,
        retryable=retryable,
        failures=_failures_from_details(failures),
    )


class ErrorReport(BaseModel):
    """Failure summary that can hold only a static message and allowlisted metadata.

    Validation rebuilds every report from its metadata. Input messages, stack
    traces and other fields are discarded, so raw exception text cannot pass
    through this model, whether it comes from a caller, a Temporal payload or a
    historical database row.
    """

    model_config = ConfigDict(extra="ignore", frozen=True, hide_input_in_errors=True)

    error_message: str = Field(..., description="Static message for the error code")
    metadata: ErrorReportMetadata = Field(
        ..., description="Allowlisted failure diagnostics"
    )

    @model_validator(mode="before")
    @classmethod
    def _rebuild_from_allowlist(cls, value: object) -> object:
        if isinstance(value, ErrorReport):
            return value
        raw_metadata = value.get("metadata") if isinstance(value, Mapping) else None
        metadata = _metadata_from_untrusted(raw_metadata)
        return {
            "error_message": WORKFLOW_ERROR_MESSAGES[metadata.code],
            "metadata": metadata,
        }


def _classify_exception(
    exception: BaseException,
) -> Tuple[WorkflowErrorCode, BaseException]:
    """Walk the cause chain to the first allowlisted type, using it only as a key.

    Temporal stores the wrapped failure in ``__cause__``. ``ApplicationError.type``
    is checked first, then the exception class name for errors raised in process.
    Messages are never read.
    """
    current = exception
    for _ in range(_MAX_CAUSE_DEPTH):
        code = _error_code_for_type(getattr(current, "type", None))
        if code is None:
            code = _error_code_for_type(type(current).__name__)
        if code is not None:
            return code, current
        if current.__cause__ is None:
            break
        current = current.__cause__
    return WorkflowErrorCode.WORKFLOW_FAILED, current


def error_report_from_exception(exception: BaseException) -> ErrorReport:
    """Build a persisted-safe report without reading exception message text."""
    code, source = _classify_exception(exception)
    return ErrorReport.model_validate(
        {
            "metadata": {
                "code": code.value,
                "non_retryable": getattr(source, "non_retryable", None),
                "details": getattr(source, "details", None),
            }
        }
    )


def workflow_failure_entry(
    exception: BaseException,
    *,
    agent: Optional[str] = None,
    codebase: Optional[str] = None,
) -> Dict[str, object]:
    """Describe one failed unit as a JSON-safe entry for failure details."""
    code, source = _classify_exception(exception)
    return WorkflowFailureEntry.model_validate(
        {
            "agent": agent,
            "codebase": codebase,
            "code": code.value,
            "status_code": getattr(source, "status_code", None),
        }
    ).model_dump(mode="json")


def persisted_error_report(report: Optional[ErrorReport]) -> Optional[Dict[str, object]]:
    """Return the only form of an error report that may be written to the database.

    Revalidating here also covers instances changed with ``model_copy`` or built
    with ``model_construct``, which skip the model's validators.
    """
    if report is None:
        return None
    return ErrorReport.model_validate(
        report.model_dump(mode="json", warnings=False)
    ).model_dump(mode="json")
