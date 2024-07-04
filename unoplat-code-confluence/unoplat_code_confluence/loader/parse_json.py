from typing import Dict, List
from pydantic import ValidationError
from unoplat_code_confluence.data_models.chapi_unoplat_codebase import UnoplatCodebase
from unoplat_code_confluence.data_models.chapi_unoplat_package import UnoplatPackage
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_annotation_subset import DspyUnoplatAnnotationSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_call_subset import DspyUnoplatFunctionCallSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_function_subset import DspyUnoplatFunctionSubset
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_fs_node_subset import DspyUnoplatNodeSubset
from unoplat_code_confluence.loader.iparse_json import IParseJson
from unoplat_code_confluence.data_models.chapi_unoplat_node import Node
from loguru import logger
from unoplat_code_confluence.nodeparser.isummariser import ISummariser

class JsonParser(IParseJson):
    def parse_json_to_nodes(self, json_data: dict) -> UnoplatCodebase:
        """Concrete implementation of the parse_json_to_nodes method."""
        unoplat_codebase = UnoplatCodebase()
        
        unoplat_package = UnoplatPackage()
        
        unoplat_package_dict: Dict[str,List[DspyUnoplatNodeSubset]] = {}
        
        for item in json_data:
            try:
                node = Node(**item)
                if node.type == 'CLASS':
                
                    # Creating node subset
                    node_subset = DspyUnoplatNodeSubset(
                    NodeName=node.node_name,
                    Imports=node.imports,
                    Extend=node.extend,
                    MultipleExtend=node.multiple_extend,
                    Fields=node.fields,
                    Annotations=[DspyUnoplatAnnotationSubset(Name=annotation.name,KeyValues=annotation.key_values) for annotation in node.annotations],
                    Content=node.content
                    )
                    function_subset_list = []
                    
                    # Creating list function subset
                    
                    for func in node.functions:
                        function_subset = DspyUnoplatFunctionSubset(
                        Name=func.name,
                        ReturnType=func.return_type,
                        Annotations=[DspyUnoplatAnnotationSubset(Name=annotation.name,KeyValues=annotation.key_values) for annotation in node.annotations],
                        LocalVariables=func.local_variables,
                        Content=func.content,
                        FunctionCalls=[DspyUnoplatFunctionCallSubset(NodeName=call.node_name, FunctionName=call.function_name, Parameters=call.parameters) for call in func.function_calls])
                        function_subset_list.append(function_subset)
                    
                    node_subset.functions = function_subset_list
                    
                    if node.package in unoplat_package_dict:
                        print("added package",node.package)
                        unoplat_package_dict[node.package].append(node_subset)
                    else:
                        list_node_subset: List[DspyUnoplatNodeSubset] = [] 
                        list_node_subset.append(node_subset)
                        unoplat_package_dict[node.package] = list_node_subset
            except Exception as e:
                logger.error(f"Error processing node: {e}")
        unoplat_package.package_dict = unoplat_package_dict
        unoplat_codebase.packages =  unoplat_package
        
        return unoplat_codebase