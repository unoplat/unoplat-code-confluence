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
    local_vars = {v.function_variable_name: v for v in parsed_function.local_variables}
    
    # Instead of checking individual variables, check complete patterns
    assert "(w, (x, (y, z)))" in local_vars
    assert local_vars["(w, (x, (y, z)))"].function_variable_value == "(1, (2, (3, 4)))"
    
    # Check starred expression pattern
    assert "first, *middle, last" in local_vars
    assert local_vars["first, *middle, last"].function_variable_value == "[10, 20, 30, 40, 50]"
    
    # Rest of complex variable checks
    complex_data_var = next((lv for lv in parsed_function.local_variables if lv.function_variable_name == "complex_data"), None)
    assert complex_data_var is not None
    assert "Dict[str, Dict[str, List[Optional[int]]]]" in (complex_data_var.function_variable_type or "")
    assert '"outer"' in (complex_data_var.function_variable_value or "")
    
    # Function call checks remain same
    call_names = [c.function_name for c in parsed_function.function_calls]
    assert "complicated_call" in call_names
    
    # Check result_data with complex call
    result_data_var = next((lv for lv in parsed_function.local_variables if lv.function_variable_name == "result_data"), None)
    assert result_data_var is not None
    assert "complicated_call" in (result_data_var.function_variable_value or "")

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

def test_basic_sample_function(parser: FunctionMetadataParser):
    """Test basic function with no special features."""
    func = create_sample_function(
        name="basic_function",
        content="""
        def basic_function():
            x = 1
            y = 2
            return x + y
        """
    )
    
    parsed_functions = parser.process_functions([func])
    parsed_func = parsed_functions[0]
    
    # Basic assertions
    assert parsed_func.name == "basic_function"
    assert parsed_func.return_type is None  # No return type annotation
    
    # Check local variables
    local_vars = {v.function_variable_name: v for v in parsed_func.local_variables}
    assert len(local_vars) == 2
    assert "x" in local_vars
    assert "y" in local_vars
    assert local_vars["x"].function_variable_value == "1"
    assert local_vars["y"].function_variable_value == "2"

def test_complex_sample_function(parser: FunctionMetadataParser, complex_sample_function: ChapiFunction):
    """Test complex function with multiple features."""
    parsed_functions = parser.process_functions([complex_sample_function])
    parsed_func = parsed_functions[0]
    
    # Test return type
    assert parsed_func.return_type == "Optional[List[str]]"
    
    # Test parameters
    params = {p.type_value: p.type_type for p in parsed_func.parameters}
    assert "self" in params
    assert params["data"] == "dict"
    assert params["3"] == "retry"
    
    # Test local variables
    local_vars = {v.function_variable_name: v for v in parsed_func.local_variables}
    
    # Check result variable (initial assignment)
    assert "result" in local_vars
    assert local_vars["result"].function_variable_value == "[]"
    
    # Check count variable (initial assignment with type hint)
    assert "count" in local_vars
    assert local_vars["count"].function_variable_type == "int"
    assert local_vars["count"].function_variable_value == "0"
    
    # Check x (initial assignment only)
    assert "x" in local_vars
    assert local_vars["x"].function_variable_type is None  # No type hint in first assignment
    assert local_vars["x"].function_variable_value == "1"  # First value
    
    # Test function calls
    calls = {c.function_name: c for c in parsed_func.function_calls}
    assert "validate" in calls
    assert calls["validate"].node_name == "self"
    assert "process" in calls
    assert calls["process"].node_name == "helper"

def test_function_with_complex_variables(parser: FunctionMetadataParser, sample_function_with_complex_variables: ChapiFunction):
    """Test function with complex variable assignments."""
    parsed_functions = parser.process_functions([sample_function_with_complex_variables])
    parsed_func = parsed_functions[0]
    
    local_vars = {v.function_variable_name: v for v in parsed_func.local_variables}
    
    # Test simple assignments (initial only)
    assert "x" in local_vars
    assert local_vars["x"].function_variable_value == "1"  # First assignment value
    
    # Test type hints with initial assignment
    assert "y" in local_vars
    assert local_vars["y"].function_variable_type == "int"
    assert local_vars["y"].function_variable_value == "2"  # Initial value
    
    # Test type hint only (initial declaration)
    assert "z" in local_vars
    assert local_vars["z"].function_variable_type == "str"
    assert not local_vars["z"].function_variable_value  # No initial value
    
    # Test complex type hints (initial assignments)
    assert "result" in local_vars
    assert local_vars["result"].function_variable_type == "List[int]"
    assert local_vars["result"].function_variable_value == "[]"
    
    assert "data" in local_vars
    assert local_vars["data"].function_variable_type == "Dict[str, Any]"
    assert local_vars["data"].function_variable_value == '{"key": "value"}'
    
    # Test tuple unpacking as single pattern (initial assignment)
    assert "a, b" in local_vars
    assert local_vars["a, b"].function_variable_value == "1, 2"

def test_function_with_complex_variables_2(parser: FunctionMetadataParser, sample_function_with_complex_variables_2: ChapiFunction):
    """Test function with more complex variable patterns."""
    parsed_functions = parser.process_functions([sample_function_with_complex_variables_2])
    parsed_func = parsed_functions[0]
    
    local_vars = {v.function_variable_name: v for v in parsed_func.local_variables}
    
    # Test simple assignment (initial only)
    assert "x" in local_vars
    assert local_vars["x"].function_variable_value == "1"  # First assignment
    
    # Test initial nested pattern unpacking - assert entire pattern
    assert "(c, (d, e))" in local_vars
    assert local_vars["(c, (d, e))"].function_variable_value == "(3, (4, 5))"
    
    # Test initial walrus operator assignments
    assert "n" in local_vars
    assert "f" in local_vars
    assert local_vars["f"].function_variable_value == "0"  # Initial value
    
    # Test initial comprehension assignments (not loop variables)
    assert "comp_list" in local_vars
    assert "comp_dict" in local_vars
    assert "comp_set" in local_vars
    assert "i" not in local_vars  # Loop variable
    assert "j" not in local_vars  # Loop variable
    
    # Test initial function-scoped variable
    assert "inner_var" in local_vars
    assert local_vars["inner_var"].function_variable_value == "inner()"
    
    # Test initial nested pattern unpacking with different types - assert entire pattern
    assert "(p, q), r" in local_vars
    assert local_vars["(p, q), r"].function_variable_value == '(("nested", True), 42)'


def test_vector_index_function(parser: FunctionMetadataParser):
    code ="""
    def create_vector_index(self, label: str, property: str, dimension: int = None, similarity_function: str = 'cosine') -> None:
        query = f"CREATE VECTOR INDEX {property}_vector_index FOR (n:{label}) ON (n.{property})"
        if dimension is not None:
            query += f" OPTIONS {{indexConfig: {{`vector.dimensions`: {dimension}, `vector.similarity_function`: '{similarity_function}'}}}}"
        try:
            # Using neomodel's db object to execute the query
            db.cypher_query(query)
        except Exception as e:
            if "equivalent index already exists" in str(e):
                print(f"Vector index for {label}.{property} already exists. Skipping creation.")
            else:
                raise  # Re-raise the exception if it's not about existing index
    """
    create_vector_index = create_sample_function(
        name="create_vector_index",
        content=code
    )
    parsed_functions = parser.process_functions([create_vector_index])
    parsed_func = parsed_functions[0]
    assert parsed_func.name == "create_vector_index"
    assert parsed_func.return_type == "None"
    assert len(parsed_func.local_variables) == 1