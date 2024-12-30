# Standard Library
from pathlib import Path

# Third Party
from temporalio import activity

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_codebase import UnoplatCodebase
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import PackageManagerType, ProgrammingLanguage, ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_parser import PackageManagerParser


class PackageMetadataActivity:
    
    def __init__(self):
        self.package_manager_parser = PackageManagerParser()
    
    @activity.defn
    def run(self, local_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """
        Process package manager specific metadata
        
        Args:
            local_path: Local path to the codebase
            programming_language_metadata: Programming language metadata
            
        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
        """
        package_metadata: UnoplatPackageManagerMetadata = self.package_manager_parser.parse_package_metadata(local_workspace_path=local_path, programming_language_metadata=programming_language_metadata)
        
        return package_metadata
        
        
