
import traceback

from loguru import logger
from temporalio.exceptions import ApplicationError
from unoplat_code_confluence_commons.programming_language_metadata import (
    ProgrammingLanguageMetadata,
)

from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_factory import (
    PackageManagerStrategyFactory,
    UnsupportedPackageManagerError,
)


class PackageManagerParser:
    def parse_package_metadata(self, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """
        Parse package metadata using the specified package manager.
        
        Args:
            local_workspace_path: Path to the local workspace
            programming_language_metadata: Programming language metadata with package manager specified
            
        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
            
        Raises:
            ApplicationError: If package manager is not specified or processing fails
        """
        try:
            if not programming_language_metadata.package_manager:
                error_msg = f"Package manager not specified for {local_workspace_path}"
                logger.error(
                    f"{error_msg} | language={programming_language_metadata.language.value}"
                )
                raise ApplicationError(
                    error_msg,
                    {"local_workspace_path": local_workspace_path},
                    {"language": programming_language_metadata.language.value},
                    type="PACKAGE_MANAGER_NOT_SPECIFIED_ERROR"
                )
            
            logger.debug(
                f"Using specified package manager: {programming_language_metadata.package_manager.value} | "
                f"codebase_path={local_workspace_path}"
            )
            
            package_strategy = PackageManagerStrategyFactory.get_strategy(
                programming_language_metadata.language, 
                programming_language_metadata.package_manager
            )
                
            return package_strategy.process_metadata(local_workspace_path, programming_language_metadata)
            
        except UnsupportedPackageManagerError as e:
            # Get traceback for detailed error reporting
            tb_str = traceback.format_exc()
            logger.error("Unsupported package manager: {} | traceback={}", str(e), tb_str)
            
            # Re-raise with comprehensive context
            raise ApplicationError(
                f"Unsupported package manager: {str(e)}",
                {"local_workspace_path": local_workspace_path},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                type="UNSUPPORTED_PACKAGE_MANAGER_ERROR"
            )
            
        except Exception as e:
            # Get traceback for detailed error reporting
            tb_str = traceback.format_exc()
            logger.error("Failed to parse package metadata: {} | traceback={}", str(e), tb_str)
            
            # Re-raise with comprehensive context
            raise ApplicationError(
                f"Failed to parse package metadata: {str(e)}",
                {"local_workspace_path": local_workspace_path},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                type="PACKAGE_PARSER_ERROR"
            )
        
