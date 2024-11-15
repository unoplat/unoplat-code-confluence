from unoplat_code_confluence.parser.codebase_parser_strategy import CodebaseParserStrategy
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.configuration.external_config import ProgrammingLanguageMetadata
from typing import Dict, List
import os
from loguru import logger
from unoplat_code_confluence.parser.python.package_manager.package_manager_factory import PackageManagerStrategyFactory
from unoplat_code_confluence.parser.python.python_package_naming_strategy import PythonPackageNamingStrategy
from unoplat_code_confluence.parser.python.python_qualified_name_strategy import PythonQualifiedNameStrategy

class PythonCodebaseParser(CodebaseParserStrategy):
    
    def parse_codebase(self, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        workspace_name = local_workspace_path.rstrip('/').split('/')[-1]
        unoplat_codebase = UnoplatCodebase()
        unoplat_codebase.name = workspace_name
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}
        package_manager = programming_language_metadata.package_manager
        package_naming_strategy: PythonPackageNamingStrategy = PythonPackageNamingStrategy()
        qualified_name_strategy: PythonQualifiedNameStrategy = PythonQualifiedNameStrategy()
        
        # Get the package manager strategy
        try:
            package_manager_strategy = PackageManagerStrategyFactory.get_strategy(
                package_manager
            )
            processed_metadata = package_manager_strategy.process_metadata(local_workspace_path, programming_language_metadata)
            unoplat_codebase.package_manager_metadata = processed_metadata
            
        except Exception as e:
            logger.warning(str(e))
            #TODO: handle this
    
            
        for item in json_data:
            try:
                node: ChapiUnoplatNode = ChapiUnoplatNode.model_validate(item)
                
                if node.node_name == "default":
                    if node.file_path:
                        node.node_name = os.path.basename(node.file_path).split('.')[0]
                    else:
                        node.node_name = "unknown"
                
                node.qualified_name = qualified_name_strategy.get_qualified_name(
                    node_name=node.node_name, # type: ignore
                    node_file_path=node.file_path, # type: ignore
                    local_workspace_path=local_workspace_path,
                    codebase_name=unoplat_codebase.name
                )

                
                node.package = package_naming_strategy.get_package_name(
                    node.file_path, # type: ignore
                    local_workspace_path,
                    unoplat_codebase.name
                    )
                
                
                    
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

            except Exception as e:
                logger.error(f"Error processing node: {e}")
                
        unoplat_codebase.packages = unoplat_package_dict #type: ignore
        return unoplat_codebase 
    
    
        
        