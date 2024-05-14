import marko

def dict_to_markdown(classes):
    """Convert a dictionary to a Markdown formatted string."""
    markdown_output = ""
    for key, content in classes.items():
        markdown_output += f"## {key}\n"  # Add Markdown header for each key
        for item in content:
            markdown_output += f"{item}\n\n"  # Add each item in the content list with spacing for readability
    return markdown_output

# Dictionary of classes and their summaries
classes = {
    'ToolFactory': [
        'This code is a Python class `ToolFactory` that provides methods for creating and generating OpenAPI schemas from various sources.',
        'Here’s a breakdown of the methods:',
        '1. `from_olangchain_tools(tools: List[Id])`: This method takes a list of tool IDs as input and extracts the description, parameters, and schema from an OpenAPI specification. It then creates a new function with these details and appends it to the `tools` list.',
        '2. `from_file(file_path: str) -> Type[BaseTool]`: This method dynamically imports a BaseTool class from a Python file within a package structure. The `file_path` parameter specifies the path to the Python file. If the import is successful, it checks if the imported class is a subclass of `BaseTool` and returns it.',
        '3. `get_openapi_schema(tools: List[Type[BaseTool]], url: str, title="Agent Tools", description="A collection of tools.") -> str`: This method generates an OpenAPI schema from a list of BaseTools. It creates a base OpenAPI schema with the specified title and description, then iterates over each tool in the list, adding its details to the schema as separate endpoints.'
    ],
    'UserDetail': [
        'Here is a summary of the class in 2 lines:',
        'The `UserDetail` class represents a user\'s details, including their unique identifier (`id`), age, name, and a list of friend IDs. The `friends` field is described as a correct and complete list of friend IDs representing relationships between users.'
    ],
    'JSON Module': [
        'Imported the `json` module, which provides functionality for encoding and decoding JSON data in Python.',
        'The `json` module allows for easy conversion between JSON (JavaScript Object Notation) data structures and Python data structures such as dictionaries and lists. It provides functions to serialize (encode) and deserialize (decode) JSON data.'
    ]
}

# Convert the dictionary to markdown
markdown_text = dict_to_markdown(classes)
print(markdown_text)
