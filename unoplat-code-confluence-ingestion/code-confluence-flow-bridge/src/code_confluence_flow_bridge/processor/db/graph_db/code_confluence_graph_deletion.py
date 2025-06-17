from __future__ import annotations

from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    workflow_id_var,
    workflow_run_id_var,
)
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph

import traceback
from typing import Dict, Set, Union

from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.graph_models.code_confluence_file import (
    CodeConfluenceFile,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository
from unoplat_code_confluence_commons.graph_models.code_confluence_package import (
    CodeConfluencePackage,
)


class CodeConfluenceGraphDeletion:
    """
    Class for handling deletion operations in the Code Confluence graph database.
    """
    
    def __init__(self, code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)
    
    async def initialize(self) -> None:
        """Initialize graph connection"""
        await self.code_confluence_graph.connect()
        logger.info("Graph deletion service initialized")
    
    async def close(self) -> None:
        """Close graph connection"""
        await self.code_confluence_graph.close()
    
    async def _delete_package_recursive(
        self,
        package: CodeConfluencePackage,
        stats: Dict[str, Union[int, str]],
        visited: Set[str],
    ) -> None:
        """Recursively delete a package, all its nested sub-packages and files.

        Args:
            package: Package node to delete.
            stats: Shared statistics collector.
            visited: Set to track visited packages to avoid infinite recursion
        """
        # Prevent cycles / revisiting the same package
        if package.qualified_name in visited:
            return
        visited.add(package.qualified_name)

        # Delete files contained directly in this package via CONTAINS_FILE edge
        files = await package.files.all()
        for file in files:
            await file.delete()
            stats["files_deleted"] = int(stats.get("files_deleted", 0)) + 1

        # Fallback: There might be legacy graphs where only the reverse relationship exists
        if not files:
            

            alt_files = await CodeConfluenceFile.nodes.filter(
                package__qualified_name=package.qualified_name
            ).all()
            for file in alt_files:
                await file.delete()
                stats["files_deleted"] = int(stats.get("files_deleted", 0)) + 1

        # Recursively delete all nested sub-packages
        sub_packages = await package.sub_packages.all()
        for sub_pkg in sub_packages:
            await self._delete_package_recursive(sub_pkg, stats, visited)

        # Finally delete this package node itself
        await package.delete()
        stats["packages_deleted"] = int(stats.get("packages_deleted", 0)) + 1

    async def delete_repository_by_qualified_name(self, qualified_name: str) -> Dict[str, Union[int, str]]:
        """
        Delete a repository and all its related nodes by qualified name.
        
        Args:
            qualified_name: The qualified name of the repository (format: {owner}_{repo_name})
            
        Returns:
            Dict containing deletion statistics
            
        Raises:
            ApplicationError: If repository not found or deletion fails
        """
        try:
            async with self.code_confluence_graph.transaction:
                # First, check if the repository exists
                try:
                    repo_node = await CodeConfluenceGitRepository.nodes.get(qualified_name=qualified_name)
                except CodeConfluenceGitRepository.DoesNotExist:
                    raise ApplicationError(
                        f"Repository not found: {qualified_name}",
                        {"repository": qualified_name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="REPOSITORY_NOT_FOUND"
                    )
                
                # Collect statistics
                stats: Dict[str, Union[int, str]] = {
                    "repository_qualified_name": "",  # Placeholder – will be removed before return
                    "codebases_deleted": 0,
                    "packages_deleted": 0,
                    "files_deleted": 0,
                    "metadata_deleted": 0,
                }
                
                # Get all connected codebases
                codebases = await repo_node.codebases.all()
                
                # Delete each codebase and its children
                for codebase in codebases:
                    # Delete package manager metadata
                    metadata_nodes = await codebase.package_manager_metadata.all()
                    for metadata in metadata_nodes:
                        await metadata.delete()
                        stats["metadata_deleted"] = int(stats.get("metadata_deleted", 0)) + 1
                    
                    # Delete packages and their files
                    packages = await codebase.packages.all()
                    visited_pkgs: Set[str] = set()
                    for package in packages:
                        # Recursively delete package, its sub-packages and files
                        await self._delete_package_recursive(package, stats, visited_pkgs)
                    
                    # Delete the codebase
                    await codebase.delete()
                    stats["codebases_deleted"] = int(stats.get("codebases_deleted", 0)) + 1
                
                # Finally delete the repository
                await repo_node.delete()
                
                # Attach repository qualified name now that deletion succeeded
                stats["repository_qualified_name"] = qualified_name
                return stats
                
        except ApplicationError:
            # Re-raise ApplicationError as is
            raise
        except Exception as e:
            error_msg = f"Failed to delete repository {qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)}")
            
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"repository": qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="GRAPH_DELETION_ERROR"
            )