from typing import Dict, List
from pydantic import ValidationError
from loader.iparse_json import IParseJson
from data_models.chapi_unoplat_node import Node
from loguru import logger
from nodeparser.isummariser import ISummariser

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict, isummariser: ISummariser = None) -> Dict[str, List[Node]]:
        """Concrete implementation of the parse_json_to_nodes method."""
        package_dict = {}
        for item in json_data:
            try:
                node = Node(**item)
                #Only summarise if node type is class 
                #TODO: going forward might require other constructs too like interface, abstract class for better intellisense etc
               #TODO: disabled right now for dspy
                # if node.type == "CLASS":
                #     node = isummariser.summarise_node(node)

                if node.package not in package_dict:
                    package_dict[node.package] = []
                package_dict[node.package].append(node)
                
            except ValidationError as e:
                logger.error(f"Error validating node: {e}")
        return package_dict