import os
from typing import Dict
from pydantic import ValidationError
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.loader.iparse_json import IParseJson
from loguru import logger
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.loader.package_naming_factory import PackageNamingStrategyFactory
from unoplat_code_confluence.loader.package_naming_strategy import UnsupportedLanguageError

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict, local_workspace_path: str, programming_language: str) -> UnoplatCodebase:
        """Concrete implementation of the parse_json_to_nodes method."""
        unoplat_codebase = UnoplatCodebase()
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}
        
        # Get the appropriate package naming strategy
        try:
            package_naming_strategy = PackageNamingStrategyFactory.get_strategy(programming_language)
        except UnsupportedLanguageError:
            logger.warning(f"Skipping processing for unsupported language: {programming_language}")
            return unoplat_codebase
        
        for item in json_data:
            try:
                node = ChapiUnoplatNode.model_validate(item)
                
                if node.node_name == "default":
                    node.node_name = os.path.basename(node.file_path).split('.')[0]
                
                try:
                    # Use the strategy to determine package name
                    node.package = package_naming_strategy.get_package_name(
                        node.file_path,
                        local_workspace_path,
                        node.node_name
                    )
                    
                except UnsupportedLanguageError:
                    logger.warning(f"Skipping node processing for unsupported language: {programming_language}")
                    continue
                
                package_parts = node.package.split('.')
                current_package = unoplat_package_dict

                full_package_name = ""
                for i, part in enumerate(package_parts):
                    full_package_name = part if i == 0 else f"{full_package_name}.{part}"
                    if full_package_name not in current_package:
                        current_package[full_package_name] = UnoplatPackage(name=full_package_name)
                    if i == len(package_parts) - 1:
                        current_package[full_package_name].nodes.append(node)
                    else:
                        current_package = current_package[full_package_name].sub_packages

            except Exception as e:
                logger.error(f"Error processing node: {e}")
                
        unoplat_codebase.packages = unoplat_package_dict
        return unoplat_codebase