from typing import List
import pytest
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.parser.python.node_variables.node_variables_parser import NodeVariablesParser
from unoplat_code_confluence.configuration.settings import ProgrammingLanguage
from unoplat_code_confluence.data_models.chapi.class_global_field_scope import ClassGlobalFieldScope


@pytest.fixture
def parser() -> NodeVariablesParser:
    """Create parser instance with Python language."""
    tree_sitter = CodeConfluenceTreeSitter(ProgrammingLanguage.PYTHON)
    return NodeVariablesParser(tree_sitter)

def test_simple_variables(parser: NodeVariablesParser):
    """Test parsing simple variables."""
    code = """
    global_var = 1
    GLOBAL_CONSTANT = "test"
    
    class MyClass:
        class_var = "test"
        CLASS_CONSTANT = 42
    """
    
    variables = parser.parse_variables(code)
    assert len(variables) == 4
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check global variables
    assert (global_scope, "global_var") in var_dict
    global_var = var_dict[(global_scope, "global_var")]
    assert len(global_var.field_metadata) == 1
    assert global_var.field_metadata[0].class_field_value == "1"
    
    assert (global_scope, "GLOBAL_CONSTANT") in var_dict
    global_const = var_dict[(global_scope, "GLOBAL_CONSTANT")]
    assert len(global_const.field_metadata) == 1
    assert global_const.field_metadata[0].class_field_value == '"test"'
    
    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check class variables
    assert (class_scope, "class_var") in var_dict
    class_var = var_dict[(class_scope, "class_var")]
    assert len(class_var.field_metadata) == 1
    assert class_var.field_metadata[0].class_field_value == '"test"'
    
    assert (class_scope, "CLASS_CONSTANT") in var_dict
    class_const = var_dict[(class_scope, "CLASS_CONSTANT")]
    assert len(class_const.field_metadata) == 1
    assert class_const.field_metadata[0].class_field_value == "42"

def test_variable_with_type_hints(parser: NodeVariablesParser):
    """Test parsing variables with type hints."""
    code = """
    count: int = 0
    name: str = "test"
    
    class MyClass:
        items: list = []
        data: dict = {}
    """
    
    variables = parser.parse_variables(code)
    assert len(variables) == 4
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check global variables
    assert (global_scope, "count") in var_dict
    count_var = var_dict[(global_scope, "count")]
    assert len(count_var.field_metadata) == 1
    assert count_var.field_metadata[0].class_field_type == "int"
    assert count_var.field_metadata[0].class_field_value == "0"
    
    assert (global_scope, "name") in var_dict
    name_var = var_dict[(global_scope, "name")]
    assert len(name_var.field_metadata) == 1
    assert name_var.field_metadata[0].class_field_type == "str"
    assert name_var.field_metadata[0].class_field_value == '"test"'
    
    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check class variables
    assert (class_scope, "items") in var_dict
    items_var = var_dict[(class_scope, "items")]
    assert len(items_var.field_metadata) == 1
    assert items_var.field_metadata[0].class_field_type == "list"
    assert items_var.field_metadata[0].class_field_value == "[]"
    
    assert (class_scope, "data") in var_dict
    data_var = var_dict[(class_scope, "data")]
    assert len(data_var.field_metadata) == 1
    assert data_var.field_metadata[0].class_field_type == "dict"
    assert data_var.field_metadata[0].class_field_value == "{}"

def test_variables_with_annotations(parser: NodeVariablesParser):
    """Test parsing variables with annotations."""
    code = """
    @fastapi
    @validation
    old_var = "legacy"
    
    class MyClass:
        @property
        old_class_var = "outdated"
    """
    
    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check old_var annotations
    assert (global_scope, "old_var") in var_dict
    old_var = var_dict[(global_scope, "old_var")]
    assert len(old_var.field_metadata) == 1
    assert old_var.field_metadata[0].annotations is not None
    assert len(old_var.field_metadata[0].annotations) == 2
    assert old_var.field_metadata[0].annotations[0].name == "fastapi"
    assert old_var.field_metadata[0].annotations[1].name == "validation"
    
    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check old_class_var annotations
    assert (class_scope, "old_class_var") in var_dict
    old_class_var = var_dict[(class_scope, "old_class_var")]
    assert len(old_class_var.field_metadata) == 1
    assert old_class_var.field_metadata[0].annotations is not None
    assert len(old_class_var.field_metadata[0].annotations) == 1
    assert old_class_var.field_metadata[0].annotations[0].name == "property"

def test_decorator_with_arguments(parser: NodeVariablesParser):
    """Test parsing variables with complex decorators."""
    code = """
    @route("/api", methods=["GET"])
    api_var = "endpoint"
    
    @dataclass(frozen=True)
    class MyClass:
        @validate(min_val=0, max_val=100)
        threshold = 50
    """
    
    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check api_var decorator
    assert (global_scope, "api_var") in var_dict
    api_var = var_dict[(global_scope, "api_var")]
    assert len(api_var.field_metadata) == 1
    assert api_var.field_metadata[0].annotations is not None
    api_dec = api_var.field_metadata[0].annotations[0]
    assert api_dec.name == "route"
    assert api_dec.key_values is not None
    assert len(api_dec.key_values) == 2
    assert api_dec.key_values[0].key == "0"  # Positional arg
    assert api_dec.key_values[0].value == '"/api"'
    assert api_dec.key_values[1].key == "methods"
    assert api_dec.key_values[1].value == '["GET"]'
    
    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check threshold decorator
    assert (class_scope, "threshold") in var_dict
    threshold = var_dict[(class_scope, "threshold")]
    assert len(threshold.field_metadata) == 1
    assert threshold.field_metadata[0].annotations is not None
    threshold_dec = threshold.field_metadata[0].annotations[0]
    assert threshold_dec.name == "validate"
    assert threshold_dec.key_values is not None
    assert len(threshold_dec.key_values) == 2
    assert threshold_dec.key_values[0].key == "min_val"
    assert threshold_dec.key_values[0].value == "0"
    assert threshold_dec.key_values[1].key == "max_val"
    assert threshold_dec.key_values[1].value == "100"

def test_complex_assignments(parser: NodeVariablesParser):
    """Test parsing complex variable assignments."""
    code = """
    # Tuple assignment
    x, y = 1, 2
    
    # With computation
    computed_var = 10 * 20
    
    class MyClass:
        a, b = "test", 123
        computed_class_var = 30 + 40
    """
    
    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check global variables with computation
    assert (global_scope, "computed_var") in var_dict
    computed_var = var_dict[(global_scope, "computed_var")]
    assert len(computed_var.field_metadata) == 1
    assert computed_var.field_metadata[0].class_field_value == "10 * 20"
    
    # Check global tuple unpacking
    assert (global_scope, "x") in var_dict
    x_var = var_dict[(global_scope, "x")]
    assert len(x_var.field_metadata) == 1
    assert x_var.field_metadata[0].class_field_value == "1"
    
    assert (global_scope, "y") in var_dict
    y_var = var_dict[(global_scope, "y")]
    assert len(y_var.field_metadata) == 1
    assert y_var.field_metadata[0].class_field_value == "2"
    
    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check class tuple unpacking
    assert (class_scope, "a") in var_dict
    a_var = var_dict[(class_scope, "a")]
    assert len(a_var.field_metadata) == 1
    assert a_var.field_metadata[0].class_field_value == '"test"'
    
    assert (class_scope, "b") in var_dict
    b_var = var_dict[(class_scope, "b")]
    assert len(b_var.field_metadata) == 1
    assert b_var.field_metadata[0].class_field_value == "123"
    
    # Check class computation
    assert (class_scope, "computed_class_var") in var_dict
    computed_class_var = var_dict[(class_scope, "computed_class_var")]
    assert len(computed_class_var.field_metadata) == 1
    assert computed_class_var.field_metadata[0].class_field_value == "30 + 40"

def test_empty_content(parser: NodeVariablesParser):
    """Test parsing empty content."""
    code = """
    # Empty file
    """
    
    variables = parser.parse_variables(code)
    assert len(variables) == 0

def test_only_functions(parser: NodeVariablesParser):
    """Test parsing content with only functions."""
    code = """
    def global_function():
        local_var = 1
        
    class MyClass:
        def class_method(self):
            method_var = 2
    """
    
    variables = parser.parse_variables(code)
    assert len(variables) == 0

def test_variable_components(parser: NodeVariablesParser):
    """Test all components of variable declarations."""
    code = """
    # Just name and value
    x = 5
    
    # Name, type hint, and value
    y: int = 10
    
    # Name and type hint
    z: list
    
    # Complex value
    w = 1 + 2 * 3
    
    # String value
    s: str = "test"
    
    # Reassignment with different type
    x = "five"
    """
    
    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check x (multiple assignments)
    assert (global_scope, "x") in var_dict
    x_var = var_dict[(global_scope, "x")]
    assert len(x_var.field_metadata) == 2  # Two assignments
    assert x_var.field_metadata[0].class_field_value == "5"
    assert x_var.field_metadata[1].class_field_value == '"five"'
    assert x_var.field_metadata[0].class_field_type is None
    
    # Check y (type hint and value)
    assert (global_scope, "y") in var_dict
    y_var = var_dict[(global_scope, "y")]
    assert len(y_var.field_metadata) == 1
    assert y_var.field_metadata[0].class_field_value == "10"
    assert y_var.field_metadata[0].class_field_type == "int"
    
    # Check z (only type hint)
    assert (global_scope, "z") in var_dict
    z_var = var_dict[(global_scope, "z")]
    assert len(z_var.field_metadata) == 1
    assert z_var.field_metadata[0].class_field_value is None
    assert z_var.field_metadata[0].class_field_type == "list"
    
    # Check w (complex value)
    assert (global_scope, "w") in var_dict
    w_var = var_dict[(global_scope, "w")]
    assert len(w_var.field_metadata) == 1
    assert w_var.field_metadata[0].class_field_value == "1 + 2 * 3"
    assert w_var.field_metadata[0].class_field_type is None
    
    # Check s (type hint and string value)
    assert (global_scope, "s") in var_dict
    s_var = var_dict[(global_scope, "s")]
    assert len(s_var.field_metadata) == 1
    assert s_var.field_metadata[0].class_field_value == '"test"'
    assert s_var.field_metadata[0].class_field_type == "str"

def test_comprehensive_variables(parser: NodeVariablesParser):
    """Test parsing variables in a complex Python file with multiple scenarios."""
    code = """
    from typing import List, Dict, Optional
    import os
    from datetime import datetime
    
    # Global constants
    MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 1000
    ERROR_MESSAGES = {
        "404": "Not Found",
        "500": "Server Error"
    }
    
    # Global variables with type hints
    count: int
    items: List[str]
    
    # Global variables with values
    count = 0
    items = ["a", "b"]
    
    # Global variables with type hints and values
    data: Dict[str, int] = {"a": 1}
    status: bool = True
    
    # Global variable with computation
    total = 10 * 5
    
    # Global tuple unpacking
    x, y = 1, 2
    
    class FirstClass:
        # Class constants
        MAX_ITEMS = 100
        DEFAULT_VALUES = ["default"]
        STATUS_CODES = {
            "SUCCESS": 200,
            "ERROR": 400
        }
        
        # Class variables with type hints
        class_count: int
        class_items: List[str]
        
        # Class variables with values
        class_count = 10
        class_items = ["x", "y"]
        
        # Class variables with type hints and values
        class_data: Dict[str, int] = {"x": 1}
        class_status: bool = False
        
        # Class variable with computation
        class_total = 20 * 3
        
        # Class tuple unpacking
        a, b = "test", 123
    
    class SecondClass:
        # Decorated class variables
        @property
        name: str = "second"
        
        @deprecated
        old_var = "legacy"
        
        # Multiple decorators
        @classmethod
        @validator("field")
        field_value = 42
        
        def __init__(self):
            # Instance variables - should not be captured
            self.instance_var = "instance"
            self.count = 0
        
        def process(self):
            # More instance variables - should not be captured
            self.processed = True
            self.status: bool = False
            
            # Local variables - should not be captured
            local_var = "local"
    """
    
    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}
    
    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value
    
    # Check global constants
    assert (global_scope, "MAX_RETRIES") in var_dict
    max_retries = var_dict[(global_scope, "MAX_RETRIES")]
    assert len(max_retries.field_metadata) == 1
    assert max_retries.field_metadata[0].class_field_value == "3"
    
    # Check global variables with type hints and latest value
    assert (global_scope, "count") in var_dict
    count_var = var_dict[(global_scope, "count")]
    assert len(count_var.field_metadata) == 2  # One for type hint, one for value
    assert count_var.field_metadata[0].class_field_type == "int"
    assert count_var.field_metadata[1].class_field_value == "0"
    
    # Check global variables with type hints and values in single declaration
    assert (global_scope, "data") in var_dict
    data_var = var_dict[(global_scope, "data")]
    assert len(data_var.field_metadata) == 1
    assert data_var.field_metadata[0].class_field_type == "Dict[str, int]"
    assert data_var.field_metadata[0].class_field_value == '{"a": 1}'
    
    # Check global tuple unpacking
    assert (global_scope, "x") in var_dict
    x_var = var_dict[(global_scope, "x")]
    assert len(x_var.field_metadata) == 1
    assert x_var.field_metadata[0].class_field_value == "1"
    
    # Class scope - FirstClass
    first_class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check class constants
    assert (first_class_scope, "MAX_ITEMS") in var_dict
    max_items = var_dict[(first_class_scope, "MAX_ITEMS")]
    assert len(max_items.field_metadata) == 1
    assert max_items.field_metadata[0].class_field_value == "100"
    
    # Check class variables with type hints and values
    assert (first_class_scope, "class_count") in var_dict
    class_count = var_dict[(first_class_scope, "class_count")]
    assert len(class_count.field_metadata) == 2  # One for type hint, one for value
    assert class_count.field_metadata[0].class_field_type == "int"
    assert class_count.field_metadata[1].class_field_value == "10"
    
    # Class scope - SecondClass
    second_class_scope = ClassGlobalFieldScope.CLASS.value
    
    # Check decorated variables
    assert (second_class_scope, "name") in var_dict
    name_var = var_dict[(second_class_scope, "name")]
    assert len(name_var.field_metadata) == 1
    assert name_var.field_metadata[0].class_field_type == "str"
    assert name_var.field_metadata[0].class_field_value == '"second"'
    assert name_var.field_metadata[0].annotations is not None
    assert len(name_var.field_metadata[0].annotations) == 1
    assert name_var.field_metadata[0].annotations[0].name == "property"
    
    # Check multiple decorators
    assert (second_class_scope, "field_value") in var_dict
    field_value = var_dict[(second_class_scope, "field_value")]
    assert len(field_value.field_metadata) == 1
    assert field_value.field_metadata[0].class_field_value == "42"
    assert field_value.field_metadata[0].annotations is not None
    assert len(field_value.field_metadata[0].annotations) == 2
    annotation_names = [a.name for a in field_value.field_metadata[0].annotations]
    assert "classmethod" in annotation_names
    assert "validator" in annotation_names
    
    # Verify instance variables are not captured
    assert (second_class_scope, "instance_var") not in var_dict
    assert (second_class_scope, "count") not in var_dict
    assert (second_class_scope, "processed") not in var_dict
    assert (second_class_scope, "status") not in var_dict
    
    # Verify local variables are not captured
    assert (second_class_scope, "local_var") not in var_dict

def test_variable_scopes(parser: NodeVariablesParser):
    """Test variables in different scopes."""
    code = """
    a = 1

    class MyClass:
        b = 2

        def method(self):
            c = 3
    """

    variables = parser.parse_variables(code)
    var_dict = {(v.scope, v.class_field_name): v for v in variables}

    # Global scope
    global_scope = ClassGlobalFieldScope.GLOBAL.value

    # Global variable 'a'
    assert (global_scope, "a") in var_dict
    a_var = var_dict[(global_scope, "a")]
    assert len(a_var.field_metadata) == 1
    assert a_var.field_metadata[0].class_field_value == "1"

    # Class scope
    class_scope = ClassGlobalFieldScope.CLASS.value

    # Class variable 'b' in MyClass
    assert (class_scope, "b") in var_dict
    b_var = var_dict[(class_scope, "b")]
    assert len(b_var.field_metadata) == 1
    assert b_var.field_metadata[0].class_field_value == "2"

    # Variable 'c' inside method should not be included (since we're skipping function variables)
    assert (class_scope, "c") not in var_dict