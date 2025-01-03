
from src.code_confluence_flow_bridge.models.chapi_forge.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata
from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguageMetadata
from src.code_confluence_flow_bridge.parser.package_manager.package_manager_factory import PackageManagerStrategyFactory


class PackageManagerParser():
    def parse_package_metadata(self, local_workspace_path: str, programming_language_metadata: ProgrammingLanguageMetadata) -> UnoplatPackageManagerMetadata:
        """Concrete implementation of the parse_codebase method."""
        package_strategy = PackageManagerStrategyFactory.get_strategy(programming_language_metadata.language,programming_language_metadata.package_manager)
        return package_strategy.process_metadata(local_workspace_path, programming_language_metadata)
