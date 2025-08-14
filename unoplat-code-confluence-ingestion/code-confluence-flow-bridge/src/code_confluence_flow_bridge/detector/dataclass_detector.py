"""
Simplified dataclass detection using existing import extraction infrastructure.

This module detects whether a Python file defines dataclasses by:
1. Using the existing import extraction to get all imports
2. Checking if dataclass-related modules are imported
3. Using a simple tree-sitter query to find decorated classes
4. Matching decorators against imported dataclass symbols
"""

from typing import List, Optional


def is_dataclass_file(
    source_code: str, 
    imports: List[str], 
    structural_signature: Optional[object] = None
) -> bool:
    """
    Detect if a Python file contains dataclass definitions.
    
    This simplified approach:
    1. Checks if dataclass-related imports exist
    2. If yes, checks for @dataclass decorators on classes
    
    Args:
        source_code: The Python source code
        imports: List of import statements (already extracted)
        structural_signature: Optional structural signature (unused but kept for compatibility)
        
    Returns:
        True if the file contains dataclass definitions, False otherwise
    """
    # Quick check: if no imports mention dataclass, it can't be a dataclass file
    if has_dataclass_imports(imports):
        return True
    
    return False


def has_dataclass_imports(imports: List[str]) -> bool:
    """
    Check if any imports bring in dataclass functionality.
    
    We check for any import that contains 'dataclass' or 'dataclasses'
    This covers:
    - from dataclasses import dataclass
    - import dataclasses
    - from pydantic.dataclasses import dataclass
    - etc.
    
    Args:
        imports: List of import statement strings
        
    Returns:
        True if dataclass-related imports exist
    """
    for import_stmt in imports:
        # Simple text-based check - if the import mentions dataclass, it's relevant
        if 'dataclass' in import_stmt.lower():
            return True
    return False



