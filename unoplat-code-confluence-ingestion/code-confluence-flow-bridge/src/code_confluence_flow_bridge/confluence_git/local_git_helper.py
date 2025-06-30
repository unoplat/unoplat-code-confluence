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
    GitHubRepoRequestConfiguration,
)

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from git import Repo
from loguru import logger


class LocalGitHelper:
    """Helper class for processing local Git repositories."""
    

    def process_local_repository(self, local_path: str, repo_request: GitHubRepoRequestConfiguration) -> UnoplatGitRepository:
        """
        Process a local Git repository and extract metadata.
        
        Args:
            local_path: Local filesystem path to the Git repository
            repo_request: Repository request configuration
            
        Returns:
            UnoplatGitRepository object with extracted metadata
        """
        logger.info("Processing local git repository | local_path={} | status=started", local_path)
        
        try:
            # Open the local repository using GitPython
            # As per GitPython docs, Repo() accepts a local path
            repo = Repo(local_path)
            
            # Extract repository name from path
            repo_name = os.path.basename(local_path)
            
            # Use repository owner name from request (already resolved at endpoint level)
            github_org = repo_request.repository_owner_name
            repo_url = f"file://{local_path}"  # Default to file:// URL for local repos
            
            logger.debug("Using repository owner from request | github_org={}", github_org)
            
            # Get repository metadata
            try:
                default_branch = repo.active_branch.name
            except Exception:
                # Handle detached HEAD state
                default_branch = "main"
                logger.debug("Repository in detached HEAD state, using 'main' as default branch")
            
            # Get file timestamps for creation/modification dates
            repo_metadata: Dict[str, Any] = {
                "stars": 0,  # Local repos don't have stars
                "forks": 0,  # Local repos don't have forks
                "default_branch": default_branch,
                "created_at": str(datetime.fromtimestamp(os.path.getctime(local_path))),
                "updated_at": str(datetime.fromtimestamp(os.path.getmtime(local_path))),
                "language": None,  # Will be detected by codebase detector
            }
            
            # Get README content if available
            readme_content: Optional[str] = None
            for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
                readme_path = os.path.join(local_path, readme_name)
                if os.path.exists(readme_path):
                    try:
                        with open(readme_path, 'r', encoding='utf-8') as f:
                            readme_content = f.read()
                        logger.debug("Found README | filename={}", readme_name)
                        break
                    except Exception as e:
                        logger.warning("Failed to read README | filename={} | error={}", readme_name, str(e))
                        continue
            
            # Process codebases (similar to GithubHelper but with local paths)
            codebases: List[UnoplatCodebase] = []
            for codebase_config in repo_request.repository_metadata:
                # Build codebase path
                codebase_path = local_path
                if codebase_config.codebase_folder and codebase_config.codebase_folder != ".":
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
                            root_package_path = os.path.join(codebase_path, root_package)
                        
                        # Verify the path exists
                        if not os.path.exists(root_package_path):
                            logger.warning("Root package path not found | path={} | skipping", root_package_path)
                            continue
                        
                        root_package_paths.append(root_package_path)
                else:
                    if codebase_config.programming_language_metadata.language.value == "python":
                        logger.warning("No root packages specified for python codebase, using codebase root")
                    root_package_paths.append(codebase_path)
                
                # Verify at least one valid root package path exists
                if not root_package_paths:
                    raise Exception(f"No valid root package paths found for codebase at {codebase_path}")
                
                # Log the computed paths for the codebase
                logger.info("Codebase paths computed | codebase_path={} | root_packages={} | status=success", 
                           codebase_path, root_package_paths)
                
                # Determine codebase name
                codebase_name = codebase_config.codebase_folder
                if codebase_config.root_packages and len(codebase_config.root_packages) > 0:
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
                        programming_language=codebase_config.programming_language_metadata.language.value,
                        package_manager=codebase_config.programming_language_metadata.package_manager.value
                        if codebase_config.programming_language_metadata.package_manager
                        else "unknown",
                        programming_language_version=codebase_config.programming_language_metadata.language_version,
                    ),
                )
                codebases.append(codebase)
            
            # Create and return UnoplatGitRepository
            return UnoplatGitRepository(
                repository_url=repo_url,
                repository_name=repo_name,
                repository_metadata=repo_metadata,
                codebases=codebases,
                readme=readme_content,
                github_organization=github_org,
            )
            
        except Exception as e:
            logger.error("Failed to process local repository | local_path={} | error={} | status=failed", 
                        local_path, str(e))
            raise