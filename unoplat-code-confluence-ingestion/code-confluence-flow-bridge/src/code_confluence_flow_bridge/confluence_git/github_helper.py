import os
from datetime import datetime
from pathlib import PurePosixPath
import traceback
from typing import Any, Dict, List, Optional

from git import Repo
from github import Auth, Github
from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.base_models import (
    ProgrammingLanguageMetadata,
)

from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    workflow_id_var,
    workflow_run_id_var,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_codebase import (
    UnoplatCodebase,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.models.github.github_repo import (
    RepositoryRequestConfiguration,
)
from src.code_confluence_flow_bridge.utility.environment_utils import (
    ensure_local_repository_base_path,
)


def _relative_manifest_path(
    manifest_path: Optional[str], codebase_folder: str
) -> Optional[str]:
    """Normalize manifest path so it is relative to the codebase root."""
    if not manifest_path:
        return None

    manifest = PurePosixPath(manifest_path)
    codebase = PurePosixPath(codebase_folder) if codebase_folder else PurePosixPath(".")

    if str(codebase) in {"", "."}:
        return manifest.as_posix()

    try:
        relative = manifest.relative_to(codebase)
        return relative.as_posix()
    except ValueError:
        name = manifest.name
        return name if name else manifest.as_posix()


def _has_unmerged_files(repo: Repo) -> bool:
    """
    Check if the repository has unmerged files (merge conflicts).

    Uses git status --porcelain to detect unmerged entries.
    Unmerged status codes: DD, AU, UD, UA, DU, AA, UU (contain 'U' or DD/AA)
    """
    try:
        status_output: str = repo.git.status("--porcelain")
        if not status_output:
            return False

        for line in status_output.splitlines():
            if len(line) < 2:
                continue
            status_code = line[:2]
            if "U" in status_code or status_code in ("DD", "AA"):
                return True
        return False
    except Exception:
        return False


def _reset_to_remote(repo: Repo, default_branch: str, repo_path: str) -> None:
    """
    Hard reset repository to remote branch state and clean untracked files.

    Used when repository is in a conflicted state that prevents stashing.
    """
    logger.warning(
        "Repository in conflicted state, resetting to remote | repo_path={} | branch=origin/{} | status=resetting",
        repo_path,
        default_branch,
    )

    # Abort any in-progress merge
    try:
        repo.git.merge("--abort")
        logger.debug("Aborted in-progress merge | repo_path={}", repo_path)
    except Exception:
        pass  # No merge in progress

    # Hard reset to remote branch
    repo.git.reset("--hard", f"origin/{default_branch}")
    logger.debug("Hard reset completed | repo_path={}", repo_path)

    # Clean untracked files and directories
    repo.git.clean("-fd")
    logger.debug("Cleaned untracked files | repo_path={}", repo_path)


class GithubHelper:
    # works with - vhttps://github.com/organization/repository,https://github.com/organization/repository.git,git@github.com:organization/repository.git
    def clone_repository(
        self, repo_request: RepositoryRequestConfiguration, github_token: str
    ) -> UnoplatGitRepository:
        """
        Clone the repository and return repository details.
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

        # Bind Loguru logger with the passed trace_id

        try:
            logger.debug(
                "Processing git repository | git_url={} | repo_name={} | status=started",
                repo_url,
                repo_name,
            )
            # Get repository object
            github_repo = github_client.get_repo(repo_path)

            # Use configured repository base path from environment settings
            base_path = ensure_local_repository_base_path()
            # Reassign repo_path to the local clone path
            repo_path = os.path.join(str(base_path), repo_name)

            # Clone repository if not already cloned, otherwise update it
            if not os.path.exists(repo_path):
                logger.info(
                    "Repository not found locally, cloning | repo_path={} | status=cloning",
                    repo_path,
                )
                Repo.clone_from(repo_url, repo_path)
                logger.info(
                    "Repository cloned successfully | repo_path={} | status=success",
                    repo_path,
                )
            else:
                logger.info(
                    "Repository exists locally, updating | repo_path={} | status=updating",
                    repo_path,
                )

                # Open existing repository
                local_repo = Repo(repo_path)

                try:
                    # Fetch first - we need remote refs for reset/pull operations
                    logger.debug("Fetching from remote | repo_path={}", repo_path)
                    local_repo.git.fetch("origin")

                    # Get default branch (needed for reset or checkout)
                    default_branch = github_repo.default_branch

                    # Check for unmerged files BEFORE attempting stash
                    # Git cannot stash when files are in an unmerged state (merge conflicts)
                    if _has_unmerged_files(local_repo):
                        # Cannot stash with unmerged files - reset to remote state
                        _reset_to_remote(local_repo, default_branch, repo_path)
                    elif local_repo.is_dirty(untracked_files=True):
                        # Normal dirty state - stash works
                        logger.info(
                            "Found uncommitted changes, stashing | repo_path={} | status=stashing",
                            repo_path,
                        )
                        # Create stash message with available context
                        stash_msg = f"Auto-stash before pull - workflow: {workflow_run_id_var.get('')} - {datetime.now().isoformat()}"
                        stash_result = local_repo.git.stash(
                            "save", "--include-untracked", stash_msg
                        )
                        logger.debug(
                            "Stash result | result={} | repo_path={}",
                            stash_result,
                            repo_path,
                        )

                    # Ensure we're on the default branch
                    logger.debug(
                        "Checking out default branch | branch={} | repo_path={}",
                        default_branch,
                        repo_path,
                    )

                    # Check if branch exists locally
                    local_branches = [ref.name for ref in local_repo.heads]
                    if default_branch not in local_branches:
                        # Branch doesn't exist locally, create tracking branch from remote
                        logger.debug(
                            "Branch does not exist locally, creating tracking branch | branch={} | repo_path={}",
                            default_branch,
                            repo_path,
                        )
                        local_repo.git.checkout(
                            "-b", default_branch, f"origin/{default_branch}"
                        )
                    else:
                        # Branch exists locally, just checkout
                        local_repo.git.checkout(default_branch)

                    # Pull latest changes
                    logger.info(
                        "Pulling latest changes | repo_path={} | status=pulling",
                        repo_path,
                    )

                    try:
                        # Git (>=2.34) requires an explicit reconciliation strategy
                        pull_output: str = local_repo.git.pull(
                            "--no-rebase", "origin", default_branch
                        )
                        logger.debug(
                            "Pull output | output={} | repo_path={}",
                            pull_output,
                            repo_path,
                        )
                    except Exception as git_err:
                        # Log and re-raise for outer handler
                        logger.error(
                            "git pull failed | repo_path={} | error={} | status=failed",
                            repo_path,
                            str(git_err),
                        )
                        raise

                    logger.info(
                        "Repository updated successfully | repo_path={} | status=success",
                        repo_path,
                    )

                except Exception as pull_error:
                    logger.error(
                        "Failed to update repository | repo_path={} | error={} | status=failed",
                        repo_path,
                        str(pull_error),
                    )
                    # Re-raise to be caught by outer exception handler
                    raise

            # Build repo metadata
            repo_metadata: Dict[str, Any] = {
                "stars": github_repo.stargazers_count,
                "forks": github_repo.forks_count,
                "default_branch": github_repo.default_branch,
                "created_at": str(github_repo.created_at),
                "updated_at": str(github_repo.updated_at),
                "language": github_repo.language,
            }

            # Get README content (if available)
            try:
                readme_content: str | None = (
                    github_repo.get_readme().decoded_content.decode("utf-8")
                )
            except Exception:
                readme_content = None

            # Create UnoplatCodebase objects for each codebase config in repository_metadata
            codebases: List[UnoplatCodebase] = []
            if repo_request.repository_metadata:
                for codebase_config in repo_request.repository_metadata:
                    # Build codebase path with codebase_folder
                    codebase_path = repo_path
                    if (
                        codebase_config.codebase_folder
                        and codebase_config.codebase_folder != "."
                    ):
                        path_components = codebase_config.codebase_folder.split("/")
                        for component in path_components:
                            codebase_path = os.path.join(codebase_path, component)

                    # Build absolute paths for each root package
                    root_package_paths: List[str] = []
                    if codebase_config.root_packages:
                        for root_package in codebase_config.root_packages:
                            if root_package == ".":
                                # Root package at codebase root
                                root_package_path = codebase_path
                            else:
                                # Root package in subdirectory
                                root_package_path = os.path.join(
                                    codebase_path, root_package
                                )

                            # Verify the path exists
                            if not os.path.exists(root_package_path):
                                logger.warning(
                                    "Root package path not found | path={} | skipping",
                                    root_package_path,
                                )
                                continue

                            root_package_paths.append(root_package_path)
                    else:
                        if (
                            codebase_config.programming_language_metadata.language.value
                            == "python"
                        ):
                            logger.warning(
                                "No root packages specified for python codebase, using codebase root"
                            )
                        root_package_paths.append(codebase_path)

                    # Verify at least one valid root package path exists
                    if not root_package_paths:
                        raise Exception(
                            f"No valid root package paths found for codebase at {codebase_path}"
                        )

                    # Log the computed paths for the codebase
                    logger.info(
                        "Codebase paths computed | codebase_path={} | root_packages={} | status=success",
                        codebase_path,
                        root_package_paths,
                    )

                    programming_language_metadata: ProgrammingLanguageMetadata = (
                        codebase_config.programming_language_metadata
                    )

                    # Determine codebase name (use codebase_folder or first root package name)
                    codebase_name = codebase_config.codebase_folder
                    if (
                        codebase_config.root_packages
                        and len(codebase_config.root_packages) > 0
                    ):
                        # Use first root package name, or codebase_folder if root package is "."
                        first_root_package = codebase_config.root_packages[0]
                        if first_root_package != ".":
                            codebase_name = first_root_package

                    codebase = UnoplatCodebase(
                        name=codebase_name,
                        root_packages=root_package_paths,
                        codebase_path=codebase_path,
                        codebase_folder=codebase_config.codebase_folder,
                        package_manager_metadata=UnoplatPackageManagerMetadata(
                            programming_language=programming_language_metadata.language.value,
                            package_manager=programming_language_metadata.package_manager.value
                            if programming_language_metadata.package_manager
                            else "unknown",
                            programming_language_version=programming_language_metadata.language_version,
                            manifest_path=_relative_manifest_path(
                                programming_language_metadata.manifest_path,
                                codebase_config.codebase_folder,
                            ),
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
                github_organization=(
                    github_repo.organization.login
                    if github_repo.organization
                    else github_repo.owner.login
                ),
            )

        except Exception as e:
            logger.error(
                "Failed to clone repository | git_url={} | error={} | status=failed",
                repo_url,
                str(e),
            )
            # Capture the traceback string
            tb_str = traceback.format_exc()

            raise ApplicationError(
                f"Failed to clone repository: {str(e)}",
                {"repository": repo_url},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="GithubHelperError",
            )
