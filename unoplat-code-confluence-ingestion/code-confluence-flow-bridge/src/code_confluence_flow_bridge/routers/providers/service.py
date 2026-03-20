import json
from typing import TypedDict, cast

from fastapi import HTTPException
from gql import Client as GQLClient, gql
from gql.transport.aiohttp import AIOHTTPTransport
import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import Credentials
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)

from src.code_confluence_flow_bridge.models.github.github_repo import (
    GitHubRepoSummary,
    PaginatedResponse,
    RepositoryProvidersResponse,
)
from src.code_confluence_flow_bridge.utility.provider_urls import (
    get_github_graphql_url,
    get_github_rest_api_base_url,
)
from src.code_confluence_flow_bridge.utility.token_utils import (
    fetch_repository_provider_token,
)

SEARCH_REPOSITORIES_QUERY = gql(
    """
    query SearchRepositories($query: String!, $first: Int!, $after: String) {
        search(query: $query, type: REPOSITORY, first: $first, after: $after) {
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                ... on Repository {
                    name
                    isPrivate
                    url
                    owner {
                        login
                        url
                    }
                }
            }
        }
    }
    """
)

VIEWER_REPOSITORIES_QUERY = gql(
    """
    query GetRepositories($first: Int!, $after: String) {
        viewer {
            repositories(
                first: $first,
                affiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER],
                after: $after
            ) {
                pageInfo {
                    endCursor
                    hasNextPage
                }
                nodes {
                    name
                    isPrivate
                    url
                    owner {
                        login
                        url
                    }
                }
            }
        }
    }
    """
)


class RepositoryFilterValues(TypedDict, total=False):
    name: str


class GraphQLPageInfo(TypedDict):
    endCursor: str | None
    hasNextPage: bool


class GraphQLRepositoryOwner(TypedDict):
    login: str
    url: str


class GraphQLRepositoryNode(TypedDict):
    name: str
    isPrivate: bool
    url: str
    owner: GraphQLRepositoryOwner


class GraphQLSearchResult(TypedDict):
    pageInfo: GraphQLPageInfo
    nodes: list[GraphQLRepositoryNode]


class GraphQLViewerRepositories(TypedDict):
    pageInfo: GraphQLPageInfo
    nodes: list[GraphQLRepositoryNode]


class GraphQLViewer(TypedDict):
    repositories: GraphQLViewerRepositories


class SearchRepositoriesPayload(TypedDict):
    search: GraphQLSearchResult


class ViewerRepositoriesPayload(TypedDict):
    viewer: GraphQLViewer


class GitHubUserPayload(TypedDict, total=False):
    name: str | None
    avatar_url: str | None
    email: str | None


class GitHubEmailPayload(TypedDict, total=False):
    email: str
    primary: bool
    verified: bool


def parse_repository_filters(filter_values: str | None) -> RepositoryFilterValues:
    """Parse the optional repository filter query string."""
    if filter_values is None:
        return {}

    try:
        parsed_filters = json.loads(filter_values)
    except Exception as exc:
        logger.error("Invalid JSON in filterValues: {}", exc)
        raise HTTPException(
            status_code=400, detail="Invalid JSON in filterValues query parameter"
        )

    if not isinstance(parsed_filters, dict):
        return {}

    name_value = parsed_filters.get("name")
    if isinstance(name_value, str):
        return {"name": name_value}

    return {}


def build_repository_summary(item: GraphQLRepositoryNode) -> GitHubRepoSummary:
    """Map GraphQL repository data into the public response model."""
    return GitHubRepoSummary(
        name=item["name"],
        owner_url=item["owner"]["url"],
        private=item["isPrivate"],
        git_url=item["url"],
        owner_name=item["owner"]["login"],
    )


async def list_repository_providers(
    session: AsyncSession,
) -> RepositoryProvidersResponse:
    """Return configured repository providers from stored credentials."""
    result = await session.execute(
        select(Credentials)
        .where(Credentials.namespace == CredentialNamespace.REPOSITORY)
        .where(Credentials.secret_kind == SecretKind.PAT)
    )
    credentials = result.scalars().all()
    provider_keys = [credential.provider_key for credential in credentials]
    return RepositoryProvidersResponse(providers=provider_keys)


async def fetch_paginated_repositories(
    session: AsyncSession,
    provider_key: ProviderKey,
    per_page: int,
    cursor: str | None,
    filter_values: str | None,
) -> PaginatedResponse:
    """Fetch repositories for the authenticated provider account."""
    token, metadata = await fetch_repository_provider_token(
        session, CredentialNamespace.REPOSITORY, provider_key
    )
    repository_filters = parse_repository_filters(filter_values)
    search_query = repository_filters.get("name")
    graphql_url = get_github_graphql_url(provider_key, metadata)

    transport = AIOHTTPTransport(
        url=graphql_url,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Unoplat Code Confluence",
        },
    )

    async with GQLClient(
        transport=transport,
        fetch_schema_from_transport=False,
    ) as client:
        if search_query:
            result = cast(
                SearchRepositoriesPayload,
                await client.execute(
                    SEARCH_REPOSITORIES_QUERY,
                    variable_values={
                        "query": search_query,
                        "first": per_page,
                        "after": cursor,
                    },
                ),
            )
            repositories = result["search"]["nodes"]
            page_info = result["search"]["pageInfo"]
        else:
            result = cast(
                ViewerRepositoriesPayload,
                await client.execute(
                    VIEWER_REPOSITORIES_QUERY,
                    variable_values={"first": per_page, "after": cursor},
                ),
            )
            repositories = result["viewer"]["repositories"]["nodes"]
            page_info = result["viewer"]["repositories"]["pageInfo"]

    return PaginatedResponse(
        items=[build_repository_summary(item) for item in repositories],
        per_page=per_page,
        has_next=page_info["hasNextPage"],
        next_cursor=page_info["endCursor"],
    )


def select_primary_verified_email(emails: list[GitHubEmailPayload]) -> str | None:
    """Choose the primary verified email from the GitHub emails payload."""
    for email_entry in emails:
        if email_entry.get("primary") and email_entry.get("verified"):
            return email_entry.get("email")
    return None


async def fetch_authenticated_user_details(
    session: AsyncSession,
    provider_key: ProviderKey,
) -> dict[str, str | None]:
    """Fetch authenticated provider user details from the GitHub REST API."""
    token, metadata = await fetch_repository_provider_token(
        session, CredentialNamespace.REPOSITORY, provider_key
    )
    api_base_url = get_github_rest_api_base_url(provider_key, metadata)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient() as client:
        user_response = await client.get(f"{api_base_url}/user", headers=headers)
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=user_response.status_code,
                detail="Failed to fetch user info",
            )

        user_data = cast(GitHubUserPayload, user_response.json())
        email = user_data.get("email")

        if not email:
            emails_response = await client.get(
                f"{api_base_url}/user/emails", headers=headers
            )
            if emails_response.status_code == 200:
                email_payload = cast(list[GitHubEmailPayload], emails_response.json())
                email = select_primary_verified_email(email_payload)

    return {
        "name": user_data.get("name"),
        "avatar_url": user_data.get("avatar_url"),
        "email": email,
    }
