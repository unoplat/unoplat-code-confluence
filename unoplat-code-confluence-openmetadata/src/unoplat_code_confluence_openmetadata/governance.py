"""OpenMetadata domain and data product requests for Code Confluence assets."""

from __future__ import annotations

from collections.abc import Iterator
from typing import TypeAlias

from metadata.generated.schema.api.domains.createDataProduct import CreateDataProductRequest
from metadata.generated.schema.api.domains.createDomain import CreateDomainRequest
from metadata.generated.schema.entity.domains.domain import DomainType
from metadata.generated.schema.type.basic import EntityName, FullyQualifiedEntityName, Markdown
from metadata.ingestion.models.custom_pydantic import BaseModel
from metadata.ingestion.ometa.ometa_api import OpenMetadata

DEVELOPER_TOOLING_DOMAIN_NAME = EntityName("DeveloperTooling")
DEVELOPER_TOOLING_DOMAIN_FQN = FullyQualifiedEntityName("DeveloperTooling")

CODE_CONFLUENCE_DATA_PRODUCT_NAME = EntityName("DeterministicContextForCodeConfluence")
CODE_CONFLUENCE_DATA_PRODUCT_FQN = FullyQualifiedEntityName(
    "DeterministicContextForCodeConfluence"
)

GovernanceCreateRequest: TypeAlias = CreateDomainRequest | CreateDataProductRequest


def publish_governance(metadata: OpenMetadata[BaseModel, BaseModel]) -> None:
    """Create or update the DeveloperTooling domain and Code Confluence data product."""

    for request in iter_governance_requests():
        metadata.create_or_update(request)


def iter_governance_requests() -> Iterator[GovernanceCreateRequest]:
    """Yield the developer-tooling domain and Code Confluence data product requests."""

    yield CreateDomainRequest(
        domainType=DomainType.Aggregate,
        name=DEVELOPER_TOOLING_DOMAIN_NAME,
        fullyQualifiedName=DEVELOPER_TOOLING_DOMAIN_FQN,
        displayName="Developer Tooling",
        description=Markdown(
            "Aggregate domain for tools and platforms that serve software developers and "
            "AI coding agents. It groups data products that aggregate signals across many "
            "source-code repositories to provide developer-facing context, evidence, and "
            "discovery surfaces."
        ),
        style=None,
        parent=None,
        owners=None,
        experts=None,
        tags=None,
        extension=None,
    )
    yield CreateDataProductRequest(
        name=CODE_CONFLUENCE_DATA_PRODUCT_NAME,
        fullyQualifiedName=CODE_CONFLUENCE_DATA_PRODUCT_FQN,
        displayName="Deterministic Context for Code Confluence",
        description=Markdown(
            "Deterministic source-code context produced by Unoplat Code Confluence. This "
            "data product packages repository API services, codebase collections, and "
            "route-level endpoints with evidence-backed metadata so developers and AI "
            "agents can connect catalog assets directly to authoritative source-code "
            "facts (where behavior lives, how to change it, and which file/line evidence "
            "supports each surface)."
        ),
        style=None,
        owners=None,
        domains=[DEVELOPER_TOOLING_DOMAIN_FQN],
        experts=None,
        reviewers=None,
        assets=None,
        tags=None,
        extension=None,
    )


def code_confluence_domain_fqns() -> list[FullyQualifiedEntityName]:
    """Return the domain FQNs assigned to Code Confluence assets."""

    return [DEVELOPER_TOOLING_DOMAIN_FQN]


def code_confluence_data_product_fqns() -> list[FullyQualifiedEntityName]:
    """Return data product FQNs assigned to Code Confluence assets."""

    return [CODE_CONFLUENCE_DATA_PRODUCT_FQN]
