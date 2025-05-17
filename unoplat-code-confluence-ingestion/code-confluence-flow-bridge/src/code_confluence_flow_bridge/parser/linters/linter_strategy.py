from abc import ABC, abstractmethod
from typing import List, Optional


class LinterStrategy(ABC):
    
    @abstractmethod
    def lint_codebase(self, local_workspace_path: str, dependencies: Optional[List[str]], programming_language_version: str) -> bool:
        """
        Run linting on the codebase and return results

        Args:
            local_workspace_path: Path to the local workspace

        Returns:
            bool: True if fixing linting violations else False
        """
        pass
