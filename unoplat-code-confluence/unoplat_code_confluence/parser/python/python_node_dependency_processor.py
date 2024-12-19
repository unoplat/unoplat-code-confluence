import logging
from typing import Dict, List, Set

from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.utility.is_class_name import IsClassName

logger = logging.getLogger(__name__)


class PythonNodeDependencyProcessor:
    def process_dependencies(self, node: UnoplatChapiForgeNode, qualified_dict: Dict[str, UnoplatChapiForgeNode]) -> List['UnoplatChapiForgeNode']:
        """Process dependencies for a given node.
        
        We have internal imports with source and usage - original and alias both.
        What we have to do is go through each import and identify class dependencies
        based on import type. Classes use CamelCase naming convention.
        
        For example:
        from myproject.models import UserModel, BaseClass, helper_func
        from myproject.utils import helper_function, HelperClass as helper
        
        We identify:
        - UserModel, BaseClass as class dependencies -> myproject.models.UserModel, myproject.models.BaseClass
        - helper_func as function -> myproject.models
        - HelperClass as class dependency -> myproject.utils.HelperClass
        - helper_function as function -> myproject.utils
        
        Args:
            node: The ChapiUnoplatNode to process dependencies for
            
        Note:
            Modifies node.dependent_internal_classes in place:
            - For classes: adds fully qualified name (source.original_name)
            - For non-classes: adds only the source module path
        """
        try:
            if not node.segregated_imports or ImportType.INTERNAL not in node.segregated_imports:
                return []
            
            node.dependent_internal_classes = []
            procedural_nodes: Set[str] = set()    
            internal_imports = node.segregated_imports[ImportType.INTERNAL]
            
            for imp in internal_imports:
                if imp.usage_names:
                    for usage in imp.usage_names:
                        if usage.original_name:
                            try:
                                if IsClassName.is_python_class_name(usage.original_name):
                                    # For classes, add the fully qualified name
                                    qualified_name = f"{imp.source}.{usage.original_name}"
                                    # try:
                                    #     class_dependent_node = qualified_dict[qualified_name]
                                    # except KeyError:
                                    #     logger.error(
                                    #         f"Missing qualified name in dictionary: {qualified_name}\n"
                                    #         f"Available qualified names: {list(qualified_dict.keys())}\n"
                                    #         f"Current node: {node.node_name}\n"
                                    #         f"Import source: {imp.source}"
                                    #     )
                                    #     continue
                                    node.dependent_internal_classes.append(qualified_name)
                                
                                else:
                                    # For non-classes, add only the source module path
                                    try:
                                        procedural_dependent_node = qualified_dict[imp.source] #type: ignore
                                    except KeyError:
                                        logger.error(
                                            f"Missing source module in dictionary: {imp.source}\n"
                                            f"Available modules: {list(qualified_dict.keys())}\n"
                                            f"Current node: {node.node_name}"
                                        )
                                        continue
                                        
                                    if procedural_dependent_node.node_name not in procedural_nodes:
                                        node.dependent_internal_classes.append(imp.source) #type: ignore
                                        procedural_nodes.add(procedural_dependent_node.node_name) #type: ignore
                                        
                            except Exception as inner_e:
                                logger.error(
                                    f"Error processing import usage: {usage.original_name}\n"
                                    f"Import source: {imp.source}\n"
                                    f"Error: {str(inner_e)}"
                                )
                                continue
                                
            return node.dependent_internal_classes                            
                    
        except Exception as e:
            logger.error(
                f"Error processing dependencies for node: {node.node_name}\n"
                f"Node type: {node.type}\n"
                f"Node package: {node.package}\n"
                f"Internal imports: {internal_imports if 'internal_imports' in locals() else 'Not initialized'}\n"
                f"Error: {str(e)}\n"
                f"Available qualified names: {list(qualified_dict.keys())}"
            )
            return []
                        
    
    
        
        
        
        