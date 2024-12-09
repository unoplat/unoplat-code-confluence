# Standard Library
from typing import List, Dict

# Third Party
import pytest

# First Party
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport, ImportedName
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from unoplat_code_confluence.parser.python.python_node_dependency_processor import PythonNodeDependencyProcessor


@pytest.fixture
def dependency_processor() -> PythonNodeDependencyProcessor:
    """Fixture for PythonNodeDependencyProcessor."""
    return PythonNodeDependencyProcessor()


def create_node_with_imports(imports: List[UnoplatImport]) -> UnoplatChapiForgeNode:
    """Helper to create a node with given imports."""
    node = UnoplatChapiForgeNode()
    node.segregated_imports = {ImportType.INTERNAL: imports}
    return node


def _is_class_name(name: str) -> bool:
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

        

def create_qualified_dict(imports: List[UnoplatImport]) -> Dict[str, UnoplatChapiForgeNode]:
    """Helper to create qualified_node_dict from imports."""
    qualified_dict = {}
    
    for imp in imports:
        if imp.source:  # Check if source is not None
            # Add module node
            module_node = UnoplatChapiForgeNode(NodeName=imp.source.split('.')[-1])
            qualified_dict[imp.source] = module_node
            
            # Add class nodes
            if imp.usage_names:
                for usage in imp.usage_names:
                    if _is_class_name(usage.original_name): #type: ignore
                        class_node = UnoplatChapiForgeNode(NodeName=usage.original_name)
                        qualified_dict[f"{imp.source}.{usage.original_name}"] = class_node
                    else:
                        procdural_node = UnoplatChapiForgeNode(NodeName=imp.source)
                        qualified_dict[f"{imp.source}"] = procdural_node     
    
    return qualified_dict


def test_simple_class_dependencies(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test identifying simple class dependencies."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.models",
            UsageName=[
                ImportedName(original_name="UserModel"),
                ImportedName(original_name="BaseModel")
            ],
            ImportType=ImportType.INTERNAL
        ),
        UnoplatImport(
            Source="myproject.utils",
            UsageName=[ImportedName(original_name="helper_function")],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 3
    assert qualified_dict["myproject.models.UserModel"] in node.dependent_internal_classes
    assert qualified_dict["myproject.models.BaseModel"] in node.dependent_internal_classes
    assert qualified_dict["myproject.utils"] in node.dependent_internal_classes


def test_class_with_alias(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test class dependencies with aliases."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.core",
            UsageName=[ImportedName(original_name="DataModel", alias="Model")],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 1
    assert qualified_dict["myproject.core.DataModel"] in node.dependent_internal_classes


def test_mixed_dependencies(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test mix of class and non-class dependencies."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.models",
            UsageName=[
                ImportedName(original_name="UserModel"),
                ImportedName(original_name="helper_func"),
                ImportedName(original_name="DataModel", alias="model"),
                ImportedName(original_name="CONSTANT")
            ],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 3  # 2 classes + 1 module
    assert qualified_dict["myproject.models.UserModel"] in node.dependent_internal_classes
    assert qualified_dict["myproject.models.DataModel"] in node.dependent_internal_classes
    assert qualified_dict["myproject.models"] in node.dependent_internal_classes


def test_no_class_dependencies(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test when there are no class dependencies."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.utils",
            UsageName=[
                ImportedName(original_name="helper_one"),
                ImportedName(original_name="helper_two")
            ],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 1
    assert qualified_dict["myproject.utils"] in node.dependent_internal_classes


def test_all_class_dependencies(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test when all imports are classes."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.models",
            UsageName=[
                ImportedName(original_name="ModelOne"),
                ImportedName(original_name="ModelTwo"),
                ImportedName(original_name="BaseModel")
            ],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 3
    assert qualified_dict["myproject.models.ModelOne"] in node.dependent_internal_classes
    assert qualified_dict["myproject.models.ModelTwo"] in node.dependent_internal_classes
    assert qualified_dict["myproject.models.BaseModel"] in node.dependent_internal_classes


def test_constants_vs_classes(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test distinguishing between constants and classes."""
    internal_imports = [
        UnoplatImport(
            Source="myproject.constants",
            UsageName=[
                ImportedName(original_name="UserModel"),
                ImportedName(original_name="USER_MODEL"),
                ImportedName(original_name="Model", alias="MODEL")
            ],
            ImportType=ImportType.INTERNAL
        )
    ]
    
    node = create_node_with_imports(internal_imports)
    qualified_dict = create_qualified_dict(internal_imports)
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 3
    assert qualified_dict["myproject.constants.UserModel"] in node.dependent_internal_classes
    assert qualified_dict["myproject.constants.Model"] in node.dependent_internal_classes
    assert qualified_dict["myproject.constants"] in node.dependent_internal_classes


def test_empty_imports(dependency_processor: PythonNodeDependencyProcessor) -> None:
    """Test handling empty imports list."""
    node = create_node_with_imports([])
    qualified_dict = create_qualified_dict([])
    
    dependency_processor.process_dependencies(node, qualified_dict)
    
    assert len(node.dependent_internal_classes) == 0
    
    # Similar updates needed for remaining tests... 