from abc import ABC, abstractmethod
from typing import Dict


from unoplat_code_confluence.data_models.unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

class PackageManagerStrategy(ABC):
    @abstractmethod
    def process_metadata(self, local_workspace_path: str, metadata: Dict[str, str]) -> UnoplatPackageManagerMetadata:
        """Process package manager specific metadata"""
        pass



