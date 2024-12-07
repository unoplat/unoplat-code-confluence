from typing import Dict, List, Set
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType


class PythonNodeDependencyProcessor:
    def process_dependencies(self, node: UnoplatChapiForgeNode,qualified_node_dict: Dict[str,UnoplatChapiForgeNode]) -> None:
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
        
        if not node.segregated_imports or ImportType.INTERNAL not in node.segregated_imports:
            return
            
        node.dependent_internal_classes = []
        procedural_nodes: Set[str] = set()    
        internal_imports = node.segregated_imports[ImportType.INTERNAL]
        for imp in internal_imports:
            if imp.usage_names:
                for usage in imp.usage_names:
                    if usage.original_name:
                        #TODO: this will work if python semantics are followed in terms of class 
                        if self._is_class_name(usage.original_name):
                            # For classes, add the fully qualified name
                            qualified_name = f"{imp.source}.{usage.original_name}"
                            class_dependent_node: UnoplatChapiForgeNode = qualified_node_dict[qualified_name]
                            node.dependent_internal_classes.append(class_dependent_node) #type: ignore
                            
                        else:
                            # For non-classes, add only the source module path
                            procedural_dependent_node: UnoplatChapiForgeNode = qualified_node_dict[imp.source] #type: ignore
                            if procedural_dependent_node.node_name not in procedural_nodes:
                                node.dependent_internal_classes.append(procedural_dependent_node)#type: ignore
                                procedural_nodes.add(procedural_dependent_node.node_name) #type: ignore
                        
    
    def _is_class_name(self, name: str) -> bool:
        """Check if a name follows class naming convention (CamelCase).
        
        Args:
            name: Name to check
            
        Returns:
            bool: True if name follows class naming convention
        """
        # Class names should:
        # 1. Start with uppercase letter
        # 2. Not contain underscores (CamelCase not snake_case)
        # 3. Not be all uppercase (to exclude constants)
        return (
            name[0].isupper() and  # Starts with uppercase
            '_' not in name and    # No underscores
            not name.isupper()     # Not all uppercase
        )
        
        
        
        