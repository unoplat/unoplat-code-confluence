"""Utility functions for working with language-specific structural signatures."""

from unoplat_code_confluence_commons.base_models.python_structural_signature import (
    PythonStructuralSignature,
)
from unoplat_code_confluence_commons.base_models.typescript_structural_signature import (
    TypeScriptStructuralSignature,
)

from typing import Union

# Type alias for all supported structural signatures
StructuralSignatureUnion = Union[
    PythonStructuralSignature,
    TypeScriptStructuralSignature,
]


def deserialize_structural_signature(
    json_data: str,
    language: str,
) -> StructuralSignatureUnion:
    """
    Deserialize structural signature based on programming language context.

    This function uses language context to determine which structural signature
    model to use for deserialization. The language information comes from the
    graph database (via package manager metadata).

    Args:
        json_data: JSON string of structural signature
        language: Programming language (e.g., "python", "typescript", "javascript")

    Returns:
        Language-specific structural signature object

    Raises:
        ValueError: If language is not supported

    Example:
        >>> json_str = '{"module_docstring": "A module", "functions": []}'
        >>> sig = deserialize_structural_signature(json_str, "python")
        >>> isinstance(sig, PythonStructuralSignature)
        True
    """
    language_lower = language.lower()

    if language_lower == "python":
        return PythonStructuralSignature.model_validate_json(json_data)
    elif language_lower in ("typescript", "javascript"):
        # Both TypeScript and JavaScript use the same structural signature model
        return TypeScriptStructuralSignature.model_validate_json(json_data)
    else:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: python, typescript, javascript"
        )


def get_signature_type_for_language(language: str) -> type[StructuralSignatureUnion]:
    """
    Get the structural signature type class for a given language.

    Args:
        language: Programming language name

    Returns:
        Structural signature class type

    Raises:
        ValueError: If language is not supported

    Example:
        >>> sig_type = get_signature_type_for_language("python")
        >>> sig_type == PythonStructuralSignature
        True
    """
    language_lower = language.lower()

    if language_lower == "python":
        return PythonStructuralSignature
    elif language_lower in ("typescript", "javascript"):
        return TypeScriptStructuralSignature
    else:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Supported languages: python, typescript, javascript"
        )
