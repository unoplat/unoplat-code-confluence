"""OpenMetadata glossary requests for Code Confluence output sections."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from metadata.generated.schema.api.data.createGlossary import CreateGlossaryRequest
from metadata.generated.schema.api.data.createGlossaryTerm import CreateGlossaryTermRequest
from metadata.generated.schema.entity.data.glossaryTerm import TermReference
from metadata.generated.schema.type.basic import EntityName, FullyQualifiedEntityName, Markdown
from metadata.generated.schema.type.tagLabel import LabelType, State, TagFQN, TagLabel, TagSource
from metadata.ingestion.models.custom_pydantic import BaseModel
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from pydantic import AnyUrl

CODE_CONFLUENCE_GLOSSARY_NAME = EntityName("CodeConfluenceSections")
CODE_CONFLUENCE_GLOSSARY_FQN = FullyQualifiedEntityName("CodeConfluenceSections")


def iter_glossary_requests() -> Iterator[CreateGlossaryRequest | CreateGlossaryTermRequest]:
    """Yield glossary entities describing Code Confluence output sections."""

    yield CreateGlossaryRequest(
        name=CODE_CONFLUENCE_GLOSSARY_NAME,
        displayName="Code Confluence Sections",
        description=Markdown(
            "Canonical glossary for Code Confluence repository analysis sections "
            "emitted from the agent markdown output model."
        ),
        reviewers=None,
        owners=None,
        tags=None,
        mutuallyExclusive=None,
        domains=None,
        extension=None,
    )

    for term in _section_terms():
        yield CreateGlossaryTermRequest(
            glossary=CODE_CONFLUENCE_GLOSSARY_FQN,
            name=term.name,
            displayName=term.display_name,
            description=term.description,
            synonyms=term.synonyms,
            references=term.references,
            parent=None,
            relatedTerms=None,
            reviewers=None,
            owners=None,
            tags=None,
            mutuallyExclusive=None,
            extension=None,
        )


def publish_glossary(metadata: OpenMetadata[BaseModel, BaseModel]) -> None:
    """Create or update Code Confluence glossary entities via the SDK."""

    for request in iter_glossary_requests():
        metadata.create_or_update(request)


def collection_section_tags() -> list[TagLabel]:
    """Return glossary labels for the four codebase-level output sections."""

    return [
        TagLabel(
            tagFQN=TagFQN(f"{CODE_CONFLUENCE_GLOSSARY_NAME.root}.{term.name.root}"),
            name=None,
            displayName=None,
            description=None,
            href=None,
            source=TagSource.Glossary,
            labelType=LabelType.Generated,
            state=State.Confirmed,
            reason=None,
            appliedAt=None,
            appliedBy=None,
            metadata=None,
        )
        for term in _section_terms()
    ]


@dataclass(frozen=True, slots=True)
class _GlossaryTerm:
    name: EntityName
    display_name: str
    description: Markdown
    synonyms: list[EntityName] | None = None
    references: list[TermReference] | None = None


def _section_terms() -> list[_GlossaryTerm]:
    return [
        _GlossaryTerm(
            name=EntityName("DevelopmentWorkflow"),
            display_name="Development Workflow",
            description=Markdown(
                "Canonical engineering workflow for a codebase. It captures runnable "
                "commands by execution stage, including install, build, development, "
                "test, lint, and type-check commands, plus the relevant config file and "
                "working directory for each command."
            ),
            synonyms=[
                EntityName("Engineering Workflow"),
                EntityName("engineering_workflow"),
            ],
        ),
        _GlossaryTerm(
            name=EntityName("DependencyGuide"),
            display_name="Dependency Guide",
            description=Markdown(
                "Documentation entries for codebase dependencies. Each entry records the "
                "dependency name and a concise purpose derived from official documentation."
            ),
            synonyms=[EntityName("Dependencies"), EntityName("dependency_guide")],
        ),
        _GlossaryTerm(
            name=EntityName("BusinessLogicDomain"),
            display_name="Business Domain",
            description=Markdown(
                "Business logic domain details for a codebase. It summarizes the domain "
                "description and the core data model files, responsibilities, identifiers, "
                "and line-level source references that support the domain."
            ),
            synonyms=[EntityName("Business Domain"), EntityName("business_logic")],
        ),
        _GlossaryTerm(
            name=EntityName("AppInterfaces"),
            display_name="App Interfaces",
            description=Markdown(
                "Application interfaces used by a codebase. The section separates inbound "
                "constructs that receive traffic, outbound constructs emitted to external "
                "systems, and internal framework features, with library and codebase-relative "
                "match-pattern evidence for each construct."
            ),
            synonyms=[EntityName("Application Interfaces"), EntityName("app_interfaces")],
            references=[
                TermReference(
                    name="Capability and Operation Hierarchy",
                    endpoint=AnyUrl(
                        "https://docs.unoplat.io/docs/contribution/"
                        "custom-framework-schema#capability-and-operation-hierarchy"
                    ),
                )
            ],
        ),
    ]
