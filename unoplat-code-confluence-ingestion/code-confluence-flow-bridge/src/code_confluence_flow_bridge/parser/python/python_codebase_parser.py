# Standard Library
from src.code_confluence_flow_bridge.models.chapi.chapi_class_global_fieldmodel import (
    ClassGlobalFieldModel,
)
from src.code_confluence_flow_bridge.models.chapi.chapi_node import ChapiNode
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_function import (
    UnoplatChapiForgeFunction,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_chapi_forge_node import (
    UnoplatChapiForgeNode,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import import (
    UnoplatImport,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_import_type import (
    ImportType,
)
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package import (
    UnoplatPackage,
)

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)
from src.code_confluence_flow_bridge.parser.codebase_parser_strategy import (
    CodebaseParserStrategy,
)
from src.code_confluence_flow_bridge.parser.python.in_class_dependency.sort_function_dependencies import (
    SortFunctionDependencies,
)
from src.code_confluence_flow_bridge.parser.python.node_variables.node_variables_parser import (
    NodeVariablesParser,
)
from src.code_confluence_flow_bridge.parser.python.python_extract_function_calls import PythonExtractFunctionCalls
from src.code_confluence_flow_bridge.parser.python.python_extract_inheritance import (
    PythonExtractInheritance,
)
from src.code_confluence_flow_bridge.parser.python.python_import_segregation_strategy import (
    PythonImportSegregationStrategy,
)
from src.code_confluence_flow_bridge.parser.python.python_link_nested_function import PythonLinkNestedFunction
from src.code_confluence_flow_bridge.parser.python.python_node_dependency_processor import (
    PythonNodeDependencyProcessor,
)
from src.code_confluence_flow_bridge.parser.python.python_package_naming_strategy import (
    PythonPackageNamingStrategy,
)
from src.code_confluence_flow_bridge.parser.python.python_qualified_name_strategy import (
    PythonQualifiedNameStrategy,
)
from src.code_confluence_flow_bridge.parser.python.utils.read_programming_file import (
    ProgrammingFileReader,
)
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import (
    CodeConfluenceTreeSitter,
)

import os
import json
from typing import Dict, List, Tuple

# Third Party
from loguru import logger
from pydantic import ValidationError


class PythonCodebaseParser(CodebaseParserStrategy):
    def __init__(self):
        self.python_extract_inheritance = PythonExtractInheritance()
        self.package_naming_strategy = PythonPackageNamingStrategy()
        self.qualified_name_strategy = PythonQualifiedNameStrategy()
        self.code_confluence_tree_sitter = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
        self.python_import_segregation_strategy = PythonImportSegregationStrategy(code_confluence_tree_sitter=self.code_confluence_tree_sitter)
        self.python_extract_function_calls = PythonExtractFunctionCalls(code_confluence_tree_sitter=self.code_confluence_tree_sitter)
        self.python_link_nested_function = PythonLinkNestedFunction(code_confluence_tree_sitter=self.code_confluence_tree_sitter)
        self.sort_function_dependencies = SortFunctionDependencies()
        self.python_node_dependency_processor = PythonNodeDependencyProcessor()
        self.node_variables_parser = NodeVariablesParser(code_confluence_tree_sitter=self.code_confluence_tree_sitter)

    # we handle procedural , class and mix of procedural and class nodes.
    def __preprocess_nodes(self, json_data: dict, local_workspace_path: str, source_directory: str, codebase_name: str) -> Tuple[Dict[str, List[UnoplatChapiForgeNode]], Dict[str, UnoplatChapiForgeNode]]:
        """Preprocess nodes to extract qualified names and segregate imports."""
        file_path_nodes: Dict[str, List[UnoplatChapiForgeNode]] = {}
        qualified_names_dict: Dict[str, UnoplatChapiForgeNode] = {}

        for item in json_data:
            try:
                node: ChapiNode = ChapiNode.model_validate(item)
                unoplat_node: UnoplatChapiForgeNode = self.__common_node_processing(node, local_workspace_path, source_directory)

                # Add debug logging
                logger.debug("Processing node: {}", node.node_name)
                logger.debug("Qualified name: {}", unoplat_node.qualified_name)

                if unoplat_node.file_path not in file_path_nodes:
                    file_path_nodes[unoplat_node.file_path] = [unoplat_node]  # type: ignore
                else:
                    file_path_nodes[unoplat_node.file_path].append(unoplat_node)

                qualified_names_dict[unoplat_node.qualified_name] = unoplat_node

            except ValidationError as ve:
                logger.error("ValidationError while building qualified name map: {}", ve)
                try:
                    logger.error("Offending item: {}", json.dumps(item, indent=2)[:1000])
                except Exception:
                    logger.error("Offending item could not be serialized for logging.")
                continue
            except Exception as e:
                logger.error("Error building qualified name map: {}", e)

        # # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
        # # Add debug logging for file_path_nodes count
        # logger.info(f"Total number of file_path_nodes after preprocessing: {len(file_path_nodes)}")
        # logger.debug(f"File paths processed: {list(file_path_nodes.keys())}")
        # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ===============

        return file_path_nodes, qualified_names_dict
    
    def __get_import_prefix(self, local_workspace_path: str, source_directory: str):
        import_prefix = os.path.relpath(
            local_workspace_path,  # From workspace path
            source_directory      # To source root
        )
        logger.debug("Computed import prefix: {} (from '{}' to '{}')", import_prefix, local_workspace_path, source_directory)
        return import_prefix
        
    
    
    def __common_node_processing(
        self,
        node: ChapiNode,
        local_workspace_path: str,
        source_directory: str
    ) -> UnoplatChapiForgeNode:
        """Process common node attributes and imports.
        
        Args:
            node: The ChapiNode to process
            local_workspace_path: Path like /Users/user/projects/myproject/src/code_confluence_flow_bridge
            source_directory: Path like /Users/user/projects/myproject
        """
        logger.debug("Starting __common_node_processing for node: {} (file_path={})", getattr(node, 'node_name', None), getattr(node, 'file_path', None))
        qualified_name: str = "unknown"
        try:
            if node.node_name == "default":
                logger.debug("Node name is 'default', attempting to set from file_path: {}", node.file_path)
                node.node_name = os.path.basename(node.file_path).split(".")[0] if node.file_path else "unknown"
                logger.debug("Node name set to: {}", node.node_name)
            
            if not node.node_name:
                try:
                    logger.error("JSON item missing 'node_name': {}", node.model_dump_json(indent=2))
                except Exception:
                    logger.error("JSON item missing 'node_name' could not be serialized for logging.")
            
            # Fail fast when we still don't have both a node name and a file path
            if not node.node_name or not node.file_path:
                raise ValueError(
                    f"Cannot build qualified name: node_name={node.node_name!r}, file_path={node.file_path!r}"
                )

            # Get the import prefix by finding the path from workspace to source root
            import_prefix = self.__get_import_prefix(
                local_workspace_path=local_workspace_path,
                source_directory=source_directory
            )
            logger.debug("Import prefix computed: {}", import_prefix)

            if node.node_name and node.file_path:  # Type guard for linter
                logger.debug(
                    "Attempting to get qualified name with node_name={}, node_file_path={}, node_type={}, import_prefix={}",
                    node.node_name, node.file_path, node.type, import_prefix
                )
                qualified_name = self.qualified_name_strategy.get_qualified_name(
                    node_name=node.node_name, 
                    node_file_path=node.file_path, 
                    node_type=node.type,
                    import_prefix=import_prefix
                )
                logger.debug("Qualified name formed: {}", qualified_name)
            else:
                logger.warning(
                    "Cannot form qualified name: node_name={}, node_file_path={}", node.node_name, node.file_path
                )

            import_prefix_directory = import_prefix.replace(os.sep, ".")
            logger.debug("Import prefix directory for import segregation: {}", import_prefix_directory)

            # segregating imports
            imports_dict: Dict[ImportType, List[UnoplatImport]] = self.python_import_segregation_strategy.process_imports(
                source_directory=import_prefix_directory,  # Now correctly "src.code_confluence_flow_bridge"
                class_metadata=node
            )
            logger.debug("Imports segregated: {{ {} }}", ', '.join(f'{k.value}: {[str(i) for i in v]}' for k, v in imports_dict.items()))

            # Extracting inheritance
            if imports_dict and ImportType.INTERNAL in imports_dict:
                logger.debug("Extracting inheritance for node: {}", node.node_name)
                final_internal_imports = self.python_extract_inheritance.extract_inheritance(
                    node, 
                    imports_dict[ImportType.INTERNAL]
                )
                imports_dict[ImportType.INTERNAL] = final_internal_imports
                logger.debug(f"Final internal imports after inheritance extraction: {[str(i) for i in final_internal_imports]}")

            if node.file_path:  # Type guard for linter
                logger.debug(f"Attempting to get package name for file_path={node.file_path}, import_prefix={import_prefix}")
                node.package = self.package_naming_strategy.get_package_name(
                    file_path=node.file_path,
                    import_prefix=import_prefix
                )
                logger.debug(f"Package name set to: {node.package}")

        except Exception as e:
            logger.error(f"Exception in __common_node_processing: {e}", exc_info=True)
            try:
                logger.error(f"Offending node JSON: {node.model_dump_json(indent=2)[:1000]}")
            except Exception:
                pass

        logger.debug(
            f"Returning UnoplatChapiForgeNode with qualified_name={qualified_name}, node_name={node.node_name}, file_path={node.file_path}, package={getattr(node, 'package', None)}"
        )
        return UnoplatChapiForgeNode.from_chapi_node(
            chapi_node=node,
            qualified_name=qualified_name,
            segregated_imports=imports_dict if 'imports_dict' in locals() and imports_dict is not None else {}
        )

    def parse_codebase(
        self, 
        codebase_name: str, 
        json_data: dict, 
        local_workspace_path: str, 
        source_directory: str, 
        programming_language_metadata: ProgrammingLanguageMetadata
    ) -> List[UnoplatPackage]:
        """Parse the entire codebase.

        First preprocesses nodes to extract qualified names and segregate imports,
        then processes dependencies for each node using that map.
        """
        # Phase 1: Preprocess nodes
        preprocessed_result: Tuple[Dict[str, List[UnoplatChapiForgeNode]], Dict[str, UnoplatChapiForgeNode]] = self.__preprocess_nodes(
            json_data, 
            local_workspace_path, 
            source_directory, 
            codebase_name
        )
        preprocessed_file_path_nodes: Dict[str, List[UnoplatChapiForgeNode]] = preprocessed_result[0]
        preprocessed_qualified_name_dict = preprocessed_result[1]

        # Phase 2: Process dependencies using the map
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}
        
        import_prefix_directory = self.__get_import_prefix(
            local_workspace_path=local_workspace_path, 
            source_directory=source_directory
        ).replace(os.sep, ".")

        for file_path, nodes in preprocessed_file_path_nodes.items():  # file_path: str, nodes: List[UnoplatChapiForgeNode] from unoplat_chapi_forge_node.py
            try:
                # Process file-level data
                content_of_file = ProgrammingFileReader.read_file(file_path)
                global_variables: List[ClassGlobalFieldModel] = self.node_variables_parser.parse_global_variables(content_of_file)
                dependent_classes: List[str] = self.python_node_dependency_processor.process_dependencies(nodes[0], preprocessed_qualified_name_dict)
                
                # Create a file object to track file metadata
                file_obj = UnoplatFile(
                    file_path=file_path,
                    content=content_of_file,
                    nodes=[]  # Will populate with nodes later
                )
                
                # # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
                # logger.debug(f"Created UnoplatFile object for: {file_path}")
                # # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============
                
                if nodes[0].segregated_imports:
                    internal_imports: List[UnoplatImport] = nodes[0].segregated_imports[ImportType.INTERNAL] 
                    # This call will update each function's "function_calls" attribute
                nodes = self.python_extract_function_calls.extract_function_calls(
                    file_path_nodes={file_path: nodes},
                    imports=internal_imports,
                    entire_code=content_of_file
                )[file_path]
                 
                # Process all nodes from file
                for node in nodes:
                    self.python_link_nested_function.process_nested_functions(
                        functions=node.functions,
                        file_content=content_of_file
                    )
                    
                    sorted_functions: List[UnoplatChapiForgeFunction] = self.sort_function_dependencies.sort_function_dependencies(
                        functions=node.functions, 
                        node_type=node.type
                    )
                    node.global_variables = global_variables

                    if sorted_functions:
                        node.functions = sorted_functions

                    if node.node_name != nodes[0].node_name:
                        node.dependent_internal_classes = dependent_classes
                    
                    # Add node to file object
                    file_obj.nodes.append(node)
                    
                    # Build package structure using the desired root prefix
                    if node.package:
                        # If node.package starts with the desired prefix, collapse it into one token
                        if node.package.startswith(import_prefix_directory):
                            suffix = node.package[len(import_prefix_directory):].strip(".")
                            if suffix:
                                package_parts = [import_prefix_directory] + suffix.split(".")
                            else:
                                package_parts = [import_prefix_directory]
                        else:
                            # Otherwise, just split the node.package on the dot
                            package_parts = node.package.split(".")

                        current_package = unoplat_package_dict
                        full_package_name = ""
                        
                        for i, part in enumerate(package_parts):
                            full_package_name = part if i == 0 else f"{full_package_name}.{part}"
                            
                            if full_package_name not in current_package:
                                current_package[full_package_name] = UnoplatPackage(name=full_package_name)
                                
                            if i == len(package_parts) - 1:
                                # Check if this file already exists in the package's files dictionary
                                # If it does, use the existing file object instead of the new one
                                if file_path in current_package[full_package_name].files:
                                    # Reuse the existing file object
                                    file_obj = current_package[full_package_name].files[file_path]
                                else:
                                    # Add the new file object to the files dictionary
                                    current_package[full_package_name].files[file_path] = file_obj
                            else:
                                current_package = current_package[full_package_name].sub_packages  # type: ignore
                                
            except Exception as e:
                logger.error(f"Error processing node dependencies: {e}")
        
        packages: List[UnoplatPackage] = list(unoplat_package_dict.values()) if unoplat_package_dict else []
        
        # ============== BEGIN DEBUG CODE (REMOVE AFTER TESTING) ==============
        # Count total files across all packages
        # total_files = 0
        # file_paths = set()
        # package_file_counts = {}  # Dictionary to track files per package
        
        # def count_files_recursive(pkg_list, parent_path=""):
        #     nonlocal total_files, file_paths, package_file_counts
        #     for pkg in pkg_list:
        #         current_path = f"{parent_path}.{pkg.name}" if parent_path else pkg.name
                
        #         # Initialize count for this package
        #         if current_path not in package_file_counts:
        #             package_file_counts[current_path] = 0
                    
        #         if pkg.files:
        #             pkg_file_count = 0
        #             for file_path in pkg.files.keys():
        #                 if file_path not in file_paths:
        #                     file_paths.add(file_path)
        #                     total_files += 1
        #                     pkg_file_count += 1
                    
        #             # Update count for this package
        #             package_file_counts[current_path] = pkg_file_count
        #             logger.debug(f"Package '{current_path}' contains {pkg_file_count} files")
                    
        #         if pkg.sub_packages:
        #             count_files_recursive(pkg.sub_packages.values(), current_path)
        
        # count_files_recursive(packages)
        
        # Log file counts per package
        # logger.info(f"File counts per package:")
        # for pkg_name, count in package_file_counts.items():
        #     logger.info(f"  - {pkg_name}: {count} files")
            
        # logger.info(f"Total number of unique UnoplatFile objects created: {total_files}")
        # logger.debug(f"Unique file paths: {list(file_paths)}")
        # ============== END DEBUG CODE (REMOVE AFTER TESTING) ==============
        
        return packages
