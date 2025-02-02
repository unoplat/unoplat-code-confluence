# Standard Library
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata, RepositorySettings

import os
from typing import Any, Dict, List

# Third Party
from git import Repo
from github import Auth, Github


class GithubHelper:
    # works with - vhttps://github.com/organization/repository,https://github.com/organization/repository.git,git@github.com:organization/repository.git
    def clone_repository(self, repository_settings: RepositorySettings, github_token: str) -> UnoplatGitRepository:
        """
        Clone the repository and return repository details
        Works with URL formats:
        - https://github.com/organization/repository
        - https://github.com/organization/repository.git
        - git@github.com:organization/repository.git
        """

        # Initialize Github client with personal access token
        auth = Auth.Token(github_token)
        github_client = Github(auth=auth)

        # Get repository from URL
        repo_url = repository_settings.git_url

        # Extract owner and repo name from different URL formats
        if repo_url.startswith("git@"):
            # Handle SSH format: git@github.com:org/repo.git
            repo_path = repo_url.split("github.com:")[-1]
        else:
            # Handle HTTPS format: https://github.com/org/repo[.git]
            repo_path = repo_url.split("github.com/")[-1]

        # Remove .git suffix if present
        repo_path = repo_path.replace(".git", "")
        repo_name = repo_path.split("/")[-1]

        try:
            # Get repository object from Github using owner/repo format
            github_repo = github_client.get_repo(repo_path)

            # Create local directory if it doesn't exist
            local_path = os.path.join(os.path.expanduser("~"), ".unoplat", "repositories")
            os.makedirs(local_path, exist_ok=True)
            repo_path = os.path.join(local_path, repo_name)

            # Clone repository if not already cloned
            if not os.path.exists(repo_path):
                Repo.clone_from(repo_url, repo_path)

            # Get repository metadata
            repo_metadata: Dict[str, Any] = {
                "stars": github_repo.stargazers_count,
                "forks": github_repo.forks_count,
                "default_branch": github_repo.default_branch,
                "created_at": str(github_repo.created_at),
                "updated_at": str(github_repo.updated_at),
                "language": github_repo.language,
            }

            # Get README content
            try:
                readme_content = github_repo.get_readme().decoded_content.decode("utf-8")
            except:
                readme_content = None

            # Create UnoplatCodebase objects for each codebase config
            codebases: List[UnoplatCodebase] = []
            for codebase_config in repository_settings.codebases:  # type: CodebaseConfig
                # First build path with codebase_folder
                local_path = repo_path
                if codebase_config.codebase_folder and codebase_config.codebase_folder != ".":
                    path_components = codebase_config.codebase_folder.split("/")

                    for component in path_components:
                        local_path = os.path.join(local_path, component)

                source_directory = local_path

                # Then append root_package components if present
                if codebase_config.root_package and codebase_config.root_package != ".":
                    root_package_components = codebase_config.root_package.split("/")
                    for component in root_package_components:
                        local_path = os.path.join(local_path, component)
                else:
                    if codebase_config.programming_language_metadata.language.value == "python":
                        raise Exception("Root package should be specified for python codebases")

                programming_language_metadata: ProgrammingLanguageMetadata = codebase_config.programming_language_metadata
                # Verify the path exists
                if not os.path.exists(local_path):
                    raise Exception(f"Codebase path not found: {local_path}")

                codebase = UnoplatCodebase(
                    name=codebase_config.root_package,  # type: ignore
                    local_path=local_path,
                    source_directory=source_directory,
                    package_manager_metadata=UnoplatPackageManagerMetadata(programming_language=programming_language_metadata.language.value, package_manager=programming_language_metadata.package_manager, programming_language_version=programming_language_metadata.language_version),
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

    def close(self):
        """
        Close the Github client connection
        """
        self.github_client.close()
