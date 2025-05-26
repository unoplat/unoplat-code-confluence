# Standard Library
import traceback
from pathlib import Path

# Third Party
from loguru import logger
from temporalio.exceptions import ApplicationError

# First Party
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata, PackageManagerType
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_factory import PackageManagerStrategyFactory, UnsupportedPackageManagerError
from src.code_confluence_flow_bridge.parser.package_manager.detectors.registry import detect_manager
# No need to import trace_utils as logger already has context


class PackageManagerParser:
    def parse_package_metadata(self, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """
        Parse package metadata with automatic detection if needed.
        
        Args:
            local_workspace_path: Path to the local workspace
            programming_language_metadata: Programming language metadata
            
        Returns:
            UnoplatPackageManagerMetadata: Processed package manager metadata
            
        Raises:
            ApplicationError: If package manager detection or processing fails
        """
        try:
            
            # If package manager is specified and not AUTO_DETECT, use it directly
            if programming_language_metadata.package_manager and programming_language_metadata.package_manager != PackageManagerType.AUTO_DETECT:
                logger.debug(
                    f"Using specified package manager: {programming_language_metadata.package_manager.value} | "
                    f"codebase_path={local_workspace_path}"
                )
                package_strategy = PackageManagerStrategyFactory.get_strategy(
                    programming_language_metadata.language, 
                    programming_language_metadata.package_manager
                )
            else:
                # Auto-detect package manager
                logger.info(
                    f"Attempting to auto-detect package manager for {local_workspace_path} | "
                    f"language={programming_language_metadata.language.value}"
                )
                
                detected_manager = detect_manager(
                    Path(local_workspace_path), 
                    programming_language_metadata.language.value
                )
                
                if not detected_manager:
                    error_msg = f"Could not detect package manager for {local_workspace_path}"
                    logger.error(
                        f"{error_msg} | language={programming_language_metadata.language.value}"
                    )
                    raise ApplicationError(
                        error_msg,
                        {"local_workspace_path": local_workspace_path},
                        {"language": programming_language_metadata.language.value},
                        type="PACKAGE_MANAGER_DETECTION_ERROR"
                    )
                    
                logger.info(
                    f"Detected package manager: {detected_manager} for {local_workspace_path}"
                )
                
                # Convert string name to strategy
                package_strategy = PackageManagerStrategyFactory.get_strategy_from_name(
                    programming_language_metadata.language, 
                    detected_manager
                )
                
            return package_strategy.process_metadata(local_workspace_path, programming_language_metadata)
            
        except UnsupportedPackageManagerError as e:
            # Get traceback for detailed error reporting
            tb_str = traceback.format_exc()
            logger.error(f"Unsupported package manager: {str(e)} | traceback={tb_str}")
            
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
            logger.error(f"Failed to parse package metadata: {str(e)} | traceback={tb_str}")
            
            # Re-raise with comprehensive context
            raise ApplicationError(
                f"Failed to parse package metadata: {str(e)}",
                {"local_workspace_path": local_workspace_path},
                {"error": str(e)},
                {"error_type": type(e).__name__},
                {"traceback": tb_str},
                type="PACKAGE_PARSER_ERROR"
            )
        
