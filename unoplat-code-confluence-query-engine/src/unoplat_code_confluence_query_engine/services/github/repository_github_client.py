"""Server-side GitHub client construction from stored repository credentials."""

from __future__ import annotations

from ghapi.core import GhApi
from unoplat_code_confluence_commons.credential_enums import ProviderKey

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.github.github_api_helpers import (
    resolve_github_host,
)


class RepositoryCredentialsError(Exception):
    """Repository provider access cannot be established from stored credentials."""


class RepositoryCredentialsMissingError(RepositoryCredentialsError):
    """No repository token is stored for the provider."""


class RepositoryCredentialsInvalidError(RepositoryCredentialsError):
    """The stored token cannot be decrypted, or its host configuration is invalid."""


async def create_repository_github_client(
    owner: str, repository: str, provider: ProviderKey
) -> GhApi:
    """Build a GitHub client using the credentials stored for a provider.

    Args:
        owner: Repository owner name.
        repository: Repository name.
        provider: Repository provider recorded on the repository row.

    Returns:
        A client bound to the repository. No request has been sent yet.

    Raises:
        RepositoryCredentialsMissingError: No token is stored for the provider.
        RepositoryCredentialsInvalidError: The stored credential is unusable.
    """
    try:
        async with get_startup_session() as session:
            pat = await CredentialsService.get_repository_pat(session, provider)
            metadata = await CredentialsService.get_repository_credential_metadata(
                session, provider
            )
            host = resolve_github_host(provider, metadata)
    except ValueError as error:
        raise RepositoryCredentialsInvalidError(
            "Repository credentials or GitHub host configuration are invalid"
        ) from error
    if not pat:
        raise RepositoryCredentialsMissingError(
            "Repository credentials are not configured"
        )
    return GhApi(owner=owner, repo=repository, token=pat, gh_host=host)
