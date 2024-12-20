import pytest
from unoplat_code_confluence.utility.is_class_name import IsClassName


@pytest.mark.parametrize("name,expected", [
    # Valid class names (CamelCase)
    ("MyClass", True),
    ("UserModel", True),
    ("HTTPResponse", True),
    ("ILoadJson", True), # interface
    ("A", True),  # Single uppercase letter
    
    # Invalid class names
    ("my_class", False),  # snake_case
    ("myclass", False),   # all lowercase
    ("MYCLASS", False),   # all uppercase
    ("_MyClass", False),  # starts with underscore
    ("My_Class", False),  # contains underscore
    ("", False),         # empty string
    ("123Class", False), # starts with number
    
])
def test_is_python_class_name(name: str, expected: bool):
    """Test various class name patterns against Python naming conventions."""
    result = IsClassName.is_python_class_name(name)
    assert result == expected, f"Expected {name} to be {'valid' if expected else 'invalid'} class name"

def test_is_python_class_name_edge_cases():
    """Test edge cases for class name validation."""
    # None type
    with pytest.raises(AttributeError):
        IsClassName.is_python_class_name(None) # type: ignore
        
    # Non-string types
    with pytest.raises(AttributeError):
        IsClassName.is_python_class_name(123) # type: ignore
        
    # Empty string
    assert not IsClassName.is_python_class_name("")
    
    # Whitespace
    assert not IsClassName.is_python_class_name(" ")
    assert not IsClassName.is_python_class_name("\t")
    assert not IsClassName.is_python_class_name("\n")

def test_is_python_class_name_special_characters():
    """Test class names with special characters."""
    special_cases = [
        "Class$Name",
        "Class-Name",
        "Class.Name",
        "Class@Name",
        "Class Name",
    ]
    
    for name in special_cases:
        assert not IsClassName.is_python_class_name(name), \
            f"Class name with special character should be invalid: {name}" 