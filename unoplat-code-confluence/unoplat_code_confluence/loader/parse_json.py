from ast import Name
import os
from typing import Dict
from pydantic import ValidationError
from unoplat_code_confluence.configuration.external_config import ProgrammingLanguage
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.loader.iparse_json import IParseJson
from loguru import logger
from unoplat_code_confluence.data_models.chapi_unoplat_node import ChapiUnoplatNode
from unoplat_code_confluence.language_custom_parsing.package_naming.package_naming_factory import PackageNamingStrategyFactory
from unoplat_code_confluence.language_custom_parsing.package_naming.python.python_package_naming_strategy import PythonPackageNamingStrategy
from unoplat_code_confluence.configuration.external_config import ProgrammingLanguageMetadata
from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from unoplat_code_confluence.language_custom_parsing.package_manager.package_manager_factory import (
    PackageManagerStrategyFactory,
    UnsupportedPackageManagerError
)
from unoplat_code_confluence.language_custom_parsing.qualified_name.qualified_name_factory import (
    QualifiedNameStrategyFactory,
    UnsupportedLanguageError
)

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatCodebase:
        """Concrete implementation of the parse_json_to_nodes method."""
        workspace_name = local_workspace_path.rstrip('/').split('/')[-1]
        unoplat_codebase = UnoplatCodebase()
        unoplat_codebase.name  = workspace_name
        unoplat_package_dict: Dict[str, UnoplatPackage] = {}
        programming_language = programming_language_metadata.language.value
        package_manager = programming_language_metadata.package_manager
        package_naming_support : bool = False
        
        # Get the qualified name strategy
        try:
            qualified_name_strategy = QualifiedNameStrategyFactory.get_strategy(programming_language)
        except UnsupportedLanguageError as e:
            logger.error(f"Qualified name processing not supported for language: {programming_language}:{e}")
            raise
        
        # Get the package manager strategy
        try:
            package_manager_strategy = PackageManagerStrategyFactory.get_strategy(
                programming_language,
                package_manager
            )
            # Process metadata using the strategy
            processed_metadata: UnoplatPackageManagerMetadata = package_manager_strategy.process_metadata(local_workspace_path,programming_language_metadata)
            unoplat_codebase.package_manager_metadata= processed_metadata
            
        except (UnsupportedLanguageError, UnsupportedPackageManagerError) as e:
            logger.warning(str(e))
            #return unoplat_codebase
        
        # Get the appropriate package naming strategy
        try:
            package_naming_strategy = PackageNamingStrategyFactory.get_strategy(programming_language)
            package_naming_support = True
        except UnsupportedLanguageError:
            logger.warning(f"Skipping processing package name for  language: {programming_language}")
            
        
        for item in json_data:
            try:
                
                node: ChapiUnoplatNode = ChapiUnoplatNode.model_validate(item)
                
                if node.node_name == "default":
                    node.node_name = os.path.basename(node.file_path).split('.')[0]
                
                # Get qualified name using the strategy
                node.qualified_name = qualified_name_strategy.get_qualified_name(
                    node_name=node.node_name,
                    node_file_path=node.file_path,
                    local_workspace_path=local_workspace_path,
                    codebase_name=unoplat_codebase.name
                )

                if package_naming_support:
                    # Use the strategy to determine package name
                    node.package = package_naming_strategy.get_package_name(
                        node.file_path,
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
                        current_package[full_package_name].nodes.append(node)
                    else:
                        current_package = current_package[full_package_name].sub_packages

            except Exception as e:
                logger.error(f"Error processing node: {e}")
                
        unoplat_codebase.packages = unoplat_package_dict
        return unoplat_codebase