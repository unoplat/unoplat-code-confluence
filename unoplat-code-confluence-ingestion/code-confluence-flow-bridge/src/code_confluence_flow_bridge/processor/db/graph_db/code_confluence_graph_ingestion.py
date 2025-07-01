from src.code_confluence_flow_bridge.logging.trace_utils import (
    activity_id_var,
    activity_name_var,
    workflow_id_var,
    workflow_run_id_var,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import (
    ParentChildCloneMetadata,
)
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import (
    CodeConfluenceGraph,
)

import traceback

from loguru import logger
from neomodel.exceptions import RequiredProperty, UniqueProperty
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons import (
    CodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import (
    CodeConfluenceCodebase,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import (
    CodeConfluenceGitRepository,
)


class CodeConfluenceGraphIngestion:
    def __init__(self, code_confluence_env: EnvironmentSettings):
        # Reuse the singleton global connection
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)
        # No longer need to initialize or close - global connection is managed at application level

    def _get_node_identifier(self, node) -> str:
        """
        Get the appropriate identifier for a node for logging purposes.
        
        Args:
            node: The node to get identifier for
            
        Returns:
            str: The identifier value
        """
        # CodeConfluenceFile inherits from AsyncStructuredNode and uses file_path as unique identifier
        if hasattr(node, 'file_path') and node.file_path:
            return node.file_path
        # CodeConfluenceAnnotation inherits from AsyncStructuredNode and uses name as unique identifier
        elif hasattr(node, 'name') and node.name and not hasattr(node, 'qualified_name'):
            return node.name
        # All BaseNode-derived classes use qualified_name
        elif hasattr(node, 'qualified_name') and node.qualified_name:
            return node.qualified_name
        # Fallback to string representation
        else:
            return str(node)

    async def _safe_connect(self, source_node, relationship_attr: str, target_node) -> bool:
        """
        Safely connect two nodes, checking if relationship already exists.
        Logs at INFO level if relationship already exists and proceeds gracefully.
        
        Args:
            source_node: The source node
            relationship_attr: The name of the relationship attribute
            target_node: The target node
            
        Returns:
            bool: True if new connection made, False if already existed
        """
        try:
            relationship = getattr(source_node, relationship_attr)
            if await relationship.is_connected(target_node):
                # Use appropriate identifier for each node type based on inheritance
                source_id = self._get_node_identifier(source_node)
                target_id = self._get_node_identifier(target_node)
                logger.info(
                    "Relationship already exists: {}.{} -> {} (source: {}, target: {})",
                    source_node.__class__.__name__,
                    relationship_attr,
                    target_node.__class__.__name__,
                    source_id,
                    target_id
                )
                return False
            else:
                await relationship.connect(target_node)
                source_id = self._get_node_identifier(source_node)
                target_id = self._get_node_identifier(target_node)
                logger.debug(
                    "Created new relationship: {}.{} -> {} (source: {}, target: {})",
                    source_node.__class__.__name__,
                    relationship_attr,
                    target_node.__class__.__name__,
                    source_id,
                    target_id
                )
                return True
        except Exception as e:
            # Log the error but don't fail the application
            logger.warning(
                "Failed to create relationship {}.{} -> {}: {}. Proceeding gracefully.",
                source_node.__class__.__name__,
                relationship_attr,
                target_node.__class__.__name__,
                str(e)
            )
            return False

    async def _handle_node_creation(self, node_class, node_dict: dict):
        """
        Safely create or update a node with graceful error handling for constraint violations.
        Logs constraint violations and proceeds gracefully instead of failing.
        
        Args:
            node_class: The neomodel node class
            node_dict: Dictionary of node properties
            
        Returns:
            List of created/updated nodes, or empty list if failed
        """
        try:
            results = await node_class.create_or_update(node_dict)
            return results if results else []
        except UniqueProperty as e:
            logger.info(
                "Node already exists with unique property: {} for {}. properties={} Proceeding gracefully.",
                str(e),
                node_class.__name__,
                node_dict,
            )
            # Try to retrieve the existing node by unique properties
            try:
                # Find unique index properties in the node dict
                for prop_name, value in node_dict.items():
                    if hasattr(node_class, prop_name):
                        prop = getattr(node_class, prop_name)
                        if hasattr(prop, 'unique_index') and prop.unique_index:
                            existing_nodes = await node_class.nodes.filter(**{prop_name: value}).all()
                            if existing_nodes:
                                return existing_nodes[:1]  # Return as list for consistency
                # If no unique property found, try qualified_name (all nodes have this from BaseNode)
                if 'qualified_name' in node_dict:
                    existing_nodes = await node_class.nodes.filter(qualified_name=node_dict['qualified_name']).all()
                    if existing_nodes:
                        return existing_nodes[:1]
            except Exception as retrieval_error:
                logger.warning(
                    "Failed to retrieve existing {} node after UniqueProperty error: {}. Proceeding gracefully.",
                    node_class.__name__,
                    str(retrieval_error)
                )
            return []
        except RequiredProperty as e:
            logger.error(
                "Missing required property for {}: {}. Cannot proceed with node creation.",
                node_class.__name__,
                str(e)
            )
            return []
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(
                "Unexpected error creating {} node with properties={} : {}. Proceeding gracefully.\nTraceback:\n{}",
                node_class.__name__,
                node_dict,
                str(e),
                tb_str,
            )
            return []

    async def insert_code_confluence_git_repo(self, git_repo: UnoplatGitRepository) -> ParentChildCloneMetadata:
        """
        Insert a git repository into the graph database

        Args:
            git_repo: UnoplatGitRepository containing git repository data

        Returns:
            ParentChildCloneMetadata: Metadata about created nodes

        Raises:
            ApplicationError: If repository insertion fails
        """
        qualified_name = f"{git_repo.github_organization}_{git_repo.repository_name}"
        parent_child_clone_metadata = ParentChildCloneMetadata(repository_qualified_name=qualified_name, codebase_qualified_names=[])

        try:
            async with self.code_confluence_graph.transaction:
                # Create repository node
                repo_dict = {"qualified_name": qualified_name, "repository_url": git_repo.repository_url, "repository_name": git_repo.repository_name, "repository_metadata": git_repo.repository_metadata, "readme": git_repo.readme, "github_organization": git_repo.github_organization}

                # 🔍 Add verbose logging to aid debugging CI-only failures
                logger.debug("Attempting to create CodeConfluenceGitRepository with properties: {}", repo_dict)

                repo_results = await self._handle_node_creation(CodeConfluenceGitRepository, repo_dict)
                if not repo_results:
                    raise ApplicationError(
                        f"Failed to create repository node: {qualified_name}", 
                        {"repository": qualified_name}, 
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="REPOSITORY_CREATION_ERROR"
                    )

                repo_node = repo_results[0]
                logger.debug(f"Created repository node: {qualified_name}")

                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_qualified_name = f"{qualified_name}_{codebase.name}"

                    codebase_dict = {"qualified_name": codebase_qualified_name, "name": codebase.name, "readme": codebase.readme, "root_packages": codebase.root_packages, "codebase_path": codebase.codebase_path}
                    parent_child_clone_metadata.codebase_qualified_names.append(codebase_qualified_name)

                    logger.debug("Attempting to create CodeConfluenceCodebase with properties: {}", codebase_dict)
                    codebase_results = await self._handle_node_creation(CodeConfluenceCodebase, codebase_dict)
                    if not codebase_results:
                        raise ApplicationError(
                            f"Failed to create codebase node: {codebase.name}",
                            {"repository": qualified_name},
                            {"codebase": codebase.name},
                            {"workflow_id": workflow_id_var.get("")},
                            {"workflow_run_id": workflow_run_id_var.get("")},
                            {"activity_name": activity_name_var.get("")},
                            {"activity_id": activity_id_var.get("")},
                            type="CODEBASE_CREATION_ERROR"
                        )

                    codebase_node = codebase_results[0]

                    # Establish relationships using safe connect
                    await self._safe_connect(repo_node, 'codebases', codebase_node)
                    await self._safe_connect(codebase_node, 'git_repository', repo_node)

                logger.debug(f"Successfully ingested repository {qualified_name}")
                return parent_child_clone_metadata

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)} | status=failed")
            
            # Capture the traceback string
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
                type="GRAPH_INGESTION_ERROR"
            ) from e

    async def insert_code_confluence_codebase_package_manager_metadata(self, codebase_qualified_name: str, package_manager_metadata: UnoplatPackageManagerMetadata) -> None:
        """
        Insert codebase package manager metadata into the graph database.
        
        Note: This method runs within the transaction context provided by the caller.
        Do not create nested transactions as Neo4j does not support them.

        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: UnoplatPackageManagerMetadata containing package manager metadata
        """
        try:
            # All operations run within the caller's transaction context
            # Use get() instead of filter() for unique index
            try:
                codebase_node = await CodeConfluenceCodebase.nodes.get(qualified_name=codebase_qualified_name)
            except CodeConfluenceCodebase.DoesNotExist:
                raise ApplicationError(
                    f"Codebase not found: {codebase_qualified_name}", 
                    {"codebase": codebase_qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="CODEBASE_NOT_FOUND"
                )

            # Create package manager metadata node
            metadata_dict = {
                "qualified_name": f"{codebase_qualified_name}_package_manager_metadata",
                "dependencies": {k: v.model_dump() for k, v in package_manager_metadata.dependencies.items()},
                "package_manager": package_manager_metadata.package_manager,
                "programming_language": package_manager_metadata.programming_language,
                "programming_language_version": package_manager_metadata.programming_language_version,
                "project_version": package_manager_metadata.project_version,
                "description": package_manager_metadata.description,
                "license": package_manager_metadata.license,
                "package_name": package_manager_metadata.package_name,
                "entry_points": package_manager_metadata.entry_points,
                "authors": package_manager_metadata.authors or [],
            }

            metadata_results = await self._handle_node_creation(CodeConfluencePackageManagerMetadata, metadata_dict)
            if not metadata_results:
                raise ApplicationError(
                    f"Failed to create package manager metadata for {codebase_qualified_name}", 
                    {"codebase": codebase_qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="METADATA_CREATION_ERROR"
                )

            metadata_node: CodeConfluencePackageManagerMetadata = metadata_results[0]

            # Connect metadata to codebase using safe connect
            await self._safe_connect(codebase_node, 'package_manager_metadata', metadata_node)

            logger.debug(f"Successfully inserted package manager metadata for {codebase_qualified_name}")

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert package manager metadata for {codebase_qualified_name}"
            logger.error(f"{error_msg} | error_type={type(e).__name__} | error={str(e)} | status=failed")
            
            # Capture the traceback string
            tb_str = traceback.format_exc()
            
            raise ApplicationError(
                error_msg,
                {"codebase": codebase_qualified_name},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                {"workflow_id": workflow_id_var.get("")},
                {"workflow_run_id": workflow_run_id_var.get("")},
                {"activity_name": activity_name_var.get("")},
                {"activity_id": activity_id_var.get("")},
                type="PACKAGE_METADATA_ERROR"
            )

    # #todo: we need to ingest packages into the graph database
    # async def insert_code_confluence_package(
    #     self, codebase_qualified_name: str, packages: List[UnoplatPackage]
    # ) -> None:
    #     """(method body omitted, deprecated)"""
        