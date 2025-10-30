import json
import traceback
from typing import Any, Dict, List, Optional, Type

from loguru import logger
from neo4j import AsyncManagedTransaction, AsyncSession, Record
from neomodel import AsyncStructuredNode, adb
from neomodel.exceptions import RequiredProperty, UniqueProperty
from sqlmodel import select
from temporalio.exceptions import ApplicationError

# 🐘 PostgreSQL models for framework lookup
from unoplat_code_confluence_commons.base_models import (
    Framework as PGFramework,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import (
    CodeConfluenceCodebase,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import (
    CodeConfluenceGitRepository,
)

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
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import (
    ParentChildCloneMetadata,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm


class CodeConfluenceGraphIngestion:
    async def _create_repository_txn(
        self, tx: AsyncManagedTransaction, repo_data: Dict[str, Any]
    ) -> Record:
        """
        Transaction function for creating or updating CodeConfluenceGitRepository node
        Based on domain model: repository_url (unique), repository_name, repository_metadata, readme
        """
        query = """
        MERGE (r:CodeConfluenceGitRepository {repository_url: $repository_url})
        ON CREATE SET
            r.qualified_name = $qualified_name,
            r.repository_name = $repository_name,
            r.repository_metadata = $repository_metadata,
            r.readme = $readme
        ON MATCH SET
            r.qualified_name = $qualified_name,
            r.repository_name = $repository_name,
            r.repository_metadata = $repository_metadata,
            r.readme = $readme
        RETURN r
        """
        result = await tx.run(query, repo_data)
        return await result.single()

    async def _create_codebase_and_relationships_txn(
        self, tx: AsyncManagedTransaction, codebase_data: Dict[str, Any]
    ) -> Record:
        """
        Transaction function for creating CodeConfluenceCodebase node and relationships
        Based on domain model: name, readme, root_packages, codebase_path, programming_language
        """
        query = """
        MATCH (r:CodeConfluenceGitRepository {qualified_name: $repo_qualified_name})
        MERGE (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
        ON CREATE SET
            c.name = $name,
            c.readme = $readme,
            c.root_packages = $root_packages,
            c.codebase_path = $codebase_path
        ON MATCH SET
            c.name = $name,
            c.readme = $readme,
            c.root_packages = $root_packages,
            c.codebase_path = $codebase_path
        MERGE (r)-[:CONTAINS_CODEBASE]->(c)
        MERGE (c)-[:PART_OF_GIT_REPOSITORY]->(r)
        RETURN c, r
        """
        result = await tx.run(query, codebase_data)
        return await result.single()

    async def _get_codebase_txn(
        self, tx: AsyncManagedTransaction, qualified_name: str
    ) -> Optional[Record]:
        """
        Transaction function for getting CodeConfluenceCodebase node
        """
        query = "MATCH (c:CodeConfluenceCodebase {qualified_name: $qualified_name}) RETURN c"
        result = await tx.run(query, {"qualified_name": qualified_name})
        return await result.single()

    def _build_package_manager_metadata_payload(
        self, metadata: UnoplatPackageManagerMetadata
    ) -> Dict[str, Any]:
        """
        Build simplified payload for package manager metadata node.

        Returns dict with:
        - dependencies (JSON string): Serialized grouped dependencies
        - package_manager (str): Package manager type
        - programming_language (str): Programming language
        - other_metadata (JSON string): All other non-empty fields
        """
        # Serialize grouped dependencies
        dependencies_json = (
            json.dumps(
                {
                    group: {pkg: dep.model_dump() for pkg, dep in packages.items()}
                    for group, packages in metadata.dependencies.items()
                }
            )
            if metadata.dependencies
            else "{}"
        )

        # Build other_metadata from non-empty fields only
        other_fields = {}
        field_mapping = {
            "programming_language_version": metadata.programming_language_version,
            "project_version": metadata.project_version,
            "description": metadata.description,
            "license": metadata.license,
            "package_name": metadata.package_name,
            "entry_points": metadata.entry_points,
            "scripts": metadata.scripts,
            "binaries": metadata.binaries,
            "authors": metadata.authors,
            "homepage": metadata.homepage,
            "repository": metadata.repository,
            "documentation": metadata.documentation,
            "keywords": metadata.keywords,
            "maintainers": metadata.maintainers,
            "readme": metadata.readme,
        }

        for key, value in field_mapping.items():
            if value is not None and value != [] and value != {}:
                other_fields[key] = value

        return {
            "dependencies": dependencies_json,
            "package_manager": metadata.package_manager,
            "programming_language": metadata.programming_language,
            "other_metadata": json.dumps(other_fields) if other_fields else "{}",
        }

    async def _create_package_manager_metadata_and_relationship_txn(
        self, tx: AsyncManagedTransaction, metadata_data: Dict[str, Any]
    ) -> Record:
        """
        Transaction function for creating CodeConfluencePackageManagerMetadata node and relationship.
        Now stores only 4 core fields: dependencies, other_metadata, package_manager, programming_language.
        """
        query = """
        MATCH (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
        MERGE (m:CodeConfluencePackageManagerMetadata {qualified_name: $metadata_qualified_name})
        ON CREATE SET
            m.dependencies = $dependencies,
            m.other_metadata = $other_metadata,
            m.package_manager = $package_manager,
            m.programming_language = $programming_language
        ON MATCH SET
            m.dependencies = $dependencies,
            m.other_metadata = $other_metadata,
            m.package_manager = $package_manager,
            m.programming_language = $programming_language
        MERGE (c)-[:HAS_PACKAGE_MANAGER_METADATA]->(m)
        RETURN m, c
        """
        result = await tx.run(query, metadata_data)
        return await result.single()

    async def _create_framework_and_relationships_txn(
        self, tx: AsyncManagedTransaction, framework_data: Dict[str, Any]
    ) -> Record:
        """
        Transaction function for creating CodeConfluenceFramework node and bidirectional relationships
        Based on domain model: qualified_name (unique), language, library
        """
        query = """
        MATCH (c:CodeConfluenceCodebase {qualified_name: $codebase_qualified_name})
        MERGE (f:CodeConfluenceFramework {qualified_name: $framework_qualified_name})
        ON CREATE SET
            f.language = $language,
            f.library = $library
        ON MATCH SET
            f.language = $language,
            f.library = $library
        MERGE (c)-[:USES_FRAMEWORK]->(f)
        MERGE (f)-[:USED_BY]->(c)
        RETURN f, c
        """
        result = await tx.run(query, framework_data)
        return await result.single()

    def _get_node_identifier(self, node: Any) -> str:
        """
        Get the appropriate identifier for a node for logging purposes.

        Args:
            node: The node to get identifier for

        Returns:
            str: The identifier value
        """
        # CodeConfluenceFile inherits from AsyncStructuredNode and uses file_path as unique identifier
        if hasattr(node, "file_path") and node.file_path:
            return node.file_path
        # CodeConfluenceAnnotation inherits from AsyncStructuredNode and uses name as unique identifier
        elif (
            hasattr(node, "name") and node.name and not hasattr(node, "qualified_name")
        ):
            return node.name
        # All BaseNode-derived classes use qualified_name
        elif hasattr(node, "qualified_name") and node.qualified_name:
            return node.qualified_name
        # Fallback to string representation
        else:
            return str(node)

    async def _safe_connect(
        self, source_node: Any, relationship_attr: str, target_node: Any
    ) -> bool:
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
                    target_id,
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
                    target_id,
                )
                return True
        except Exception as e:
            # Log the error but don't fail the application
            logger.warning(
                "Failed to create relationship {}.{} -> {}: {}. Proceeding gracefully.",
                source_node.__class__.__name__,
                relationship_attr,
                target_node.__class__.__name__,
                str(e),
            )
            return False

    async def _handle_node_creation(
        self, node_class: Type[AsyncStructuredNode], node_dict: dict
    ) -> List[AsyncStructuredNode]:
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
            # Use create_or_update for single node upsert behavior
            results = await node_class.create_or_update(node_dict)
            if results:
                logger.info(
                    "Node created/updated successfully",
                    node_class=node_class.__name__,
                    qualified_name=node_dict.get("qualified_name"),
                    count=len(results),
                )
                return results
            else:
                logger.error(
                    "create_or_update returned empty results",
                    node_class=node_class.__name__,
                    qualified_name=node_dict.get("qualified_name"),
                )
                return []
        except UniqueProperty as e:
            logger.warning(
                "Node already exists, retrieving existing",
                node_class=node_class.__name__,
                qualified_name=node_dict.get("qualified_name"),
                error=str(e),
            )
            # Try to retrieve the existing node by unique properties
            try:
                # Find unique index properties in the node dict
                for prop_name, value in node_dict.items():
                    if hasattr(node_class, prop_name):
                        prop = getattr(node_class, prop_name)
                        if hasattr(prop, "unique_index") and prop.unique_index:
                            existing_nodes = await node_class.nodes.filter(
                                **{prop_name: value}
                            ).all()
                            if existing_nodes:
                                return [
                                    existing_nodes[0]
                                ]  # Return as list for consistency
                # If no unique property found, try qualified_name (all nodes have this from BaseNode)
                if "qualified_name" in node_dict:
                    existing_nodes = await node_class.nodes.filter(
                        qualified_name=node_dict["qualified_name"]
                    ).all()
                    if existing_nodes:
                        return [existing_nodes[0]]
            except Exception as retrieval_error:
                logger.error(
                    "Failed to retrieve existing node after UniqueProperty error",
                    node_class=node_class.__name__,
                    qualified_name=node_dict.get("qualified_name"),
                    error=str(retrieval_error),
                )
            return []
        except RequiredProperty as e:
            logger.error(
                "Missing required property, cannot proceed with node creation",
                node_class=node_class.__name__,
                qualified_name=node_dict.get("qualified_name"),
                error=str(e),
            )
            return []
        except Exception as e:
            tb_str = traceback.format_exc()
            logger.error(
                "Unexpected error during node creation",
                node_class=node_class.__name__,
                qualified_name=node_dict.get("qualified_name"),
                error=str(e),
                traceback=tb_str,
            )
            return []

            async with adb.transaction:
                # Create repository node
                repo_dict = {
                    "qualified_name": qualified_name,
                    "repository_url": git_repo.repository_url,
                    "repository_name": git_repo.repository_name,
                    "repository_metadata": git_repo.repository_metadata,
                    "readme": git_repo.readme,
                    "github_organization": git_repo.github_organization,
                }

                # 🔍 Add verbose logging to aid debugging CI-only failures
                logger.debug(
                    "Attempting to create CodeConfluenceGitRepository with properties: {}",
                    repo_dict,
                )

                repo_results = await self._handle_node_creation(
                    CodeConfluenceGitRepository, repo_dict
                )
                if not repo_results:
                    raise ApplicationError(
                        f"Failed to create repository node: {qualified_name}",
                        {"repository": qualified_name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="REPOSITORY_CREATION_ERROR",
                    )

                repo_node = repo_results[0]
                logger.debug("Created repository node: {}", qualified_name)

                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_qualified_name = f"{qualified_name}_{codebase.name}"

                    codebase_dict = {
                        "qualified_name": codebase_qualified_name,
                        "name": codebase.name,
                        "readme": codebase.readme,
                        "root_packages": codebase.root_packages,
                        "codebase_path": codebase.codebase_path,
                    }
                    parent_child_clone_metadata.codebase_qualified_names.append(
                        codebase_qualified_name
                    )

                    logger.debug(
                        "Attempting to create CodeConfluenceCodebase with properties: {}",
                        codebase_dict,
                    )
                    codebase_results = await self._handle_node_creation(
                        CodeConfluenceCodebase, codebase_dict
                    )
                    if not codebase_results:
                        raise ApplicationError(
                            f"Failed to create codebase node: {codebase.name}",
                            {"repository": qualified_name},
                            {"codebase": codebase.name},
                            {"workflow_id": workflow_id_var.get("")},
                            {"workflow_run_id": workflow_run_id_var.get("")},
                            {"activity_name": activity_name_var.get("")},
                            {"activity_id": activity_id_var.get("")},
                            type="CODEBASE_CREATION_ERROR",
                        )

                    codebase_node = codebase_results[0]

                    # Establish relationships using safe connect
                    await self._safe_connect(repo_node, "codebases", codebase_node)
                    await self._safe_connect(codebase_node, "git_repository", repo_node)

                logger.debug("Successfully ingested repository {}", qualified_name)
                return parent_child_clone_metadata

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(
                "{} | error_type={} | error={} | status=failed",
                error_msg,
                type(e).__name__,
                str(e),
            )

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
                type="GRAPH_INGESTION_ERROR",
            ) from e

    async def insert_code_confluence_git_repo_managed(
        self, session: AsyncSession, git_repo: UnoplatGitRepository
    ) -> ParentChildCloneMetadata:
        """
        NEW METHOD: Insert a git repository into the graph database using managed transactions with raw Cypher

        Args:
            session: Neo4j async session for managed transactions
            git_repo: UnoplatGitRepository containing git repository data

        Returns:
            ParentChildCloneMetadata: Metadata about created nodes

        Raises:
            ApplicationError: If repository insertion fails
        """
        qualified_name = f"{git_repo.github_organization}_{git_repo.repository_name}"
        parent_child_clone_metadata = ParentChildCloneMetadata(
            repository_qualified_name=qualified_name, codebase_qualified_names=[]
        )

        try:
            # Create repository node using raw Cypher MERGE - only use properties from domain model
            repo_data = {
                "qualified_name": qualified_name,
                "repository_url": git_repo.repository_url,
                "repository_name": git_repo.repository_name,
                "repository_metadata": json.dumps(git_repo.repository_metadata)
                if git_repo.repository_metadata
                else "{}",
                "readme": git_repo.readme,
                # Note: github_organization not in domain model, using qualified_name pattern instead
            }

            logger.debug("Creating repository with managed transaction: {}", repo_data)

            # Execute repository creation using managed transaction
            repo_record = await session.execute_write(
                self._create_repository_txn, repo_data
            )
            if not repo_record:
                raise ApplicationError(
                    f"Failed to create repository node: {qualified_name}",
                    {"repository": qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="REPOSITORY_CREATION_ERROR",
                )

            logger.debug("Created repository node: {}", qualified_name)

            # Create codebase nodes and relationships using managed transactions
            for codebase in git_repo.codebases:
                codebase_qualified_name = f"{qualified_name}_{codebase.name}"
                parent_child_clone_metadata.codebase_qualified_names.append(
                    codebase_qualified_name
                )

                codebase_data = {
                    "codebase_qualified_name": codebase_qualified_name,
                    "repo_qualified_name": qualified_name,
                    "name": codebase.name,
                    "readme": codebase.readme,
                    "root_packages": codebase.root_packages,
                    "codebase_path": codebase.codebase_path,
                    # Note: programming_language set separately based on detection
                }

                logger.debug(
                    "Creating codebase with managed transaction: {}", codebase_data
                )

                # Execute codebase creation and relationships using managed transaction
                codebase_record = await session.execute_write(
                    self._create_codebase_and_relationships_txn, codebase_data
                )
                if not codebase_record:
                    raise ApplicationError(
                        f"Failed to create codebase node: {codebase.name}",
                        {"repository": qualified_name},
                        {"codebase": codebase.name},
                        {"workflow_id": workflow_id_var.get("")},
                        {"workflow_run_id": workflow_run_id_var.get("")},
                        {"activity_name": activity_name_var.get("")},
                        {"activity_id": activity_id_var.get("")},
                        type="CODEBASE_CREATION_ERROR",
                    )

            logger.debug("Successfully ingested repository {}", qualified_name)
            return parent_child_clone_metadata

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(
                "{} | error_type={} | error={} | status=failed",
                error_msg,
                type(e).__name__,
                str(e),
            )

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
                type="GRAPH_INGESTION_ERROR",
            ) from e

    async def insert_code_confluence_codebase_package_manager_metadata_managed(
        self,
        session: AsyncSession,
        codebase_qualified_name: str,
        package_manager_metadata: UnoplatPackageManagerMetadata,
    ) -> None:
        """
        NEW METHOD: Insert codebase package manager metadata using managed transactions with raw Cypher

        Args:
            session: Neo4j async session for managed transactions
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: UnoplatPackageManagerMetadata containing package manager metadata
        """
        try:
            # First verify codebase exists using managed transaction
            codebase_record = await session.execute_read(
                self._get_codebase_txn, codebase_qualified_name
            )
            if not codebase_record:
                raise ApplicationError(
                    f"Codebase not found: {codebase_qualified_name}",
                    {"codebase": codebase_qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="CODEBASE_NOT_FOUND",
                )

            # Create package manager metadata node and relationship using managed transaction
            payload = self._build_package_manager_metadata_payload(
                package_manager_metadata
            )

            metadata_data = {
                "codebase_qualified_name": codebase_qualified_name,
                "metadata_qualified_name": f"{codebase_qualified_name}_package_manager_metadata",
                **payload,
            }

            logger.debug(
                "Creating package manager metadata with managed transaction: {}",
                metadata_data,
            )

            metadata_record = await session.execute_write(
                self._create_package_manager_metadata_and_relationship_txn,
                metadata_data,
            )
            if not metadata_record:
                raise ApplicationError(
                    f"Failed to create package manager metadata for {codebase_qualified_name}",
                    {"codebase": codebase_qualified_name},
                    {"workflow_id": workflow_id_var.get("")},
                    {"workflow_run_id": workflow_run_id_var.get("")},
                    {"activity_name": activity_name_var.get("")},
                    {"activity_id": activity_id_var.get("")},
                    type="METADATA_CREATION_ERROR",
                )

            logger.debug(
                "Successfully inserted package manager metadata for {}",
                codebase_qualified_name,
            )

        except Exception as e:
            # Capture detailed error information
            error_msg = f"Failed to insert package manager metadata for {codebase_qualified_name}"
            logger.error(
                "{} | error_type={} | error={} | status=failed",
                error_msg,
                type(e).__name__,
                str(e),
            )

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
                type="PACKAGE_METADATA_ERROR",
            )

    async def sync_frameworks_for_codebase_managed(
        self,
        session: AsyncSession,
        codebase_qualified_name: str,
        package_manager_metadata: UnoplatPackageManagerMetadata,
    ) -> None:
        """
        NEW METHOD: Sync framework nodes using managed transactions with raw Cypher

        PostgreSQL queries run in their own session context (separate from Neo4j).
        Neo4j operations use managed transactions.

        Args:
            session: Neo4j async session for managed transactions
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: UnoplatPackageManagerMetadata containing dependencies
        """
        try:
            # PostgreSQL operations (completely separate from Neo4j)
            frameworks_to_create = []

            async with get_session_cm() as pg_session:
                logger.debug("Checking frameworks for {}", codebase_qualified_name)

                # Only check default group for framework detection
                default_dependencies = package_manager_metadata.dependencies.get(
                    "default", {}
                )
                for pkg_name, _ in default_dependencies.items():
                    # Only process if a matching Framework exists in Postgres
                    logger.debug("Checking for framework: {}", pkg_name)
                    stmt = select(PGFramework).where(PGFramework.library == pkg_name)
                    result = await pg_session.execute(stmt)
                    pg_framework = result.scalar_one_or_none()

                    if not pg_framework:
                        logger.debug("Unknown framework: {}", pkg_name)
                        continue  # Unknown framework – skip

                    lang = package_manager_metadata.programming_language
                    lib = pg_framework.library

                    framework_dict = {
                        "codebase_qualified_name": codebase_qualified_name,
                        "framework_qualified_name": f"{lang}.{lib}",
                        "language": lang,
                        "library": lib,
                    }
                    frameworks_to_create.append(framework_dict)

            if not frameworks_to_create:
                logger.debug("No frameworks to sync for {}", codebase_qualified_name)
                return

            # Neo4j operations using managed transactions
            logger.opt(lazy=True).debug(
                "Creating {} frameworks for {}",
                lambda: len(frameworks_to_create),
                lambda: codebase_qualified_name,
            )

            # Create framework nodes and relationships using managed transactions
            for framework_data in frameworks_to_create:
                # Level guard to prevent frequent debug logging in tight loop
                if logger.level("DEBUG").no <= logger._core.min_level:
                    logger.debug(
                        "Creating framework with managed transaction: {}",
                        framework_data,
                    )

                framework_record = await session.execute_write(
                    self._create_framework_and_relationships_txn, framework_data
                )
                if not framework_record:
                    logger.warning(
                        "Failed to create framework node: {}", framework_data
                    )
                    continue

            logger.opt(lazy=True).debug(
                "Successfully synced {} frameworks for {}",
                lambda: len(frameworks_to_create),
                lambda: codebase_qualified_name,
            )

        except Exception as sync_err:
            logger.warning(
                f"Framework sync failed for codebase {codebase_qualified_name}: {sync_err}",
            )
