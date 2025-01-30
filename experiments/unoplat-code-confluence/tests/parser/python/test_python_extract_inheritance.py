# Standard Library
from typing import List

# Third Party
import pytest

# First Party
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import ImportedName, UnoplatImport
from unoplat_code_confluence.parser.python.python_extract_inheritance import PythonExtractInheritance


@pytest.fixture
def extractor() -> PythonExtractInheritance:
    """Fixture for PythonExtractInheritance."""
    return PythonExtractInheritance()


def create_import(source: str, names: List[tuple[str, str | None]]) -> UnoplatImport:
    """Helper to create an import with usage names.
    
    Args:
        source: Import source path
        names: List of tuples (original_name, alias)
    """
    return UnoplatImport(
        Source=source,
        UsageName=[
            ImportedName(
                original_name=original,
                alias=alias
            ) for original, alias in names
        ]
    )


class TestPythonExtractInheritance:
    
    def test_simple_inheritance(self, extractor: PythonExtractInheritance):
        """Test basic class inheritance without aliases."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["BaseModel"]
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", None),
                ("helper_function", None)  # Procedural import that shouldn't affect inheritance
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == ["myproject.models.BaseModel"]
        assert len(result) == 0  # Import is removed as it was used for class inheritance
    
    def test_inheritance_with_alias(self, extractor: PythonExtractInheritance):
        """Test class inheritance using an aliased import."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["Base"]
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", "Base"),  # Class with alias
                ("process_data", None)  # Procedural import
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == ["myproject.models.BaseModel"]
        assert len(result) == 0
    
    def test_multiple_inheritance(self, extractor: PythonExtractInheritance):
        """Test class inheriting from multiple base classes."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["BaseModel", "Mixin", "Interface"]
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", None),
                ("helper_func", None)  # Procedural import
            ]),
            create_import("myproject.utils", [
                ("Mixin", None),
                ("Interface", None),
                ("process_data", None)  # Procedural import
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == [
            "myproject.models.BaseModel",
            "myproject.utils.Mixin",
            "myproject.utils.Interface"
        ]
        assert len(result) == 0
    
    def test_mixed_class_inheritance(self, extractor: PythonExtractInheritance):
        """Test inheritance with both aliased and direct class imports."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["Model", "DataValidator"]
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", "Model"),  # Class with alias
                ("DataValidator", None),  # Class without alias
                ("process_helper", None)  # Procedural import
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == [
            "myproject.models.BaseModel",
            "myproject.models.DataValidator"
        ]
        assert len(result) == 0
    
    def test_partial_inheritance_resolution(self, extractor: PythonExtractInheritance):
        """Test when only some base classes are from internal imports."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["BaseModel", "ExternalClass", "Mixin"]
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", None),
                ("helper_func", None)  # Procedural import
            ]),
            create_import("myproject.utils", [
                ("Mixin", None),
                ("process_data", None)  # Procedural import
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == [
            "myproject.models.BaseModel",
            "ExternalClass",  # Should remain unchanged
            "myproject.utils.Mixin"
        ]
        assert len(result) == 0
    
    def test_no_inheritance(self, extractor: PythonExtractInheritance):
        """Test node without inheritance but with imports."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = []
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", None),
                ("helper_func", None)
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        assert node.multiple_extend == []
        assert result == imports  # Imports should remain unchanged
    
    def test_no_imports(self, extractor: PythonExtractInheritance):
        """Test inheritance without any imports."""
        node = UnoplatChapiForgeNode()
        node.multiple_extend = ["BaseModel"]
        
        result = extractor.extract_inheritance(node, [])
        
        assert node.multiple_extend == ["BaseModel"]  # Should remain unchanged
        assert result == []
    
    def test_procedural_node(self, extractor: PythonExtractInheritance):
        """Test that procedural nodes (type=None) are not processed for inheritance."""
        node = UnoplatChapiForgeNode()
        # No need to set node.type as it defaults to None for procedural nodes
        
        
        imports = [
            create_import("myproject.models", [
                ("BaseModel", None),
                ("helper_function", None)
            ])
        ]
        
        result = extractor.extract_inheritance(node, imports)
        
        
        # Imports should remain unchanged
        assert result == imports