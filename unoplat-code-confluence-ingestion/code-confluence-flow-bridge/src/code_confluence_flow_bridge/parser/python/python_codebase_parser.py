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
from src.code_confluence_flow_bridge.parser.python.python_extract_inheritance import (
    PythonExtractInheritance,
)
from src.code_confluence_flow_bridge.parser.python.python_import_segregation_strategy import (
    PythonImportSegregationStrategy,
)
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
from typing import Dict, List, Tuple

# Third Party
from loguru import logger


class PythonCodebaseParser(CodebaseParserStrategy):
    def __init__(self):
        self.python_extract_inheritance = PythonExtractInheritance()
        self.package_naming_strategy = PythonPackageNamingStrategy()
        self.qualified_name_strategy = PythonQualifiedNameStrategy()
        self.python_import_segregation_strategy = PythonImportSegregationStrategy()
        self.code_confluence_tree_sitter = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
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
                logger.debug(f"Processing node: {node.node_name}")
                logger.debug(f"Qualified name: {unoplat_node.qualified_name}")

                if unoplat_node.file_path not in file_path_nodes:
                    file_path_nodes[unoplat_node.file_path] = [unoplat_node]  # type: ignore
                else:
                    file_path_nodes[unoplat_node.file_path].append(unoplat_node)

                qualified_names_dict[unoplat_node.qualified_name] = unoplat_node

            except Exception as e:
                logger.error(f"Error building qualified name map: {e}")

        # Add debug logging for final map
        logger.debug("Qualified names in dict:")
        for qname in qualified_names_dict.keys():
            logger.debug(f"  {qname}")

        return file_path_nodes, qualified_names_dict

    def __common_node_processing(self, node: ChapiNode, local_workspace_path: str, source_directory: str):
        """Process common node attributes and imports.
        
        Args:
            node: The ChapiNode to process
            local_workspace_path: Path like /Users/user/projects/myproject/src/code_confluence_flow_bridge
            source_directory: Path like /Users/user/projects/myproject
        """
        if node.node_name == "default":
            node.node_name = os.path.basename(node.file_path).split(".")[0] if node.file_path else "unknown"

        if node.node_name and node.file_path:  # Type guard for linter
            qualified_name = self.qualified_name_strategy.get_qualified_name(
                node_name=node.node_name, 
                node_file_path=node.file_path, 
                local_workspace_path=local_workspace_path, 
                node_type=node.type
            )
        
        # Get the import prefix by finding the path from workspace to source root
        # If local_workspace_path is /Users/user/projects/myproject/src/code_confluence_flow_bridge
        # And source_directory is /Users/user/projects/myproject
        # Then we want "src.code_confluence_flow_bridge" as the prefix
        import_prefix = os.path.relpath(
            local_workspace_path,  # From workspace path
            source_directory      # To source root
        ).replace(os.sep, ".")
        
        # segregating imports
        imports_dict: Dict[ImportType, List[UnoplatImport]] = self.python_import_segregation_strategy.process_imports(
            source_directory=import_prefix,  # Now correctly "src.code_confluence_flow_bridge"
            class_metadata=node
        )

        # Extracting inheritance
        if imports_dict and ImportType.INTERNAL in imports_dict:
            final_internal_imports = self.python_extract_inheritance.extract_inheritance(
                node, 
                imports_dict[ImportType.INTERNAL]
            )
            imports_dict[ImportType.INTERNAL] = final_internal_imports

        # Todo: Add dependent nodes
        if node.file_path:  # Type guard for linter
            node.package = self.package_naming_strategy.get_package_name(node.file_path, local_workspace_path)

        # TODO: enable below when archguard fixes the formatting issues of code content - be it class or function
        # node.fields = []
        # if node is of type class do parse class variables and instance variables and add them to node.class_variables
        # if node.type == "CLASS":
        #     node.fields = self.node_variables_parser.parse_class_variables(node.content, node.functions)

        # if node.functions:
        #     self.python_function_calls.process_functions(node.functions)

        return UnoplatChapiForgeNode.from_chapi_node(chapi_node=node, qualified_name=qualified_name, segregated_imports=imports_dict if imports_dict is not None else {})

    def parse_codebase(self, codebase_name: str, json_data: dict, local_workspace_path: str, source_directory: str, programming_language_metadata: ProgrammingLanguageMetadata) -> List[UnoplatPackage]:
        """Parse the entire codebase.

        First preprocesses nodes to extract qualified names and segregate imports,
        then processes dependencies for each node using that map.
        """
        # Phase 1: Preprocess nodes
        preprocessed_file_path_nodes, preprocessed_qualified_name_dict = self.__preprocess_nodes(json_data, local_workspace_path, source_directory, codebase_name)


        # Phase 2: Process dependencies using the map
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}

        for file_path, nodes in preprocessed_file_path_nodes.items():
            try:
                # TODO: enable when archguard fixes the formatting issues of code content - be it class or function
                # The operation of generating global variables should be done once per file even if there are multiple nodes in the file
                content_of_file = ProgrammingFileReader.read_file(file_path)
                global_variables: List[ClassGlobalFieldModel] = self.node_variables_parser.parse_global_variables(content_of_file)

                # The operation of figuring out dependent class should be done once per file even if there are multiple nodes in the file
                dependent_classes: List[str] = self.python_node_dependency_processor.process_dependencies(nodes[0], preprocessed_qualified_name_dict)

                # Process all nodes from file
                for node in nodes:
                    # TODO: check for interface and abstract class - what are types from chapi
                    sorted_functions: List[UnoplatChapiForgeFunction] = self.sort_function_dependencies.sort_function_dependencies(functions=node.functions, node_type=node.type)

                    # TODO: enable when archguard fixes the formatting issues of code content - be it class or function
                    node.global_variables = global_variables

                    if sorted_functions:
                        node.functions = sorted_functions

                    # Generate dependent classes
                    # skip first node since it is already processed
                    if node.node_name != nodes[0].node_name:
                        node.dependent_internal_classes = dependent_classes

                    # Build package structure
                    if node.package:
                        package_parts = node.package.split(".")
                        current_package = unoplat_package_dict
                        full_package_name = ""

                        for i, part in enumerate(package_parts):
                            full_package_name = part if i == 0 else f"{full_package_name}.{part}"
                            if full_package_name not in current_package:
                                current_package[full_package_name] = UnoplatPackage(name=full_package_name)
                            if i == len(package_parts) - 1:
                                # Add nodes to dict by file path
                                if file_path not in current_package[full_package_name].nodes:
                                    current_package[full_package_name].nodes[file_path] = []
                                current_package[full_package_name].nodes[file_path].append(node)
                            else:
                                current_package = current_package[full_package_name].sub_packages  # type: ignore
            except Exception as e:
                logger.error(f"Error processing node dependencies: {e}")
        
        packages: List[UnoplatPackage] = list(unoplat_package_dict.values()) if unoplat_package_dict else []
        
        return packages
