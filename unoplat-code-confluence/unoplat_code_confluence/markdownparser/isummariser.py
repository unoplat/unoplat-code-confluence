from abc import ABC, abstractmethod
from unoplat_code_confluence.data_models.chapi_unoplat_node import Node
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_codebase_summary import DspyUnoplatCodebaseSummary

class ISummariser(ABC):
    
    @abstractmethod
    def summarise_to_markdown(self, unoplat_codebase_summary: DspyUnoplatCodebaseSummary) -> str:
        """
        Summarises the provided unoplat codebase summary to markdown.
        
        Args:
            unoplat_codebase_summary (DspyUnoplatCodebaseSummary): The unoplat codebase summary to summarise.
        
        Returns:
            str: The markdown string.
        """
        pass