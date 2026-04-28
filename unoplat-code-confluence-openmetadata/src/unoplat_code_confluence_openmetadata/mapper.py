"""Map Code Confluence snapshots to OpenMetadata create requests."""

from __future__ import annotations

import re
import traceback
from collections.abc import Iterable, Iterator, Mapping
from typing import TypeAlias

from metadata.generated.schema.api.data.createAPICollection import CreateAPICollectionRequest
from metadata.generated.schema.api.data.createAPIEndpoint import CreateAPIEndpointRequest
from metadata.generated.schema.api.services.createApiService import CreateApiServiceRequest
from metadata.generated.schema.entity.data.apiEndpoint import ApiRequestMethod
from metadata.generated.schema.entity.services.apiService import ApiServiceType
from metadata.generated.schema.entity.services.ingestionPipelines.status import StackTraceError
from metadata.generated.schema.type.basic import FullyQualifiedEntityName
from metadata.ingestion.api.models import Either

from unoplat_code_confluence_openmetadata.config import CodeConfluenceSourceConfig
from unoplat_code_confluence_openmetadata.glossary import collection_section_tags
from unoplat_code_confluence_openmetadata.governance import (
    code_confluence_data_product_fqns,
    code_confluence_domain_fqns,
)
from unoplat_code_confluence_openmetadata.models import (
    CodebaseSnapshot,
    InterfaceConstruct,
    RepositoryAgentSnapshotResponse,
    iter_named_codebases,
)
from unoplat_code_confluence_openmetadata.naming import (
    codebase_collection_name,
    collection_fqn,
    endpoint_name,
    first_evidence_path,
    repository_service_name,
)
from unoplat_code_confluence_openmetadata.serialization import (
    collection_extension,
    endpoint_extension,
)

OpenMetadataCreateRequest: TypeAlias = (
    CreateApiServiceRequest | CreateAPICollectionRequest | CreateAPIEndpointRequest
)

HTTP_ENDPOINT_KIND = "http_endpoint"
_METHOD_FROM_ROUTER = re.compile(r"\.([a-zA-Z]+)\s*\(")
_METHOD_FROM_METHODS = re.compile(r"methods\s*=\s*\[\s*[\"']([A-Z]+)[\"']")


def iter_create_requests(
    snapshot: RepositoryAgentSnapshotResponse,
    config: CodeConfluenceSourceConfig,
) -> Iterator[Either[OpenMetadataCreateRequest]]:
    """Yield OpenMetadata create requests, isolating codebase/construct failures."""

    service_name = repository_service_name(
        snapshot.agent_md_output.repository,
        config.service_name,
    )
    domains = code_confluence_domain_fqns()
    data_products = code_confluence_data_product_fqns()
    yield Either(right=create_api_service(snapshot, service_name, domains, data_products))

    for codebase_key, codebase in iter_named_codebases(snapshot).items():
        try:
            collection = create_api_collection(
                codebase_key=codebase_key,
                codebase=codebase,
                service_name=service_name,
                domains=domains,
                data_products=data_products,
            )
            yield Either(right=collection)
        except Exception as exc:  # noqa: BLE001 - item-level isolation for ingestion
            yield Either(left=_stack_error(f"codebase:{codebase_key}", exc))
            continue

        collection_name = collection.name.root
        for construct_index, construct in enumerate(_http_endpoint_constructs(codebase)):
            try:
                yield Either(
                    right=create_api_endpoint(
                        construct=construct,
                        service_name=service_name,
                        collection_name=collection_name,
                        domains=domains,
                        data_products=data_products,
                    )
                )
            except Exception as exc:  # noqa: BLE001 - item-level isolation for ingestion
                evidence_path = first_evidence_path(construct.match_pattern) or "unknown-path"
                yield Either(
                    left=_stack_error(
                        f"codebase:{codebase_key}:construct:{construct_index}:{evidence_path}",
                        exc,
                    )
                )


def create_api_service(
    snapshot: RepositoryAgentSnapshotResponse,
    service_name: str,
    domains: list[FullyQualifiedEntityName],
    data_products: list[FullyQualifiedEntityName],
) -> CreateApiServiceRequest:
    """Create the repository-level APIService request."""

    repository = snapshot.agent_md_output.repository
    return CreateApiServiceRequest(
        name=service_name,
        displayName=repository,
        description=(
            "Code Confluence repository export for "
            f"`{repository}`. Generated from a repository workflow snapshot."
        ),
        serviceType=ApiServiceType.Rest,
        domains=[domain.root for domain in domains],
        dataProducts=data_products,
    )


def create_api_collection(
    *,
    codebase_key: str,
    codebase: CodebaseSnapshot,
    service_name: str,
    domains: list[FullyQualifiedEntityName],
    data_products: list[FullyQualifiedEntityName],
) -> CreateAPICollectionRequest:
    """Create the codebase-level APICollection request."""

    collection_name = codebase_collection_name(codebase.codebase_name or codebase_key)
    interfaces = codebase.app_interfaces
    inbound = interfaces.inbound_constructs if interfaces else []
    outbound = interfaces.outbound_constructs if interfaces else []
    internal = interfaces.internal_constructs if interfaces else []

    return CreateAPICollectionRequest(
        name=collection_name,
        displayName=codebase.codebase_name or codebase_key,
        description=codebase.business_logic_domain.description,
        service=service_name,
        tags=collection_section_tags(),
        domains=domains,
        dataProducts=data_products,
        extension=collection_extension(
            engineering_workflow=codebase.engineering_workflow,
            dependency_guide=codebase.dependency_guide,
            business_logic_domain=codebase.business_logic_domain,
            inbound_constructs=inbound,
            outbound_constructs=outbound,
            internal_constructs=internal,
        ),
    )


def create_api_endpoint(
    *,
    construct: InterfaceConstruct,
    service_name: str,
    collection_name: str,
    domains: list[FullyQualifiedEntityName],
    data_products: list[FullyQualifiedEntityName],
) -> CreateAPIEndpointRequest:
    """Create an APIEndpoint request for one HTTP route evidence item."""

    if construct.kind != HTTP_ENDPOINT_KIND:
        raise ValueError(f"Unsupported API endpoint construct kind: {construct.kind}")

    return CreateAPIEndpointRequest(
        name=endpoint_name(construct.kind, construct.library, construct.match_pattern),
        displayName=_display_name(construct),
        description=_endpoint_description(construct),
        apiCollection=collection_fqn(service_name, collection_name),
        requestMethod=_request_method(construct.match_pattern),
        domains=domains,
        dataProducts=data_products,
        extension=endpoint_extension(construct),
    )


def _http_endpoint_constructs(codebase: CodebaseSnapshot) -> Iterable[InterfaceConstruct]:
    if codebase.app_interfaces is None:
        return []
    return _split_http_endpoint_constructs(codebase.app_interfaces.inbound_constructs)


def _split_http_endpoint_constructs(constructs: Iterable[InterfaceConstruct]) -> Iterator[InterfaceConstruct]:
    for construct in constructs:
        if construct.kind != HTTP_ENDPOINT_KIND:
            continue
        for path, patterns in sorted(construct.match_pattern.items()):
            for pattern in sorted(patterns):
                yield construct.model_copy(update={"match_pattern": {path: [pattern]}})


def _request_method(match_pattern: Mapping[str, list[str]]) -> ApiRequestMethod:
    evidence = "\n".join(item for values in match_pattern.values() for item in values)

    methods_match = _METHOD_FROM_METHODS.search(evidence)
    if methods_match:
        return _method_enum(methods_match.group(1))

    router_match = _METHOD_FROM_ROUTER.search(evidence)
    if router_match:
        return _method_enum(router_match.group(1).upper())

    return ApiRequestMethod.GET


def _method_enum(value: str) -> ApiRequestMethod:
    try:
        return ApiRequestMethod(value.upper())
    except ValueError:
        return ApiRequestMethod.GET


def _display_name(construct: InterfaceConstruct) -> str:
    path = first_evidence_path(construct.match_pattern)
    if path:
        return f"{construct.kind} in {path}"
    return construct.kind


def _endpoint_description(construct: InterfaceConstruct) -> str:
    lines = [
        "HTTP endpoint detected by Code Confluence.",
        f"Kind: `{construct.kind}`.",
    ]
    if construct.library:
        lines.append(f"Library/framework: `{construct.library}`.")
    if construct.match_pattern:
        lines.append("Evidence:")
        for path, patterns in sorted(construct.match_pattern.items()):
            lines.append(f"- `{path}`")
            for pattern in patterns:
                lines.append(f"  - `{pattern}`")
    return "\n".join(lines)


def _stack_error(name: str, exc: Exception) -> StackTraceError:
    return StackTraceError(name=name, error=str(exc), stackTrace=traceback.format_exc())
