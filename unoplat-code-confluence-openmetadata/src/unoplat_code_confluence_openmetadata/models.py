"""Pydantic models for the repository agent snapshot endpoint response.

These models intentionally live in this package instead of importing from the
query-engine package. The OpenMetadata connector wheel must be installable inside
OpenMetadata's ingestion image without pulling the query-engine service package.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProgrammingLanguageMetadata(BaseModel):
    """Programming language metadata emitted for a codebase."""

    primary_language: str
    package_manager: str

    model_config = ConfigDict(extra="ignore")


class EngineeringWorkflowCommand(BaseModel):
    """Canonical engineering workflow command entry."""

    command: str
    stage: str
    config_file: str
    working_directory: str | None = None

    model_config = ConfigDict(extra="ignore")


class EngineeringWorkflow(BaseModel):
    """Canonical engineering workflow command inventory."""

    commands: list[EngineeringWorkflowCommand] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class DependencyGuideEntry(BaseModel):
    """Documentation entry for one dependency."""

    name: str
    purpose: str

    model_config = ConfigDict(extra="ignore")


class DependencyGuide(BaseModel):
    """Dependency documentation emitted for a codebase."""

    dependencies: list[DependencyGuideEntry] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class CoreFileReference(BaseModel):
    """Line-level reference inside a source file."""

    identifier: str
    start_line: int
    end_line: int

    model_config = ConfigDict(extra="ignore")


class CoreFile(BaseModel):
    """Core business logic source file details."""

    path: str
    responsibility: str | None = None
    references: list[CoreFileReference] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class BusinessLogicDomain(BaseModel):
    """Business logic domain emitted for a codebase."""

    description: str
    data_models: list[CoreFile] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class InterfaceConstruct(BaseModel):
    """Inbound, outbound, or internal construct detected in a codebase."""

    kind: str
    library: str | None = None
    match_pattern: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(extra="ignore")


class Interfaces(BaseModel):
    """Application interfaces emitted for a codebase."""

    inbound_constructs: list[InterfaceConstruct] = Field(default_factory=list)
    outbound_constructs: list[InterfaceConstruct] = Field(default_factory=list)
    internal_constructs: list[InterfaceConstruct] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class CodebaseSnapshot(BaseModel):
    """Completed agent output for one codebase in a repository workflow run."""

    codebase_name: str | None = None
    programming_language_metadata: ProgrammingLanguageMetadata
    engineering_workflow: EngineeringWorkflow = Field(default_factory=EngineeringWorkflow)
    dependency_guide: DependencyGuide | None = None
    business_logic: BusinessLogicDomain
    app_interfaces: Interfaces | None = None

    model_config = ConfigDict(extra="ignore")


class AgentMdOutputSnapshot(BaseModel):
    """Top-level ``agent_md_output`` payload persisted by the query-engine."""

    repository: str
    codebases: dict[str, CodebaseSnapshot]

    model_config = ConfigDict(extra="ignore")

    @field_validator("codebases")
    @classmethod
    def _must_have_codebases(
        cls,
        value: dict[str, CodebaseSnapshot],
    ) -> dict[str, CodebaseSnapshot]:
        if not value:
            raise ValueError("agent_md_output.codebases must not be empty")
        return value


class RepositoryAgentSnapshotResponse(BaseModel):
    """Response body from ``GET /v1/repository-agent-snapshot``."""

    repository_workflow_run_id: str | None = None
    agent_md_output: AgentMdOutputSnapshot

    model_config = ConfigDict(extra="ignore")


def codebase_snapshot_with_name(
    codebase_name: str,
    payload: CodebaseSnapshot,
) -> CodebaseSnapshot:
    """Return a codebase snapshot with a deterministic name populated.

    Current workflow results include the codebase name both as the key under
    ``codebases`` and as an optional ``codebase_name`` field in each value. The
    key is the stable source of truth for mapping, so this helper fills missing
    value-level names from the mapping key.
    """

    if payload.codebase_name:
        return payload
    return payload.model_copy(update={"codebase_name": codebase_name})


def iter_named_codebases(
    snapshot: RepositoryAgentSnapshotResponse,
) -> Mapping[str, CodebaseSnapshot]:
    """Return codebases with missing embedded names filled from their keys."""

    return {
        name: codebase_snapshot_with_name(name, payload)
        for name, payload in snapshot.agent_md_output.codebases.items()
    }
