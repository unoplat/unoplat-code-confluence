from typing import ClassVar, List, Dict, Any
import pytest
import os
from datetime import datetime
import json

from unoplat_code_confluence.data_models.chapi.chapi_class_global_fieldmodel import ClassGlobalFieldModel
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
    

def test_extreme_function(parser: FunctionMetadataParser):
    content = r'''
    def extreme_test_function(data: str, check: bool = True) -> Union[Tuple[int, str], Literal["error"]]:
        # Complex assignments

        # Deeply nested pattern assignment
        (w, (x, (y, z))) = (1, (2, (3, 4)))
        
        # Starred expression
        first, *middle, last = [10, 20, 30, 40, 50]

        # Complex type hints with value
        complex_data: Dict[str, Dict[str, List[Optional[int]]]] = {"outer": {"inner": [None, 1, 2]}}

        # Callable type hint with function call as default
        # Using partial to create a complex default value
        custom_func: Callable[[int, str], bool] = partial(some_validation_function, prefix="test_")

        # Assignments inside conditions with walrus operator
        f = 0
        while (line := input_stream.readline()) != "":
            processed_line = line.strip()
            # local var, no special logic needed beyond capturing

        # Walrus operator in comprehension
        lines = ["alpha", "beta", "gamma"]
        comp_values = [matched.group(1) for line in lines if (matched := regex.match(r"(\w+)", line))]

        dynamic_value = "dynamic_value"
        result_data = complicated_call(
            10,
            (lambda q: q + 2)(5),
            named="value",
            **{"dynamic_key": dynamic_value}
        )

        # Chained attribute calls and slicing
        extracted = helper.manager.datasets["mydata"][1:10].clean().finalize()

        # Inline assignment in comprehension
        comp_list = [matched_item[0] for matched_item in (regex.findall(r"(a|b)", line) for line in lines) if matched_item]

        # Complex return type and complex return value
        # Return a tuple that matches Union[Tuple[int, str], Literal["error"]]
        # Just return (42, "meaning") for now
        return (42, "meaning")
    '''

    # Construct a ChapiFunction object to simulate real scenario
    test_func = create_sample_function(
        name="extreme_test_function",
        parameters=[
            ChapiParameter(TypeValue="data", TypeType="str"),
            ChapiParameter(TypeValue="True", TypeType="check")
        ],
        annotations=[
            ChapiAnnotation(Name="cachetools.cached", KeyValues=[{"Key": "0", "Value": "{}"}]),
            ChapiAnnotation(Name="custom_decorator", KeyValues=[{"Key": "arg", "Value": '"value"'}])
        ],
        content=content
    )
    
    # Parse the function
    parsed_functions = parser.process_functions([test_func])
    parsed_function = parsed_functions[0]

    # Assertions:
    # Here, we won't assert every detail, but we focus on ensuring the parser doesn't fail and captures:
    # - Complex local variables as is.
    # - Function calls with complex args.
    # - Type hints and values remain unchanged.
    # - Return type is recorded correctly.
    # - No attempts to handle runtime class/instance vars.

    # Basic checks:
    assert parsed_function.name == "extreme_test_function"
    # Check return type was parsed
    assert parsed_function.return_type == 'Union[Tuple[int, str], Literal["error"]]'  # Exact text as in code

    # Check for presence of local variables and calls
    # For complexity, just check that certain known variable names appear in local variables
    local_var_names = [lv.function_variable_name for lv in parsed_function.local_variables]
    # Variables from pattern assignments
    assert "w" in local_var_names
    assert "x" in local_var_names
    assert "y" in local_var_names
    assert "z" in local_var_names
    # Star expression variable
    assert "first" in local_var_names
    assert "last" in local_var_names

    # Check that a complex function call like 'complicated_call(...)' is captured
    call_names = [c.function_name for c in parsed_function.function_calls]
    assert "complicated_call" in call_names  # It's a key function call

    # No runtime class vars or self.x handling: Just ensure no weird references appeared as local vars
    # For instance, if code had self.data = ... we wouldn't see 'data' from self assignment as local var
    # Just trust that we never wrote code referencing `self.x` as local var here.

    # Check that no values are stripped:
    # Find a local var known to have a complex value, like 'complex_data'
    complex_data_var = next((lv for lv in parsed_function.local_variables if lv.function_variable_name == "complex_data"), None)
    assert complex_data_var is not None
    assert "Dict[str, Dict[str, List[Optional[int]]]]" in (complex_data_var.function_variable_type or "")
    # Check value still has original structure
    assert '"outer"' in (complex_data_var.function_variable_value or "")

    # If you want to verify no simplifications:
    # E.g., result_data = complicated_call(...) should still have 'complicated_call(...' in the value
    result_data_var = next((lv for lv in parsed_function.local_variables if lv.function_variable_name == "result_data"), None)
    assert result_data_var is not None
    assert "complicated_call" in (result_data_var.function_variable_value or "")

    # If no errors occur and assertions pass, we've tested a complex scenario successfully.    


