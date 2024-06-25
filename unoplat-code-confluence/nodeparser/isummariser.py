from abc import ABC, abstractmethod
from data_models.chapi_unoplat_node import Node

class ISummariser(ABC):
    
    @abstractmethod
    def summarise_node(self, node: Node) -> Node:
        """
        Summarises the provided Node object by modifying its summary attribute.
        
        Args:
            node (Node): The node to summarise.
        
        Returns:
            Node: The node with updated summary.
        """
        pass