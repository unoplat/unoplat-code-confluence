
# Standard Library
from typing import Dict

# Third Party
from loguru import logger

from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_project_dependency import UnoplatProjectDependency

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.python.package_manager.package_manager_strategy import PackageManagerStrategy
from src.code_confluence_flow_bridge.parser.python.package_manager.utils.requirements_utils import RequirementsUtils
from src.code_confluence_flow_bridge.parser.python.package_manager.utils.setup_parser import SetupParser


class PipStrategy(PackageManagerStrategy):
    def process_metadata(self, local_workspace_path: str, metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Process pip specific metadata from requirements files and setup.py.
        
        Args:
            local_workspace_path: Path to the project workspace
            metadata: Programming language metadata
            
        Returns:
            UnoplatPackageManagerMetadata containing parsed project information
        """
        try:
            # First parse requirements to get dependencies
            dependencies: Dict[str, UnoplatProjectDependency] = RequirementsUtils.parse_requirements_folder(local_workspace_path)
            
            # Create initial metadata with dependencies
            package_metadata = UnoplatPackageManagerMetadata(
                dependencies=dependencies,
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager
            )
            
            try:
                # Try to parse setup.py for additional metadata
                package_metadata = SetupParser.parse_setup_file(
                    local_workspace_path, 
                    package_metadata
                )
                # if we do not get python version fall back to the one taken from configuration           
                if package_metadata.programming_language_version is None:
                    package_metadata.programming_language_version = metadata.language_version # type: ignore
                    
            except FileNotFoundError:
                logger.warning("setup.py not found, using only requirements data")
            except Exception as e:
                logger.error(f"Error parsing setup.py: {str(e)}")
                
            return package_metadata
            
        except Exception as e:
            logger.error(f"Error processing pip metadata: {str(e)}")
            # Return basic metadata if parsing fails
            return UnoplatPackageManagerMetadata(
                dependencies={},
                programming_language=metadata.language.value,
                package_manager=metadata.package_manager
            )