"""Provider URL construction helpers for GitHub (open-source and enterprise)."""

from typing import Any, Optional

from fastapi import HTTPException
from unoplat_code_confluence_commons.credential_enums import ProviderKey


def get_github_graphql_url(
    provider_key: ProviderKey, metadata: Optional[dict[str, Any]]
) -> str:
    """
    Get GitHub GraphQL API endpoint URL.

    Supports:
    - GitHub.com (GITHUB_OPEN): https://api.github.com/graphql
    - Enterprise Server (GITHUB_ENTERPRISE + URL): https://HOSTNAME/api/graphql
    - Enterprise Cloud standard (GITHUB_ENTERPRISE, no URL): https://api.github.com/graphql
    - Enterprise Cloud data residency (GITHUB_ENTERPRISE + ghe.com): https://api.SUBDOMAIN.ghe.com/graphql

    Args:
        provider_key: Provider key (GITHUB_OPEN or GITHUB_ENTERPRISE)
        metadata: Metadata containing base URL for enterprise instances

    Returns:
        GitHub GraphQL API endpoint URL

    Raises:
        HTTPException: If enterprise configuration is invalid
    """
    if provider_key == ProviderKey.GITHUB_ENTERPRISE:
        # Enterprise configurations require metadata, but URL is optional
        if not metadata or "url" not in metadata or not metadata["url"]:
            # No URL provided - assume Enterprise Cloud (standard) using github.com
            return "https://api.github.com/graphql"

        base_url = metadata["url"].rstrip("/")

        # Check for Enterprise Cloud with data residency (ghe.com subdomain)
        if ".ghe.com" in base_url:
            # Example: https://octocorp.ghe.com -> https://api.octocorp.ghe.com/graphql
            domain = base_url.replace("https://", "").replace("http://", "")
            return f"https://api.{domain}/graphql"

        # GitHub Enterprise Server (self-hosted)
        # Example: https://github.mycompany.com -> https://github.mycompany.com/api/graphql
        return f"{base_url}/api/graphql"
    else:
        # Default to GitHub.com for GITHUB_OPEN
        return "https://api.github.com/graphql"


def get_github_rest_api_base_url(
    provider_key: ProviderKey, metadata: Optional[dict[str, Any]]
) -> str:
    """
    Get GitHub REST API base URL based on provider type.

    Supports:
    - GitHub.com (GITHUB_OPEN): https://api.github.com
    - Enterprise Server (GITHUB_ENTERPRISE + URL): https://HOSTNAME/api/v3
    - Enterprise Cloud standard (GITHUB_ENTERPRISE, no URL): https://api.github.com
    - Enterprise Cloud data residency (GITHUB_ENTERPRISE + ghe.com): https://api.SUBDOMAIN.ghe.com

    Args:
        provider_key: Provider key (GITHUB_OPEN or GITHUB_ENTERPRISE)
        metadata: Metadata containing base URL for enterprise instances

    Returns:
        GitHub REST API base URL

    Raises:
        HTTPException: If enterprise configuration is invalid
    """
    if provider_key == ProviderKey.GITHUB_ENTERPRISE:
        # Enterprise configurations require metadata, but URL is optional
        if not metadata or "url" not in metadata or not metadata["url"]:
            # No URL provided - assume Enterprise Cloud (standard) using github.com
            return "https://api.github.com"

        base_url = metadata["url"].rstrip("/")

        # Check for Enterprise Cloud with data residency (ghe.com subdomain)
        if ".ghe.com" in base_url:
            # Example: https://octocorp.ghe.com -> https://api.octocorp.ghe.com
            domain = base_url.replace("https://", "").replace("http://", "")
            return f"https://api.{domain}"

        # GitHub Enterprise Server (self-hosted)
        # Example: https://github.mycompany.com -> https://github.mycompany.com/api/v3
        return f"{base_url}/api/v3"
    else:
        # Default to GitHub.com for GITHUB_OPEN
        return "https://api.github.com"


def build_repository_git_url(
    repository_owner_name: str,
    repository_name: str,
    provider_key: ProviderKey,
    metadata: Optional[dict[str, Any]],
) -> str:
    """
    Construct the git clone URL for a repository based on provider configuration.

    Args:
        repository_owner_name: Repository owner/organization name
        repository_name: Repository name
        provider_key: Provider key (GITHUB_OPEN or GITHUB_ENTERPRISE)
        metadata: Metadata containing base URL for enterprise instances

    Returns:
        Git clone URL (HTTPS format)

    Raises:
        HTTPException: If repository details or enterprise configuration is invalid
    """
    owner = repository_owner_name.strip()
    repo = repository_name.strip()
    if not owner or not repo:
        raise HTTPException(
            status_code=400,
            detail="Repository owner and name are required to build git URL",
        )

    if provider_key == ProviderKey.GITHUB_OPEN:
        base_url = "https://github.com"
    else:
        # GITHUB_ENTERPRISE
        if not metadata or not metadata.get("url"):
            # No URL - assume Enterprise Cloud (standard) using github.com
            base_url = "https://github.com"
        else:
            base_url = metadata["url"].rstrip("/")

    return f"{base_url}/{owner}/{repo}.git"
