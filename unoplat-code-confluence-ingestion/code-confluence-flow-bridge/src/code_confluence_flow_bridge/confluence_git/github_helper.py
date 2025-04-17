# Standard Library
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.models.github.github_repo import GitHubRepoRequestConfiguration

import os
import asyncio  # NEW: Import asyncio to run blocking calls in a thread
from typing import Any, Dict, List

# Third Party
from git import Repo
from github import Auth, Github
from loguru import logger

# NEW: Add Temporal activity based logging import
from temporalio import activity


class GithubHelper:
    # works with - vhttps://github.com/organization/repository,https://github.com/organization/repository.git,git@github.com:organization/repository.git
    async def clone_repository(self, repo_request: GitHubRepoRequestConfiguration, github_token: str) -> UnoplatGitRepository:
        """
        Clone the repository asynchronously and return repository details.
        Works with URL formats:
        - https://github.com/organization/repository
        - https://github.com/organization/repository.git
        - git@github.com:organization/repository.git
        """
        # Initialize Github client with personal access token
        auth = Auth.Token(github_token)
        github_client: Github = Github(auth=auth)

        # Get repository URL from settings and prepare repo_path and repo_name
        repo_url: str = repo_request.repository_git_url
        if repo_url.startswith("git@"):
            # Handle SSH format: git@github.com:org/repo.git
            repo_path: str = repo_url.split("github.com:")[-1]
        else:
            # Handle HTTPS format: https://github.com/org/repo[.git]
            repo_path = repo_url.split("github.com/")[-1]
        repo_path = repo_path.replace(".git", "")
        repo_name: str = repo_path.split("/")[-1]

        try:
            # Get repository object asynchronously (blocking network call wrapped in thread)
            github_repo = await asyncio.to_thread(github_client.get_repo, repo_path)

            # Create local directory if it doesn't exist
            local_path: str = os.path.join(os.path.expanduser("~"), ".unoplat", "repositories")
            os.makedirs(local_path, exist_ok=True)
            # Reassign repo_path to the local clone path
            repo_path = os.path.join(local_path, repo_name)

            # Clone repository asynchronously if not already cloned
            if not os.path.exists(repo_path):
                await asyncio.to_thread(Repo.clone_from, repo_url, repo_path)

            # Activity-based and pass-through logging
            activity.logger.info(f"[Temporal] Repository is available at local path: {repo_path}")
            logger.info(f"[Temporal-Python @Web] Repository is available at local path: {repo_path}")

            # Build repo metadata
            repo_metadata: Dict[str, Any] = {
                "stars": github_repo.stargazers_count,
                "forks": github_repo.forks_count,
                "default_branch": github_repo.default_branch,
                "created_at": str(github_repo.created_at),
                "updated_at": str(github_repo.updated_at),
                "language": github_repo.language,
            }

            # Get README content asynchronously (if available)
            try:
                readme_content: str | None = await asyncio.to_thread(
                    lambda: github_repo.get_readme().decoded_content.decode("utf-8")
                )
            except Exception:
                readme_content = None

            # Create UnoplatCodebase objects for each codebase config in repository_metadata
            codebases: List[UnoplatCodebase] = []
            for codebase_config in repo_request.repository_metadata:
                # First build path with codebase_folder
                local_path = repo_path
                if codebase_config.codebase_folder and codebase_config.codebase_folder != ".":
                    path_components = codebase_config.codebase_folder.split("/")
                    for component in path_components:
                        local_path = os.path.join(local_path, component)

                source_directory: str = local_path

                # Then append root_package components if present
                if codebase_config.root_package and codebase_config.root_package != ".":
                    root_package_components = codebase_config.root_package.split("/")
                    for component in root_package_components:
                        local_path = os.path.join(local_path, component)
                else:
                    if codebase_config.programming_language_metadata.language.value == "python":
                        raise Exception("Root package should be specified for python codebases")

                # Log the computed local path for the codebase (activity-based and pass-through)
                activity.logger.info(f"[Temporal] Codebase local path computed as: {local_path}")
                logger.info(f"[Temporal-Python @Web] Codebase local path computed as: {local_path}")

                programming_language_metadata: ProgrammingLanguageMetadata = codebase_config.programming_language_metadata
                # Verify the path exists asynchronously
                if not await asyncio.to_thread(os.path.exists, local_path):
                    raise Exception(f"Codebase path not found: {local_path}")

                codebase = UnoplatCodebase(
                    name=codebase_config.root_package,  # type: ignore
                    local_path=local_path,
                    source_directory=source_directory,
                    package_manager_metadata=UnoplatPackageManagerMetadata(
                        programming_language=programming_language_metadata.language.value,
                        package_manager=programming_language_metadata.package_manager,
                        programming_language_version=programming_language_metadata.language_version,
                    ),
                )
                codebases.append(codebase)

            # Create and return UnoplatGitRepository
            return UnoplatGitRepository(
                repository_url=repo_url,
                repository_name=repo_name,
                repository_metadata=repo_metadata,  # type: ignore
                codebases=codebases,
                readme=readme_content,
                github_organization=github_repo.organization.login if github_repo.organization else None,
            )

        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")
