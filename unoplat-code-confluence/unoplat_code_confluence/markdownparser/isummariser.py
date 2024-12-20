# Standard Library
# Standard Library
from abc import ABC, abstractmethod

# First Party
from unoplat_code_confluence.data_models.forge_summary.forge_unoplat_codebase_summary import ForgeUnoplatCodebaseSummary


class ISummariser(ABC):
    
    @abstractmethod
    def summarise_to_markdown(self, unoplat_codebase_summary: ForgeUnoplatCodebaseSummary) -> str:
        """
        Summarises the provided unoplat codebase summary to markdown.
        
        Args:
            unoplat_codebase_summary (DspyUnoplatCodebaseSummary): The unoplat codebase summary to summarise.
        
        Returns:
            str: The markdown string.
        """
        pass