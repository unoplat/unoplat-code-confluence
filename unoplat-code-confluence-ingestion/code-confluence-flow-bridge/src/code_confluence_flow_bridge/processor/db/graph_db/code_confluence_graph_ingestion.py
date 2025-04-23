# Standard Library

# Third Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_git_repository import UnoplatGitRepository
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import UnoplatPackage
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.models.workflow.parent_child_clone_metadata import ParentChildCloneMetadata
from src.code_confluence_flow_bridge.processor.db.graph_db.code_confluence_graph import CodeConfluenceGraph

import json
from typing import Any, List, Tuple, Union

from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons import (
    CodeConfluenceClass,
    CodeConfluenceInternalFunction,
    CodeConfluencePackage,
    CodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_codebase import CodeConfluenceCodebase
from unoplat_code_confluence_commons.graph_models.code_confluence_git_repository import CodeConfluenceGitRepository


class CodeConfluenceGraphIngestion:
    def __init__(self, code_confluence_env: EnvironmentSettings):
        self.code_confluence_graph = CodeConfluenceGraph(code_confluence_env=code_confluence_env)

    async def initialize(self) -> None:
        """Initialize graph connection and schema"""
        try:
            await self.code_confluence_graph.connect()
            await self.code_confluence_graph.create_schema()
            logger.info("Graph initialization complete")
        except Exception as e:
            logger.error(f"Failed to initialize graph: {str(e)}")
            raise

    async def close(self) -> None:
        """Close graph connection"""
        await self.code_confluence_graph.close()

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

                repo_results = await CodeConfluenceGitRepository.create_or_update(repo_dict)
                if not repo_results:
                    raise ApplicationError(message=f"Failed to create repository node: {qualified_name}", type="REPOSITORY_CREATION_ERROR", details=[{"repository": qualified_name}])

                repo_node = repo_results[0]
                logger.debug(f"Created repository node: {qualified_name}")

                # Create codebase nodes and establish relationships
                for codebase in git_repo.codebases:
                    codebase_qualified_name = f"{qualified_name}_{codebase.name}"

                    codebase_dict = {"qualified_name": codebase_qualified_name, "name": codebase.name, "readme": codebase.readme, "local_path": codebase.local_path}
                    parent_child_clone_metadata.codebase_qualified_names.append(codebase_qualified_name)

                    codebase_results = await CodeConfluenceCodebase.create_or_update(codebase_dict)
                    if not codebase_results:
                        raise ApplicationError(message=f"Failed to create codebase node: {codebase.name}", type="CODEBASE_CREATION_ERROR", details=[{"repository": qualified_name, "codebase": codebase.name}])

                    codebase_node = codebase_results[0]

                    # Establish relationships
                    await repo_node.codebases.connect(codebase_node)
                    await codebase_node.git_repository.connect(repo_node)

                logger.debug(f"Successfully ingested repository {qualified_name}")
                return parent_child_clone_metadata

        except Exception as e:
            error_msg = f"Failed to insert repository {qualified_name}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ApplicationError(message=error_msg, type="GRAPH_INGESTION_ERROR") from e

    async def insert_code_confluence_codebase_package_manager_metadata(self, codebase_qualified_name: str, package_manager_metadata: UnoplatPackageManagerMetadata) -> None:
        """
        Insert codebase package manager metadata into the graph database

        Args:
            codebase_qualified_name: Qualified name of the codebase
            package_manager_metadata: UnoplatPackageManagerMetadata containing package manager metadata
        """
        try:
            async with self.code_confluence_graph.transaction:
                # Use get() instead of filter() for unique index
                try:
                    codebase_node = await CodeConfluenceCodebase.nodes.get(qualified_name=codebase_qualified_name)
                except CodeConfluenceCodebase.DoesNotExist:
                    raise ApplicationError(message=f"Codebase not found: {codebase_qualified_name}", type="CODEBASE_NOT_FOUND")

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

                metadata_results = await CodeConfluencePackageManagerMetadata.create_or_update(metadata_dict)
                if not metadata_results:
                    raise ApplicationError(message=f"Failed to create package manager metadata for {codebase_qualified_name}", type="METADATA_CREATION_ERROR")

                metadata_node: CodeConfluencePackageManagerMetadata = metadata_results[0]

                # Connect metadata to codebase
                await codebase_node.package_manager_metadata.connect(metadata_node)

                logger.debug(f"Successfully inserted package manager metadata for {codebase_qualified_name}")

        except Exception as e:
            error_msg = f"Failed to insert package manager metadata for {codebase_qualified_name}"
            logger.error(f"{error_msg}: {str(e)}")
            raise ApplicationError(message=error_msg, type="PACKAGE_METADATA_ERROR")




    #todo: we need to ingest packages into the graph database
    async def insert_code_confluence_package(
        self, codebase_qualified_name: str, packages: List[UnoplatPackage]
    ) -> None:
        """
        Insert packages (with classes and functions) into the graph database.
        Expects a list of root packages, where each package may contain nested sub-packages.

        Args:
            codebase_qualified_name (str): The qualified name of the codebase
            packages (List[UnoplatPackage]): List of root packages from the parser
        """
        try:
            codebase_node: CodeConfluenceCodebase = await CodeConfluenceCodebase.nodes.get(
                qualified_name=codebase_qualified_name
            )
        except CodeConfluenceCodebase.DoesNotExist as e:
            raise ApplicationError(
                message=f"Codebase not found: {codebase_qualified_name}",
                type="CODEBASE_NOT_FOUND"
            ) from e

        async with self.code_confluence_graph.transaction:
            # Initialize stack with root packages
            # Each stack item is (package, parent_node, codebase_node)
            stack: List[Tuple[UnoplatPackage, Union[CodeConfluenceCodebase, CodeConfluencePackage]]] = [
                (pkg, codebase_node) for pkg in packages
            ]
            
            while stack:
                current_pkg, parent_node = stack.pop()
                
                # Skip packages without names
                if not current_pkg.name:
                    logger.warning("Skipping package with no name")
                    continue

                # Create package node
                pkg_name = current_pkg.name
                package_dict = {
                    "name": pkg_name,
                    "qualified_name": (
                        f"{parent_node.qualified_name}.{pkg_name}"
                        if hasattr(parent_node, "qualified_name")
                        else pkg_name
                    ),
                }

                package_results = await CodeConfluencePackage.create_or_update(package_dict)
                if not package_results:
                    raise ApplicationError(
                        message=f"Failed to create package node: {pkg_name}",
                        type="PACKAGE_CREATION_ERROR"
                    )
                package_node: CodeConfluencePackage = package_results[0]

                # Connect to parent and codebase
                if isinstance(parent_node, CodeConfluenceCodebase):
                    await parent_node.packages.connect(package_node)
                    await package_node.codebase.connect(parent_node)
                else:
                    await parent_node.sub_packages.connect(package_node)
                    await package_node.sub_packages.connect(parent_node)

                logger.debug(f"Created package node: {pkg_name}")

                # Process all classes in this package
                if current_pkg.nodes:
                    for _, nodes in current_pkg.nodes.items():
                        for node in nodes:
                            await self._process_class(node=node, package_node=package_node)

                # Add sub-packages to stack (in reverse order to maintain original order when popping)
                if current_pkg.sub_packages:
                    # Convert items to list and reverse it
                    sub_packages = list(current_pkg.sub_packages.items())
                    for sub_pkg_name, sub_pkg in reversed(sub_packages):
                        if sub_pkg.name is None:
                            sub_pkg.name = sub_pkg_name
                        # Add to stack with current package as parent
                        stack.append((sub_pkg, package_node))

    async def _process_class(
        self, node: UnoplatChapiForgeNode, package_node: CodeConfluencePackage
    ) -> CodeConfluenceClass:
        """
        Process a single class node and connect it to the given package node.

        Args:
            node (UnoplatChapiForgeNode): The parsed node representing a class.
            package_node (CodeConfluencePackage): The parent package node.

        Returns:
            CodeConfluenceClass: The created/updated class node.
        """
        #logger.info(f"Processing class node: {node.model_dump()}")
        # Map fields from the UnoplatChapiForgeNode with proper JSON serialization
        
        
        class_dict: dict[str, Any] = {
            "name": node.qualified_name or "UnnamedClass",
            "qualified_name": f"{package_node.qualified_name}.{node.node_name}",
            "type_": node.type or "",
            "file_path": node.file_path or "",
            "module": node.module or "",
            "multiple_extend": node.multiple_extend or [],
            # Convert fields to JSON if they're Pydantic models
            "fields": [field.model_dump() for field in node.fields] if node.fields else [],
            "extend": node.extend or "",
            "position": node.position.model_dump() if node.position else {},
            "content": node.content or "",
            "comments_description": node.comments_description or "",
            # Convert segregated imports to JSON, using enum value as string key
            # Then in your dictionary comprehension:
            "segregated_imports": {
                k.value if hasattr(k, 'value') else str(k): [self.__serialize_import(imp) for imp in v]
                for k, v in (node.segregated_imports or {}).items()
            },
            "dependent_internal_classes": node.dependent_internal_classes or [],
            # Convert global variables to JSON
            "global_variables": [var.model_dump() if var else {}
                               for var in (node.global_variables or [])]
        }
        class_results = await CodeConfluenceClass.create_or_update(class_dict)
        if not class_results:
            raise ApplicationError(
                message=f"Failed to create class node for {getattr(node, 'node_name', 'UnnamedClass')}",
                type="CLASS_CREATION_ERROR"
            )
        class_node: CodeConfluenceClass = class_results[0]
        # Connect the class node to its package
        await package_node.classes.connect(class_node)
        await class_node.package.connect(package_node)
        logger.debug(f"Created class node: {getattr(node, 'node_name', 'UnnamedClass')}")

        # Process functions of the class node, if any
        if node.functions:
            for function in node.functions:
                await self._process_function(function=function, class_node=class_node)
        return class_node

    async def _process_function(
        self, function: UnoplatChapiForgeFunction, class_node: CodeConfluenceClass
    ) -> CodeConfluenceInternalFunction:
        """
        Process a single function node and connect it to the given class node.

        Args:
            function (UnoplatChapiForgeFunction): The parsed function object.
            class_node (CodeConfluenceClass): The parent class node.

        Returns:
            CodeConfluenceInternalFunction: The created/updated function node.
        """
        #logger.info(f"Processing function node: {function.model_dump()}")
        func_name: str = function.qualified_name if function.qualified_name else "UnnamedFunction"
        function_dict: dict[str, Any] = {
            "name": func_name,
            "qualified_name": f"{class_node.qualified_name}.{func_name}",
            "return_type": function.return_type or "",
            # Convert function calls to JSON if they're Pydantic models
            "function_calls": [ call.model_dump() if call else {}
                for call in (function.function_calls or [])
            ],
            # Convert parameters to JSON
            "parameters": [
                param.model_dump() if param else {}
                for param in (function.parameters or [])
            ],
            "position": function.position.model_dump() if function.position else {},
            "body_hash": function.body_hash or 0,
            "content": function.content or "",
            "comments_description": function.comments_description or ""
        }
        function_results: list[CodeConfluenceInternalFunction] = await CodeConfluenceInternalFunction.create_or_update(function_dict)
        if not function_results:
            raise ApplicationError(
                message=f"Failed to create function node for {func_name}",
                type="FUNCTION_CREATION_ERROR"
            )
        function_node: CodeConfluenceInternalFunction = function_results[0]
        # Check relationship to avoid duplicates
        if await class_node.functions.is_connected(function_node):
            logger.debug(f"Function {func_name} already connected to class {class_node.qualified_name}")
            return function_node

        # Connect relationship on one side only
        await class_node.functions.connect(function_node)
        logger.debug(f"Created function node: {func_name}")
        return function_node
    
    def __serialize_import(self, imp):
    # If imp is a Pydantic model, dump it; if it's already a dict, use it directly.
        imp_data = imp.model_dump() if hasattr(imp, 'model_dump') else imp.copy()
        # Convert the 'import_type' field from an enum to its value (if needed)
        if "import_type" in imp_data and hasattr(imp_data["import_type"], "value"):
            imp_data["import_type"] = imp_data["import_type"].value
        return imp_data


    # --------------------------------------------------------------------------
    # End of added methods for package ingestion
    # --------------------------------------------------------------------------
        