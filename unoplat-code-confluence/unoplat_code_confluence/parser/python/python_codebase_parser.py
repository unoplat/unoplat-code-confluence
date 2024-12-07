# Standard Library
import os
from typing import Dict, List, Tuple,Union

# Third Party
from loguru import logger

# First Party
from unoplat_code_confluence.configuration.settings import ProgrammingLanguage, ProgrammingLanguageMetadata
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_node import ChapiNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_codebase import \
    UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.data_models.chapi_forge.unoplat_package import UnoplatPackage
from unoplat_code_confluence.parser.codebase_parser_strategy import CodebaseParserStrategy
from unoplat_code_confluence.parser.confluence_tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.parser.python.function_calls.python_function_calls import PythonFunctionCalls
from unoplat_code_confluence.parser.python.in_class_dependency.sort_function_dependencies import SortFunctionDependencies
from unoplat_code_confluence.parser.python.package_manager.package_manager_factory import \
    PackageManagerStrategyFactory
from unoplat_code_confluence.parser.python.python_extract_inheritance import PythonExtractInheritance
from unoplat_code_confluence.parser.python.python_import_segregation_strategy import \
    PythonImportSegregationStrategy
from unoplat_code_confluence.parser.python.python_node_dependency_processor import PythonNodeDependencyProcessor
from unoplat_code_confluence.parser.python.python_package_naming_strategy import \
    PythonPackageNamingStrategy
from unoplat_code_confluence.parser.python.python_qualified_name_strategy import \
    PythonQualifiedNameStrategy



class PythonCodebaseParser(CodebaseParserStrategy):
    
    def __init__(self):
        self.python_extract_inheritance = PythonExtractInheritance()
        self.package_naming_strategy = PythonPackageNamingStrategy()
        self.qualified_name_strategy = PythonQualifiedNameStrategy()
        self.python_import_segregation_strategy = PythonImportSegregationStrategy()
        self.code_confluence_tree_sitter = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
        self.python_function_calls = PythonFunctionCalls(code_confluence_tree_sitter=self.code_confluence_tree_sitter)
        self.sort_function_dependencies = SortFunctionDependencies()
        self.python_node_dependency_processor = PythonNodeDependencyProcessor()
        
        
    # we handle procedural , class and mix of procedural and class nodes.
    def __preprocess_nodes(
        self, json_data: dict, local_workspace_path: str,codebase_name: str
    ) -> Tuple[Dict[str, List[UnoplatChapiForgeNode]],Dict[str,UnoplatChapiForgeNode]]:
        """Preprocess nodes to extract qualified names and segregate imports.
        
        Args:
            json_data: Raw JSON data of nodes
            local_workspace_path: Path to local workspace
            
        Returns:
            Dict mapping of preprocessed nodes
        """
        file_path_nodes: Dict[str, List[UnoplatChapiForgeNode]] = {}  # Track nodes by file path
        qualified_names_dict: Dict[str,UnoplatChapiForgeNode] = {}
        
        for item in json_data:
            try:
                node: ChapiNode = ChapiNode.model_validate(item)
                
            
                unoplat_node: UnoplatChapiForgeNode = self.__common_node_processing(node, local_workspace_path)
                
                
                if unoplat_node.file_path not in file_path_nodes:
                    file_path_nodes[unoplat_node.file_path] = [unoplat_node] #type: ignore
                else:
                    file_path_nodes[unoplat_node.file_path].append(unoplat_node)
                
                qualified_names_dict[unoplat_node.qualified_name] = unoplat_node        
                        
            except Exception as e:
                logger.error(f"Error building qualified name map: {e}")
        
        return file_path_nodes,qualified_names_dict

            
    def __common_node_processing(self, node: ChapiNode, local_workspace_path: str):
        if node.node_name == "default":
            node.node_name = (
                os.path.basename(node.file_path).split('.')[0]
                if node.file_path
                else "unknown"
            )
            
        if node.node_name and node.file_path:  # Type guard for linter
            qualified_name = self.qualified_name_strategy.get_qualified_name(
                node_name=node.node_name,
                node_file_path=node.file_path,
                local_workspace_path=local_workspace_path
            )
        
        # segregating imports
        imports_dict: Dict[ImportType, List[UnoplatImport]] = self.python_import_segregation_strategy.process_imports(node)
            
        # Extracting inheritance
            
        if imports_dict and ImportType.INTERNAL in imports_dict:
            final_internal_imports = self.python_extract_inheritance.extract_inheritance(
                node, 
                imports_dict[ImportType.INTERNAL]
            )
            imports_dict[ImportType.INTERNAL] = final_internal_imports
        
        # Todo: Add dependent nodes
        if node.file_path:  # Type guard for linter
            node.package = self.package_naming_strategy.get_package_name(
                node.file_path,
                local_workspace_path
            )
        if node.functions:
            self.__process_functions(node.functions)
                
        return UnoplatChapiForgeNode.from_chapi_node(chapi_node=node, qualified_name=qualified_name,segregated_imports=imports_dict if imports_dict is not None else {})        
    
    def __process_functions(self, functions: List[ChapiFunction]):
        for function in functions:
            function.function_calls = self.python_function_calls.get_function_calls(function.content)
    
    def parse_codebase(
        self, codebase_name: str, json_data: dict, local_workspace_path: str, 
        programming_language_metadata: ProgrammingLanguageMetadata
    ) -> UnoplatCodebase:
        """Parse the entire codebase.
        
        First preprocesses nodes to extract qualified names and segregate imports,
        then processes dependencies for each node using that map.
        """
        # Phase 1: Preprocess nodes
        preprocessed_nodes, qualified_name_dict = self.__preprocess_nodes(json_data, local_workspace_path, codebase_name)
        
        # Get package manager metadata
        try:
            package_manager_strategy = PackageManagerStrategyFactory.get_strategy(
                programming_language_metadata.package_manager
            )
            processed_metadata = package_manager_strategy.process_metadata(
                local_workspace_path, 
                programming_language_metadata
            )
        except Exception as e:
            logger.warning(f"Error processing package manager metadata: {e}")
            processed_metadata = None
        
        # Phase 2: Process dependencies using the map
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}
        
        for list_nodes in preprocessed_nodes.values():
            try:
                if len(list_nodes) == 1:   
                    node: UnoplatChapiForgeNode = list_nodes[0]
                    sorted_functions: List[UnoplatChapiForgeFunction] = self.sort_function_dependencies.sort_function_dependencies(functions=node.functions,node_type=node.type)
                    
                    if sorted_functions:
                        node.functions = sorted_functions
                    
                    # Generate dependent classes
                    self.python_node_dependency_processor.process_dependencies(node,qualified_node_dict=qualified_name_dict)
                    
                    # Build package structure
                    if node.package:  # Type guard for linter
                        package_parts = node.package.split('.')
                        current_package = unoplat_package_dict
                        full_package_name = ""
                        
                        for i, part in enumerate(package_parts):
                            full_package_name = part if i == 0 else f"{full_package_name}.{part}"
                            if full_package_name not in current_package:
                                current_package[full_package_name] = UnoplatPackage(name=full_package_name)
                            if i == len(package_parts) - 1:
                                current_package[full_package_name].nodes.append(node) #type: ignore
                            else:
                                current_package = current_package[full_package_name].sub_packages #type: ignore
                else:
                    sorted_nodes: List[UnoplatChapiForgeFunction] = self.sort_function_dependencies.sort_function_dependencies(functions=node.functions,node_type=node.type)
                        
                                    
                
            except Exception as e:
                logger.error(f"Error processing node dependencies: {e}")
       
        unoplat_codebase: UnoplatCodebase = UnoplatCodebase(
            name=codebase_name,
            packages=list(unoplat_package_dict.values())[0] if unoplat_package_dict else None,
            package_manager_metadata=processed_metadata, #type: ignore
            local_path=local_workspace_path
        ) #type: ignore
        return unoplat_codebase
    
    
        
        