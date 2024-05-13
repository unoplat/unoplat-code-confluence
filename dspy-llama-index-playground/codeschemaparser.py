
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import json

# Define the Parameter model
class Parameter(BaseModel):
    TypeValue: str
    TypeType: str

# Define the LocalVariable model
class LocalVariable(BaseModel):
    TypeValue: str
    TypeType: str

# Define the Position model
class Position(BaseModel):
    StartLine: int
    StartLinePosition: int
    StopLine: int
    StopLinePosition: int

# Define the FunctionCall model
class FunctionCall(BaseModel):
    Package: str
    NodeName: str
    FunctionName: str
    Parameters: List[Parameter]
    Position: Position
    Type: str

# Define the Function model
class Function(BaseModel):
    Name: str
    ReturnType: str
    Parameters: List[Parameter]
    FunctionCalls: List[FunctionCall]
    Position: Position
    LocalVariables: List[LocalVariable]
    BodyHash: int
    Content: str

# Define the Import model
class Import(BaseModel):
    Source: str
    
class Annotation(BaseModel):
    Name: str
    Position: Position

class Root(BaseModel):
    NodeName: str
    Module: str
    Type: str
    Package: str
    FilePath: str
    Functions: List[Function]
    Annotations: List[Annotation]
    Imports: List[Import]
    Position: Position
    Content: str


# Define the Node model
class Node(BaseModel):
    NodeName: str
    Module: str
    Type: str
    Package: str
    FilePath: str
    Functions: List[Function]
    Imports: List[Import]

    # Method to find a function by name
    def find_function_by_name(self, name: str) -> Optional[Function]:
        for function in self.Functions:
            if function.Name == name:
                return function
        return None

    # Method to find imports by source
    def find_imports_by_source(self, source: str) -> List[Import]:
        return [imp for imp in self.Imports if imp.Source == source]

# Define the root model (List of Nodes)
class Codebase(BaseModel):
    nodes: List[Node] = Field(default_factory=list)

    # Method to find a node by type, e.g., class or module
    def find_by_type(self, node_type: str) -> List[Node]:
        return [node for node in self.nodes if node.Type == node_type]

    # Method to find a node by name
    def find_by_name(self, name: str) -> Optional[Node]:
        for node in self.nodes:
            if node.NodeName == name:
                return node
        return None

    # Method to find a node by module
    def find_by_module(self, module: str) -> List[Node]:
        return [node for node in self.nodes if node.Module == module]

def load_json_from_file(file_path: str) -> Codebase:
    """Load JSON data from a file and parse it into the Codebase model."""
    with open(file_path, 'r') as file:
        data = json.load(file)
        print(f"data val {data}")
    return Codebase.model_validate_json(data)

# Example of how to use the file loading and querying
# codebase = load_json_from_file('path_to_your_file.json')
# node = codebase.find_by_name('MyClass')
# function = node.find_function_by_name('MyFunction') if node else None

if __name__ == "__main__":
    codebase = load_json_from_file('conf/schema_code.json')
    print(f"code {codebase}")

