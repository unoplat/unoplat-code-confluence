from typing import List
from pydantic import ValidationError
from loader.iparse_json import IParseJson
from data_models.chapi_unoplat_node import Node
from loguru import logger
from nodeparser.isummariser import ISummariser

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict,isummariser:ISummariser) -> List[Node]:
        """Concrete implementation of the parse_json_to_nodes method."""
        nodes = []
        for item in json_data:
            try:
                node = Node(**item)
                #Only summarise if node type is class 
                #TODO: going forward might require other constructs too like interface, abstract class for better intellisense etc
                if node.type == "CLASS":
                    node = isummariser.summarise_node(node)
                nodes.append(node)
            except ValidationError as e:
                logger.error(f"Error validating node: {e}")
        return nodes