from typing import Tuple
from typing import List, Optional , Dict
from pydantic import BaseModel, ValidationError,Field
import json
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import AgentRunner, ReActAgentWorker, ReActAgent
from llama_index.core.agent import ReActAgent
from multiprocessing import Pool
from llama_index.core.tools import BaseTool, FunctionTool


class Position:
    def __init__(self, StartLine=None, StartLinePosition=None, StopLine=None, StopLinePosition=None):
        self.StartLine = StartLine
        self.StartLinePosition = StartLinePosition
        self.StopLine = StopLine
        self.StopLinePosition = StopLinePosition

class Function:
    def __init__(self, Name=None, ReturnType=None, Parameters=None, Position=None, Content=None, Summary=None):
        self.Name = Name
        self.ReturnType = ReturnType
        self.Parameters = Parameters if Parameters is not None else []
        self.Position = Position
        self.Content = Content
        self.Summary = Summary

    

class Import:
    def __init__(self, Source=None, UsageName=None):
        self.Source = Source
        self.UsageName = UsageName if UsageName is not None else []

class Node:
    def __init__(self, NodeName=None, Type=None, FilePath=None, Module=None, Package=None, MultipleExtend=None, Imports=None, Functions=None, Position=None, Summary=None, Content=None):
        self.NodeName = NodeName
        self.Type = Type
        self.FilePath = FilePath
        self.Module = Module
        self.Package = Package
        self.MultipleExtend = MultipleExtend if MultipleExtend is not None else []
        self.Imports = Imports if Imports is not None else []
        self.Functions = Functions if Functions is not None else []
        self.Position = Position
        self.Summary = Summary
        self.Content = Content




class CodeBase:

    def __init__(self) -> None:
        self.codebase = List[Node]

    # def load_code(self,json_payload):
    #     try:
    #         code_base = json.loads(json_payload)  # This returns a list of dictionaries
    #         validated_code_base = [Node(**node) for node in code_base]  # Validate each dictionary as a Node
            
    #         func_=find_function_by_name("example_function",validated_code_base)
    #         print(f"func is {str(func_)}")
    #         summary_dict = collect_summaries_by_package_parallel(validated_code_base)
    #         print(f"Summary : {summary_dict}")

    #     except ValidationError as e:
    #         print("Validation error:", e)
    #         pass


    def generate_markdown(self,package_dict: dict) -> str:
        """
        Generates a markdown text representation of the codebase summary.

        Args:
        - package_dict (dict): A dictionary where keys are package names and values are lists of summaries.

        Returns:
        - str: A markdown text representation of the codebase summary.
        """
        markdown_output = "# Codebase Overview\n\n"
        for package_name, summaries in package_dict.items():
            markdown_output += f"## Class: {package_name}\n\n"  # Add Markdown header for each key
            combined_summary = ' '.join(summaries)  # Combine all summary elements into one string
            markdown_output += f"### Summary:\n\n**{combined_summary}**\n\n"  # Add the combined summary in bold
        return markdown_output       


    def load_json_from_file(self,file_path: str) -> List[Node]:
        """
        Load JSON data from a file and parse it into the Codebase model. Skips nodes that fail validation.

        Args:
        - file_path (str): The path to the JSON file.

        Returns:
        - List[Node]: A list of validated Node instances, excluding those with validation errors.
        """
        with open(file_path, 'r') as file:
            code_base = json.load(file)

        validated_code_base = []
        for node_data in code_base:
            try:
                # Attempt to create a Node instance from the dictionary
                validated_node = Node(**node_data)
                validated_code_base.append(validated_node)
            except ValidationError as e:
                print(f"Skipping node due to validation error: {e}")
                #print("skip node")
        
        print(f"validated nodes : {len(validated_code_base)}")
        return validated_code_base

    def collect_summaries_by_package_parallel(self,codebase: List[Node]) -> str:
        """
        Collects summaries using parallel processing and groups them by package after collection.

        Args:
        - codebase (List[Node]): A list of Node instances representing the codebase.

        Returns:
        - str: A markdown text representation of the codebase summary.
        """
        with Pool() as pool:
            results = pool.map(node_summary_collector, codebase)
        # Filter out None results
        results = [result for result in results if result is not None]
        
        
        summaries_by_package = {}
        for class_name, summary in results:
            # if package is not none
            if class_name is not None:
                if class_name not in summaries_by_package:
                    summaries_by_package[class_name] = []
                    print(f"package : {class_name}")
                summaries_by_package[class_name].append(summary)
        # output the summary per package in a structured md out
        return self.generate_markdown(summaries_by_package)
        

# Define a separate type alias for a list of Node objects
#codebase = List[Node]

# Example JSON payload
json_payload = '''
[
    {
        "NodeName": "ExampleClass",
        "Module": "example_module",
        "Type": "class",
        "Package": "example_package",
        "FilePath": "/path/to/file.py",
        "Functions": [
            {
                "Name": "example_function",
                "ReturnType": "int",
                "Parameters": [
                    {
                        "TypeValue": "int",
                        "TypeType": "primitive"
                    }
                ],
                "Position": {
                    "StartLine": 10,
                    "StartLinePosition": 1,
                    "StopLine": 15,
                    "StopLinePosition": 1
                },
                "Content": "def example_function(x): return x * 2"
            }
        ],
        "Imports": [
            {
                "Source": "sys"
            }
        ],
        "Summary" : "The ExampleClass is defined in the module example_module within the package example_package and is located at /path/to/file.py. It includes one function named example_function that returns an int and takes a single primitive integer parameter. This function is defined from line 10 to 15 in the file and its code content is def example_function(x): return x * 2. Additionally, the class imports the sys module."
    }
]
'''

#Util methods to be used as APIs
def find_function_by_name(function_name: str, codebase: List[Node]) -> Optional[Function]:
    """
    Search for a function by name across all nodes in the codebase and return the Pydantic model of the function.
    
    Args:
    - function_name (str): The name of the function to find.
    - codebase (List[Node]): The list of nodes representing the codebase.
    
    Returns:
    - Optional[Function]: The function model if found, None otherwise.
    """
    for node in codebase:
        for function in node.Functions:
            if function.Name == function_name:
                return function
    return None




def get_functions_in_class(class_name: str, codebase: List[Node]) -> List[Function]:
    """
    Retrieve all functions defined within a specified class across all nodes in the codebase.
    
    Args:
    - class_name (str): The name of the class whose functions are to be retrieved.
    - codebase (List[Node]): The list of nodes representing the codebase.
    
    Returns:
    - List[Function]: A list of Function models that are part of the specified class, or an empty list if no functions are found or the class does not exist.
    """
    for node in codebase:
        if node.NodeName == class_name and node.Type.lower() == 'class':
            return node.Functions
    return []


def find_class_by_name(class_name: str, codebase: List[Node]) -> Optional[Node]:
    """
    Search for a class by name across all nodes in the codebase and return the Pydantic model of the class.
    
    Args:
    - class_name (str): The name of the class to find.
    - codebase (List[Node]): The list of nodes representing the codebase.
    
    Returns:
    - Optional[Node]: The node model if found, None otherwise.
    """
    for node in codebase:
        if node.NodeName == class_name and node.Type.lower() == 'class':
            return node
    return None



def find_classes_in_package(package_name: str, codebase: List[Node]) -> List[Node]:
    """
    Search for all classes within a specified package across all nodes in the codebase and return a list of Pydantic models of these classes.
    
    Args:
    - package_name (str): The name of the package to search within.
    - codebase (List[Node]): The list of nodes representing the codebase.
    
    Returns:
    - List[Node]: A list of node models representing classes within the specified package, or an empty list if no classes are found.
    """
    class_nodes = []
    for node in codebase:
        if node.Type.lower() == 'class' and node.Package == package_name:
            class_nodes.append(node)
    return class_nodes



def find_classes_in_module(module_name: str, codebase: List[Node]) -> List[Node]:
    """
    Search for all classes within a specified module across all nodes in the codebase and return a list of Pydantic models of these classes.
    
    Args:
    - module_name (str): The name of the module to search within.
    - codebase (List[Node]): The list of nodes representing the codebase.
    
    Returns:
    - List[Node]: A list of node models representing classes within the specified module, or an empty list if no classes are found.
    """
    class_nodes = []
    for node in codebase:
        if node.Type.lower() == 'class' and node.Module == module_name:
            class_nodes.append(node)
    return class_nodes


def node_summary_collector(node) -> Tuple[str, str]:
    """
    Helper function that processes a single node and returns a tuple of its package and summary.
    """
    # todo check if node's type is CLASS then only return the summary else return none
    # check if node type exists first
    if node.Type is not None:
        if node.Type.lower() == 'class':
            return (node.NodeName, node.Summary)
        else:
            return (None, None)


if __name__ == "__main__":
    repo_base = CodeBase()
    #repo_base.load_code(json_payload)
    validated_nodes = repo_base.load_json_from_file('1_codes.json')
    md_content_repo = repo_base.collect_summaries_by_package_parallel(validated_nodes) 
    #output summaries to file with json 
    with open('codebase_overview.md', 'w', encoding='utf-8') as md_file:
         md_file.write(md_content_repo)

    print("Markdown file created: codebase_overview.md")
    # create agent using llama index of type reAct and intialise tasks
    # llm = Ollama(model="llama3:8b-instruct-fp16",request_timeout=30)
    # summary_tool = FunctionTool.from_defaults(fn=repo_base.collect_summaries_by_package_parallel)

    # tools = [summary_tool]
    # agent = ReActAgent.from_tools(llm=llm, tools=tools, verbose=True)
    # agent.chat("Hi")

    
