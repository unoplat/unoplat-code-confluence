from typing import Dict

import pytest

from src.code_confluence_flow_bridge.models.configuration.settings import ProgrammingLanguage
from src.code_confluence_flow_bridge.parser.python.python_extract_function_calls import PythonExtractFunctionCalls
from src.code_confluence_flow_bridge.parser.tree_sitter.code_confluence_tree_sitter import CodeConfluenceTreeSitter

@pytest.fixture
def extractor() -> PythonExtractFunctionCalls:
    """Create PythonExtractFunctionCalls with real tree-sitter parser."""
    tree_sitter = CodeConfluenceTreeSitter(language=ProgrammingLanguage.PYTHON)
    return PythonExtractFunctionCalls(code_confluence_tree_sitter=tree_sitter)

def test_extract_instantiations_ts(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of class instantiations from Python code with multiple scenarios."""
    # Test file with various instantiation patterns
    file_source: str = """
# Simple instantiation
calculator = Calculator()

# Instantiation with arguments
parser = ArgumentParser(description="Test parser")

# Type-annotated instantiation (global scope)
config: Configuration = Configuration()

# Multiple instantiations
validator = DataValidator()
formatter = OutputFormatter()

def process_data():
    # Instantiation inside function
    processor = DataProcessor()
    
    # Type-annotated instantiation inside function
    logger: Logger = Logger()
    
    def nested_function():
        # Type-annotated instantiation in nested function
        cache: Cache = Cache()
        
        # Tuple unpacking inside nested function
        client, server = Client(), Server()
        
        return cache.get()
    
    return processor.run()

class TestClass:
    def __init__(self):
        # Instantiation in method
        self.helper = HelperClass()
        
        # Type-annotated attribute
        self.config: Config = Config()
        
    def test_method(self):
        # Another instantiation
        tester = TestRunner()
        
        # Tuple unpacking in method
        reader, writer = FileReader(), FileWriter()
        
        def inner_method():
            # Type-annotated in nested method function
            validator: Validator = Validator()
            
            # Tuple unpacking in nested method function
            model, view = Model(), View()
            return model.process()
        
        return tester.execute()

# Should not match these:
not_a_class = function_call()
also_not_class = my_var.method()
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Expected instantiations
    expected: Dict[str, str] = {
        "calculator": "Calculator",
        "parser": "ArgumentParser",
        "config": "Configuration",
        "validator": "DataValidator",
        "formatter": "OutputFormatter",
        "processor": "DataProcessor",
        "logger": "Logger",
        "cache": "Cache",
        "client": "Client",
        "server": "Server",
        "self.helper": "HelperClass",
        "self.config": "Config",
        "tester": "TestRunner",
        "reader": "FileReader",
        "writer": "FileWriter",
        "validator": "Validator",
        "model": "Model",
        "view": "View"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"

def test_extract_instantiations_ts_with_complex_structures(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of instantiations from complex Python code structures with nested elements."""
    file_source: str = """
# Procedural code with nested functions
def outer_function():
    # Instantiation in outer function
    logger = Logger()
    
    def inner_function():
        # Instantiation in inner function
        validator = Validator()
        return validator.validate()
    
    # Class instantiation in tuple unpacking within a function
    connection, session = DatabaseConnection(), SessionManager()
    
    return inner_function()

# Classes with nested methods and functions
class ComplexProcessor:
    def __init__(self):
        # Standard instantiation in constructor
        self.parser = ConfigParser()
        
    def process(self, data):
        # Attribute assignment in method
        self.helper = ProcessHelper()
        
        def local_processor():
            # Instantiation in a function inside a method
            transformer = DataTransformer()
            return transformer.transform(data)
        
        # Multiple instantiations in tuple unpacking in a method
        input_handler, output_handler = InputHandler(), OutputHandler()
        
        return local_processor()

# Procedural code after class definition
strategy = ProcessingStrategy()

# Should not match these
result = calculate_sum(10, 20)
data = process_list([1, 2, 3])
a, b = get_values(), fetch_data()  # Should not match as function names don't start with uppercase
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Expected instantiations
    expected: Dict[str, str] = {
        "logger": "Logger",
        "validator": "Validator",
        "connection": "DatabaseConnection",
        "session": "SessionManager",
        "self.parser": "ConfigParser",
        "self.helper": "ProcessHelper",
        "transformer": "DataTransformer",
        "input_handler": "InputHandler", 
        "output_handler": "OutputHandler",
        "strategy": "ProcessingStrategy"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"

def test_extract_instantiations_ts_with_complex_assignments(extractor: PythonExtractFunctionCalls) -> None:
    """Test extraction of instantiations with more complex assignment patterns."""
    file_source: str = """
# Multiple assignments
b = MyClass()

e : MyDerivedClass = MyDerivedClass()

# Tuple unpacking (should match)
x, y = Point(), Vector()

# Attribute assignment (should match)
obj.attr = Helper()
"""

    result: Dict[str, str] = extractor.extract_instantiations_ts(file_source)
    
    # Should only match simple assignments
    expected: Dict[str, str] = {
        "b": "MyClass",
        "e": "MyDerivedClass",
        "x": "Point",
        "y": "Vector",
        "obj.attr": "Helper"
    }
    
    assert result == expected, f"Expected {expected}, got {result}"