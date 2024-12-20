# Standard Library
from typing import Dict, List, Set

# Third Party
from loguru import logger

# First Party
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.utility.is_class_name import IsClassName


class PythonNodeDependencyProcessor:
    def process_dependencies(self, node: UnoplatChapiForgeNode, qualified_dict: Dict[str, UnoplatChapiForgeNode]) -> List[str]:
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
            logger.debug("Processing dependencies for node: {}", node.node_name)
            
            if not node.segregated_imports or ImportType.INTERNAL not in node.segregated_imports:
                logger.debug("No internal imports found for node: {}", node.node_name)
                return []
            
            node.dependent_internal_classes = []
            procedural_nodes: Set[str] = set()    
            internal_imports = node.segregated_imports[ImportType.INTERNAL]
            
            logger.debug("Found {} internal imports for node: {}", len(internal_imports), node.node_name)
            
            for imp in internal_imports:
                if imp.usage_names:
                    for usage in imp.usage_names:
                        if usage.original_name:
                            try:
                                if IsClassName.is_python_class_name(usage.original_name):
                                    # For classes, add the fully qualified name
                                    qualified_name = f"{imp.source}.{usage.original_name}"
                                    logger.debug("Found class dependency: {} -> {}", node.node_name, qualified_name)
                                    node.dependent_internal_classes.append(qualified_name)
                                
                                else:
                                    # For non-classes, add only the source module path
                                    try:
                                        procedural_dependent_node = qualified_dict[imp.source] #type: ignore
                                    except KeyError:
                                        logger.error(
                                            "Missing source module in dictionary: {}\n"
                                            "Available modules: {}\n"
                                            "Current node: {}", 
                                            imp.source, list(qualified_dict.keys()), node.node_name
                                        )
                                        continue
                                        
                                    if procedural_dependent_node.node_name not in procedural_nodes:
                                        logger.debug(
                                            "Found procedural dependency: {} -> {}", 
                                            node.node_name, procedural_dependent_node.node_name
                                        )
                                        node.dependent_internal_classes.append(imp.source) #type: ignore
                                        procedural_nodes.add(procedural_dependent_node.node_name) #type: ignore
                                        
                            except Exception as inner_e:
                                logger.error(
                                    "Error processing import usage: {}\n"
                                    "Import source: {}\n"
                                    "Error: {}", 
                                    usage.original_name, imp.source, str(inner_e)
                                )
                                continue
            
            logger.debug(
                "Completed processing dependencies for node: {}\n"
                "Found {} class dependencies and {} procedural dependencies",
                node.node_name, 
                len(node.dependent_internal_classes) - len(procedural_nodes),
                len(procedural_nodes)
            )
                                
            return node.dependent_internal_classes                            
                    
        except Exception as e:
            logger.opt(exception=True).error(
                "Error processing dependencies for node: {}\n"
                "Node type: {}\n"
                "Node package: {}\n"
                "Internal imports: {}\n"
                "Error: {}\n"
                "Available qualified names: {}",
                node.node_name,
                node.type,
                node.package,
                internal_imports if 'internal_imports' in locals() else 'Not initialized',
                str(e),
                list(qualified_dict.keys())
            )
            return []
                        
    
    
        
        
        
        