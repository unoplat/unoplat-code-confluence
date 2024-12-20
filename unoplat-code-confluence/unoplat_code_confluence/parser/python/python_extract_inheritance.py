from typing import List

from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport


class PythonExtractInheritance:
    
        
    def extract_inheritance(self, node: UnoplatChapiForgeNode,internal_imports: List[UnoplatImport]) -> List[UnoplatImport]:
        """Extract inheritance information from a Python node.
           we have list of mulitple extends but they have just class names. We need full qualified names to resolve the actual class.
           We have internal imports which consists of always absolute paths as source and then usage names are in form of orignal name and alias.
           Now what we have to do is match usage name (be it original or alias if alias exists) with name in multiple extend and replace the name with full qualified name with original name(original name always)
           Then in house remove the internal import from list of internal import. Do all modifications in place.
        Args:
            node: The ChapiUnoplatNode to extract inheritance from
            internal_imports: The list of unoplat imports 
            
        Returns:
            List[UnoplatImport]: Modified list of internal imports with matched imports removed
        """
        
        
        if not node.multiple_extend or not internal_imports:
            return internal_imports
            
        # Create a map of class names to their full paths
        class_map = {}
        for imp in internal_imports:
            source = imp.source
            if imp.usage_names:
                for usage in imp.usage_names:
                    # If there's an alias, use that, otherwise use original name
                    class_name = usage.alias if usage.alias else usage.original_name
                    class_map[class_name] = (source, usage.original_name, imp)
        
        # Track imports to remove using list
        imports_to_remove = []
        
        # Process each inherited class
        for i, class_name in enumerate(node.multiple_extend):
            if class_name in class_map:
                # Replace the class name with its fully qualified name
                source, original_name, imp = class_map[class_name]
                node.multiple_extend[i] = f"{source}.{original_name}"
                if imp not in imports_to_remove:  # Avoid duplicates
                    imports_to_remove.append(imp)
        
        # Remove matched imports in-place
        for imp in imports_to_remove:
            internal_imports.remove(imp)
        
        return internal_imports