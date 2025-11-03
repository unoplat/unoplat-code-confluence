"""
Extensible data model detection for multiple programming languages.

This module provides language-agnostic data model detection by dispatching to
language-specific detection logic. It identifies files that define data models
such as dataclasses, entities, DTOs, schemas, etc.
"""

from typing import List, Optional


def detect_data_model(
    source_code: str,
    imports: List[str],
    language: str,
    structural_signature: Optional[object] = None
) -> bool:
    """
    Detect if a file contains data model definitions for any supported language.
    
    Args:
        source_code: The source code content
        imports: List of import statements (already extracted)
        language: Programming language (e.g., "python", "java", "typescript")
        structural_signature: Optional structural signature (for future use)
        
    Returns:
        True if the file contains data model definitions, False otherwise
    """
    if language == "python":
        return _detect_python_data_models(imports)
    else:
        return False


def _detect_python_data_models(imports: List[str]) -> bool:
    """
    Detect Python data models (dataclasses, pydantic models, etc.).
    
    Since Ruff F401 ensures no unused imports, if dataclass is imported,
    it's being used in the file.
    
    Args:
        imports: List of import statement strings
        
    Returns:
        True if Python data model imports are found
    """
    # Check for dataclass-related imports
    dataclass_patterns = ['dataclass', 'pydantic']
    
    for import_stmt in imports:
        import_lower = import_stmt.lower()
        if any(pattern in import_lower for pattern in dataclass_patterns):
            return True
    
    return False