import os
from typing import Dict, List
from pydantic import ValidationError
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.loader.iparse_json import IParseJson
from loguru import logger
from unoplat_code_confluence.markdownparser.isummariser import ISummariser
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict, local_workspace_path: str, programming_language: str) -> UnoplatCodebase:
        """Concrete implementation of the parse_json_to_nodes method."""
        unoplat_codebase = UnoplatCodebase()
        
        
        unoplat_package_dict: Dict[str,UnoplatPackage] = {}
        
        for item in json_data:
            try:
                
                node = ChapiUnoplatNode.model_validate(item)
                
                if node.node_name == "default":
                    node.node_name = os.path.basename(node.file_path).split('.')[0]
                
                if programming_language.lower() == 'python':
                    relative_path = os.path.relpath(node.file_path, local_workspace_path)
                    node.package = os.path.dirname(relative_path).replace(os.path.sep, '.')
                    node.package = node.package if node.package else 'root'
                
                
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
        unoplat_codebase.packages =  unoplat_package_dict
        
        return unoplat_codebase