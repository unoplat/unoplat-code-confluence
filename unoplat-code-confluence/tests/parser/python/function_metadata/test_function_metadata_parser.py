from typing import List, Dict, Any
import pytest
import os
from datetime import datetime
import json

from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction
from unoplat_code_confluence.data_models.chapi.chapi_functioncall import ChapiFunctionCall
from unoplat_code_confluence.data_models.chapi.chapi_function_field_model import ChapiFunctionFieldModel
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter
from unoplat_code_confluence.data_models.chapi.chapi_position import Position
from unoplat_code_confluence.data_models.chapi.chapi_annotation import ChapiAnnotation
from unoplat_code_confluence.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter
from unoplat_code_confluence.parser.python.function_metadata.function_metadata_parser import FunctionMetadataParser
from unoplat_code_confluence.configuration.settings import ProgrammingLanguage

@pytest.fixture
def parser() -> FunctionMetadataParser:
    """Create parser instance with Python language."""
    tree_sitter = CodeConfluenceTreeSitter(ProgrammingLanguage.PYTHON)
    return FunctionMetadataParser(tree_sitter)

def create_sample_function(
    name: str = "sample_function",
    parameters: List[ChapiParameter] = None,
    annotations: List[ChapiAnnotation] = None,
    content: str = None,
    position: Position = None
) -> ChapiFunction:
    """Create a sample ChapiFunction with given parameters.
    
    Args:
        name: Function name
        parameters: List of function parameters
        annotations: List of function decorators
        content: Function body content
        position: Function position in code
        
    Returns:
        ChapiFunction with all fields set except return_type, function_calls, and local_variables
    """
    if parameters is None:
        parameters = []
    if annotations is None:
        annotations = []
    if position is None:
        position = Position(
            StartLine=1,
            StartLinePosition=0,
            StopLine=1,
            StopLinePosition=0
        )
    if content is None:
        content = "pass"
        
    return ChapiFunction(
        Name=name,
        Parameters=parameters,
        Annotations=annotations,
        Position=position,
        Content=content,
        # These will be filled by parser:
        ReturnType=None,
        FunctionCalls=[],
        LocalVariables=[]
    )

@pytest.fixture
def sample_function_with_variables() -> ChapiFunction:
    """Create a sample function with local variables and type hints."""
    content = """
    def test_variables():
        # Simple assignment
        x = 1
        
        # With type hint
        y: int = 2
        
        # Only type hint
        z: str
        
        # Reassignment
        x = "changed"
        
        # Keep type hint from earlier
        y = 3
        
        # Complex assignments
        result: List[int] = []
        data: Dict[str, Any] = {"key": "value"}
        
        # Multiple assignments in one line
        a, b = 1, 2
        
        return x
    """
    return create_sample_function(
        name="test_variables",
        content=content
    )
    
@pytest.fixture
def sample_function_with_complex_variables() -> ChapiFunction:
    """Create a sample function with local variables and type hints."""
    content = """
    def test_variables():
        # Simple assignment
        x = 1
        
        # With type hint
        y: int = 2
        
        # Only type hint
        z: str
        
        # Reassignment
        x = "changed"
        
        # Keep type hint from earlier
        y = "3"
        
        # Complex assignments
        result: List[int] = []
        data: Dict[str, Any] = {"key": "value"}
        
        # Multiple assignments in one line
        a, b = 1, 2
        
        return x
    """
    return create_sample_function(
        name="test_variables",
        content=content
    )    

@pytest.fixture
def sample_function_with_complex_variables_2() -> ChapiFunction:
    """Create a sample function with local variables and type hints."""
    content = """
   def extreme_test_variables():
    # Simple assignment
    x = 1
    
    # With type hint and value
    y: int = 2
    
    # Only type hint (no initial value)
    z: str
    
    # Reassignment to different type (no hint change)
    x = "re-changed"
    
    # Reassignment of y with different value type (hint stays the same)
    y = [1, 2, 3]  # Still 'int' hinted originally, but assigned list
    
    # Tuple unpacking
    a, b = 1, 2
    
    # Nested pattern unpacking (Python 3.10+)
    (c, (d, e)) = (3, (4, 5))
    
    # Complex type hints
    result: List[int] = []
    data: Dict[str, Any] = {"key": "value"}
    
    # Walrus operator assignment
    # Assign inline and check last value
    f = 0
    while (n := f) < 3:
        f += 1
    # After loop, f = 3, n = 2 (last successful comparison)
    
    # Assign inside if statement
    if True:
        g: float = 10.5
        g = 11.0
    
    # Assign with lambda capturing a local var
    h = lambda u: u + f  # f is 3 here
    h_result = h(5)  # h_result = 8 not a variable definition just call
    
    # Assign from a comprehension
    comp_list = [x * 2 for x in range(3)]  # x here shadows above variable in comprehension scope, 
                                           # but we only track top-level assignments, so ignore comprehension scope
    comp_dict = {f"key{i}": i for i in range(3)}
    comp_set = {j for j in range(3)}
    
    # Assign via function call
    def inner():
        return "inner_value"
    inner_var = inner()
    
    # Reassign z to test only-type var gets a value now
    z = "now assigned"
    
    # Another re-reassignment of y to confirm type hint still does not change
    y = "string now"
    
    # Multiple assignment with nested patterns again
    (p, q), r = (("nested", True), 42)
    
    # Return a variable to ensure parser sees final usage
    return x
    """
    return create_sample_function(
        name="test_variables",
        content=content
    )    


@pytest.fixture
def sample_function_with_calls() -> ChapiFunction:
    """Create a sample function with function calls."""
    content = """
    def test_calls(data: str, validate: bool = True):
        # Simple function call
        result = calculate(1, 2)
        
        # Method call with keyword args
        self.process(data=result)
        
        # Chained method call
        helper.util.format(text="test")
        
        # Call with multiple args
        process_all(
            data,
            validate=validate,
            retry=3
        )
        
        return result
    """
    return create_sample_function(
        name="test_calls",
        parameters=[
            ChapiParameter(TypeValue="data", TypeType="str"),
            ChapiParameter(TypeValue="True", TypeType="validate")
        ],
        content=content
    )

@pytest.fixture
def sample_function_with_return_type() -> ChapiFunction:
    """Create a sample function with return type annotation."""
    content = """
    def get_value() -> str:
        # Local variable
        x = "test"
        
        # Some processing
        x = x.strip().upper()
        
        return x
    """
    return create_sample_function(
        name="get_value",
        content=content
    )

@pytest.fixture
def complex_sample_function() -> ChapiFunction:
    """Create a complex function with multiple features."""
    content = """
    @validator
    @deprecated
    def process_data(self, data: dict, retry: int = 3) -> Optional[List[str]]:
        # Local variables
        result = []
        count: int = 0
        
        # Function calls
        self.validate(data)
        processed = helper.process(data, validate=True)
        
        # Multiple assignments
        x = 1
        x: int = 2
        x = "changed"
        
        return result
    """
    
    parameters = [
        ChapiParameter(TypeValue="self"),
        ChapiParameter(TypeValue="data", TypeType="dict"),
        ChapiParameter(TypeValue="3", TypeType="retry")
    ]
    
    annotations = [
        ChapiAnnotation(Name="validator"),
        ChapiAnnotation(Name="deprecated")
    ]
    
    return create_sample_function(
        name="process_data",
        parameters=parameters,
        annotations=annotations,
        content=content
    )

def test_local_variables_with_complex_types(parser: FunctionMetadataParser, sample_function_with_complex_variables: ChapiFunction):
    """Test handling of complex type hints and first assignments."""
    result = parser.get_function_metadata(sample_function_with_complex_variables)
    
    var_dict = {v.function_variable_name: v for v in result.local_variables}
    
    # Check x (first assignment only)
    assert "x" in var_dict
    x_var = var_dict["x"]
    assert x_var.function_variable_type is None  # No type hint
    assert x_var.function_variable_value == "1"  # First value only
    
    # Check y (type hint with initial value)
    assert "y" in var_dict
    y_var = var_dict["y"]
    assert y_var.function_variable_type == "int"  # Type hint
    assert y_var.function_variable_value == "2"  # Initial value only
    
    # Check z (only type hint, no value)
    assert "z" in var_dict
    z_var = var_dict["z"]
    assert z_var.function_variable_type == "str"  # Type hint
    assert z_var.function_variable_value is None  # No value assigned
    
    # Check complex type hints with initial values
    assert "result" in var_dict
    result_var = var_dict["result"]
    assert result_var.function_variable_type == "List[int]"  # Complex type hint
    assert result_var.function_variable_value == "[]"  # Initial empty list
    
    assert "data" in var_dict
    data_var = var_dict["data"]
    assert data_var.function_variable_type == "Dict[str, Any]"  # Complex type hint
    assert data_var.function_variable_value == '{"key": "value"}'  # Initial dict value
    
    # Check multiple assignments (first values only)
    assert "a" in var_dict
    a_var = var_dict["a"]
    assert a_var.function_variable_type is None  # No type hint
    assert a_var.function_variable_value == "1"  # First value from tuple unpacking
    
    assert "b" in var_dict
    b_var = var_dict["b"]
    assert b_var.function_variable_type is None  # No type hint
    assert b_var.function_variable_value == "2"  # First value from tuple unpacking
    
    # Verify total number of variables
    assert len(var_dict) == 7  # x, y, z, result, data, a, b

def test_local_variables_tracking(parser: FunctionMetadataParser, sample_function_with_variables: ChapiFunction):
    """Test that local variables are correctly tracked with their first assignments."""
    result = parser.get_function_metadata(sample_function_with_variables)
    
    # Convert to dict for easier lookup
    var_dict = {v.function_variable_name: v for v in result.local_variables}
    
    # Check x (first assignment only)
    assert "x" in var_dict
    x_var = var_dict["x"]
    assert x_var.function_variable_type is None  # No type hint
    assert x_var.function_variable_value == "1"  # First value only
    
    # Check y (type hint with initial value)
    assert "y" in var_dict
    y_var = var_dict["y"]
    assert y_var.function_variable_type == "int"  # Type hint
    assert y_var.function_variable_value == "2"  # Initial value only
    
    # Check z (only type hint)
    assert "z" in var_dict
    z_var = var_dict["z"]
    assert z_var.function_variable_type == "str"  # Type hint
    assert z_var.function_variable_value is None  # No value assigned
    
    # Check complex type hints with initial values
    assert "result" in var_dict
    result_var = var_dict["result"]
    assert result_var.function_variable_type == "List[int]"  # Complex type hint
    assert result_var.function_variable_value == "[]"  # Initial empty list
    
    assert "data" in var_dict
    data_var = var_dict["data"]
    assert data_var.function_variable_type == "Dict[str, Any]"  # Complex type hint
    assert data_var.function_variable_value == '{"key": "value"}'  # Initial dict value
    
    # Check multiple assignments in one line (first values only)
    assert "a" in var_dict
    a_var = var_dict["a"]
    assert a_var.function_variable_type is None  # No type hint
    assert a_var.function_variable_value == "1"  # First value from tuple unpacking
    
    assert "b" in var_dict
    b_var = var_dict["b"]
    assert b_var.function_variable_type is None  # No type hint
    assert b_var.function_variable_value == "2"  # First value from tuple unpacking
    
    # Verify total number of variables
    assert len(var_dict) == 7  # x, y, z, result, data, a, b

def test_function_calls_tracking(parser: FunctionMetadataParser, sample_function_with_calls: ChapiFunction):
    """Test that function calls are correctly tracked with their parameters."""
    result = parser.get_function_metadata(sample_function_with_calls)
    
    assert len(result.function_calls) == 4
    
    # Check simple function call
    calculate_call = next(call for call in result.function_calls if call.function_name == "calculate")
    assert len(calculate_call.parameters) == 2
    assert calculate_call.parameters[0].type_value == "1"
    assert calculate_call.parameters[1].type_value == "2"
    
    # Check method call with keyword args
    process_call = next(call for call in result.function_calls if call.function_name == "process")
    assert process_call.node_name == "self"
    assert len(process_call.parameters) == 1
    assert process_call.parameters[0].type_type == "data"
    
    # Check chained method call
    format_call = next(call for call in result.function_calls if call.function_name == "format")
    assert format_call.node_name == "helper.util"
    assert len(format_call.parameters) == 1
    assert format_call.parameters[0].type_type == "text"
    assert format_call.parameters[0].type_value == '"test"'
    
    # Check call with multiple args
    process_all_call = next(call for call in result.function_calls if call.function_name == "process_all")
    assert len(process_all_call.parameters) == 3
    assert process_all_call.parameters[0].type_value == "data"
    assert process_all_call.parameters[1].type_type == "validate"
    assert process_all_call.parameters[2].type_type == "retry"
    assert process_all_call.parameters[2].type_value == "3"

def test_return_type_extraction(parser: FunctionMetadataParser, sample_function_with_return_type: ChapiFunction):
    """Test that return type annotations are correctly extracted."""
    result = parser.get_function_metadata(sample_function_with_return_type)
    
    assert result.return_type == "str"
    
    # Also check that local variables are tracked
    var_dict = {v.function_variable_name: v for v in result.local_variables}
    assert "x" in var_dict
    assert var_dict["x"].function_variable_value == '"test"'

def test_complex_function_metadata(parser: FunctionMetadataParser, complex_sample_function: ChapiFunction):
    """Test all aspects of function metadata extraction."""
    result = parser.get_function_metadata(complex_sample_function)
    
    # Check return type
    assert result.return_type == "Optional[List[str]]"
    
    # Check local variables
    var_dict = {v.function_variable_name: v for v in result.local_variables}
    
    # Define expected variables first
    expected_vars = {"result", "count", "x", "processed"}
    
    # Check result variable (first assignment)
    assert "result" in var_dict
    assert var_dict["result"].function_variable_value == "[]"
    assert var_dict["result"].function_variable_type is None
    
    # Check count with type hint (first assignment)
    assert "count" in var_dict
    assert var_dict["count"].function_variable_type == "int"
    assert var_dict["count"].function_variable_value == "0"
    
    # Check x (first assignment)
    assert "x" in var_dict
    x_var = var_dict["x"]
    assert x_var.function_variable_type is None  # No type hint in first assignment
    assert x_var.function_variable_value == "1"  # First value
    
    # Check processed from function call
    assert "processed" in var_dict
    processed_var = var_dict["processed"]
    assert processed_var.function_variable_type is None
    assert processed_var.function_variable_value == "helper.process(data, validate=True)"
    
    # Check function calls
    assert len(result.function_calls) == 2
    
    # Check validate call
    validate_call = next(call for call in result.function_calls if call.function_name == "validate")
    assert validate_call.node_name == "self"
    assert len(validate_call.parameters) == 1
    assert validate_call.parameters[0].type_value == "data"
    
    # Check process call
    process_call = next(call for call in result.function_calls if call.function_name == "process")
    assert process_call.node_name == "helper"
    assert len(process_call.parameters) == 2
    assert process_call.parameters[0].type_value == "data"
    assert process_call.parameters[1].type_type == "validate"
    assert process_call.parameters[1].type_value == "True"
    
    # Verify total number of variables
    assert len(var_dict) == len(expected_vars)
    assert set(var_dict.keys()) == expected_vars

def test_ast_debug(parser: FunctionMetadataParser):
    """Test to print AST structure for analysis."""
    code = """
    @validator
    @deprecated
    def process_data(self, data: dict, retry: int = 3) -> Optional[List[str]]:
        # Local variables
        result = []
        count: int = 0
        
        # Function calls
        self.validate(data)
        processed = helper.process(data, validate=True)
        
        # Multiple assignments
        x = 1
        x: int = 2
        x = "changed"
        
        return result
    """
    
    # Create a sample function
    test_func = create_sample_function(
        name="complex_function_2",
        content=code
    )
    
    # Parse and get AST
    tree = parser.parser.parse(bytes(test_func.content, "utf8"))
    
    # Debug: Save AST to JSON
    debug_dir = "debug_output"
    os.makedirs(debug_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def node_to_dict(node):
        result = {
            "type": node.type,
            "text": node.text.decode('utf8') if node.text else None,
            "start_point": node.start_point,
            "end_point": node.end_point,
        }
        if len(node.children) > 0:
            result["children"] = [node_to_dict(child) for child in node.children]
        return result
        
    ast_dict = node_to_dict(tree.root_node)
    ast_file = f"{debug_dir}/function_ast_{timestamp}.json"
    with open(ast_file, "w") as f:
        json.dump(ast_dict, f, indent=2)

def test_local_variables_with_complex_types_2(parser: FunctionMetadataParser, sample_function_with_complex_variables_2: ChapiFunction):
    """Test handling of complex variable scenarios including nested patterns, walrus operator, and comprehensions."""
    result = parser.get_function_metadata(sample_function_with_complex_variables_2)
    
    var_dict = {v.function_variable_name: v for v in result.local_variables}
    
    # Define expected variables first
    expected_vars = {"x", "y", "z", "a", "b", "c", "d", "e", "result", "data", 
                    "f", "n", "g", "h", "comp_list", "comp_dict", "comp_set", 
                    "inner_var", "p", "q", "r","h_result"}
    
    # Debug: Print all variables
    print("\nActual variables:", sorted(var_dict.keys()))
    print("Expected variables:", sorted(expected_vars))
    
    # Check basic assignments (first values only)
    assert "x" in var_dict
    x_var = var_dict["x"]
    assert x_var.function_variable_type is None  # No type hint
    assert x_var.function_variable_value == "1"  # First value only
    
    # Check type hint with value
    assert "y" in var_dict
    y_var = var_dict["y"]
    assert y_var.function_variable_type == "int"  # Type hint
    assert y_var.function_variable_value == "2"  # Initial value only
    
    # Check type hint only
    assert "z" in var_dict
    z_var = var_dict["z"]
    assert z_var.function_variable_type == "str"  # Type hint
    assert z_var.function_variable_value is None  # No initial value
    
    # Check simple tuple unpacking
    assert "a" in var_dict
    assert "b" in var_dict
    assert var_dict["a"].function_variable_value == "1"
    assert var_dict["b"].function_variable_value == "2"
    
    # Check nested pattern unpacking
    assert "c" in var_dict
    assert "d" in var_dict
    assert "e" in var_dict
    assert var_dict["c"].function_variable_value == "3"
    assert var_dict["d"].function_variable_value == "4"
    assert var_dict["e"].function_variable_value == "5"
    
    # Check complex type hints
    assert "result" in var_dict
    result_var = var_dict["result"]
    assert result_var.function_variable_type == "List[int]"
    assert result_var.function_variable_value == "[]"
    
    assert "data" in var_dict
    data_var = var_dict["data"]
    assert data_var.function_variable_type == "Dict[str, Any]"
    assert data_var.function_variable_value == '{"key": "value"}'
    
    # Check walrus operator assignment
    assert "f" in var_dict
    assert var_dict["f"].function_variable_value == "0"  # Initial value
    
    assert "n" in var_dict  # Created by walrus operator
    assert var_dict["n"].function_variable_value == "n := f"  # Keep full walrus expression
    
    # Check if-statement variable
    assert "g" in var_dict
    g_var = var_dict["g"]
    assert g_var.function_variable_type == "float"  # Type hint
    assert g_var.function_variable_value == "10.5"  # Initial value
    
    # Check lambda assignment with exact value
    assert "h" in var_dict
    h_var = var_dict["h"]
    assert h_var.function_variable_value == "lambda u: u + f"
    assert h_var.function_variable_type is None
    
    # Check comprehension results with exact values
    assert "comp_list" in var_dict
    assert var_dict["comp_list"].function_variable_value == "[x * 2 for x in range(3)]"
    
    assert "comp_dict" in var_dict
    assert var_dict["comp_dict"].function_variable_value == '{f"key{i}": i for i in range(3)}'
    
    assert "comp_set" in var_dict
    assert var_dict["comp_set"].function_variable_value == "{j for j in range(3)}"
    
    # Check function result assignment
    assert "inner_var" in var_dict
    assert var_dict["inner_var"].function_variable_value == "inner"  # Just function name
    assert var_dict["inner_var"].function_variable_type is None
    
    # Check nested pattern assignment
    assert "p" in var_dict
    assert "q" in var_dict
    assert "r" in var_dict
    assert var_dict["p"].function_variable_value == '"nested"'
    assert var_dict["q"].function_variable_value == "True"
    assert var_dict["r"].function_variable_value == "42"
    
    # Verify we don't capture:
    # - Loop variables (i, j in comprehensions)
    # - Function parameters (u in lambda)
    # - Local variables in inner functions
    assert "i" not in var_dict  # Comprehension variable
    assert "j" not in var_dict  # Comprehension variable
    assert "u" not in var_dict  # Lambda parameter
    
    # Verify total number of variables
    assert len(var_dict) == len(expected_vars)
    assert set(var_dict.keys()) == expected_vars  # Verify exact set of variables