from abc import ABC
from data_models.chapi_unoplat_node import Node
from nodeparser.isummariser import ISummariser
from litellm import completion
from loguru import logger

class NodeSummariser(ISummariser):    
    def summarise_node(self, node: Node) -> Node:
        """
        Uses LiteLLM to generate a summary for the provided Node object.
        
        Args:
            node (Node): The node to summarise.
        
        Returns:
            Node: The node with updated summary.
        """
        logger.debug(self._create_summary_prompt(node))
        try:
            response = completion(
                model="ollama_chat/mistral:7b-instruct-fp16",
                messages=[
                    {"content": "User will be sharing class metadata in json. Understand the json first. Then understand the placeholder markdown specification shared by user. Fill the placeholders in the markdown spec based on the json. Strictly respond in markdown only."
                     ,"role": "system"},
                     {"content": 
                      f"""{node.model_dump(mode='json')} + "\n\n" + {self._create_summary_prompt(node)} """
                      , "role": "user"},
                ],
                temperature=0
            )
            node.summary = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            print(f"Error during summarization: {e}")
            node.summary = "Summarization failed."
        return node

    def _create_summary_prompt(self, node: Node) -> str:
        """
        Creates a prompt for the LLM to understand and convert the node information into a structured summary.
        
        Args:
            node (Node): The node to create a prompt for.
        
        Returns:
            str: A prompt string.
        """
        
        prompt = f"# Class Summary: [{node.node_name}]\n\n"
        prompt += f"- **Package**: `{node.package}`\n"
        prompt += f"- **File Path**: `{node.file_path}`\n"
        prompt += "- **Responsibility**: `Fill in Brief description of what the class does`\n\n"
        prompt += "## Fields\n"
        for field in node.fields:
            prompt += f"- **{field.type_type}**: `{field.type_value}`\n"
            prompt += "  - **Type**: `Fill in Description of the field, including any dependency injections if applicable`\n\n"
        prompt += "## Methods\n"
        for function in node.functions:
            internal_calls_str = ""
            external_calls_str = ""
            for call in function.function_calls:
                call_description = f"`{call.function_name}()` to `Fill in description of what the call is for. Focus on call interactions within the class and outside the class using fields`"
                if call.node_name == node.node_name:  # Internal call
                    internal_calls_str += f"    - {call_description}\n"
                else:  # External call
                    external_calls_str += f"    - `{call.node_name}.{call_description}\n"
            prompt += f"- **{function.name}()**: `{function.return_type}`\n"
            prompt += "  - **Summary**: `Fill in Brief description of what the method does`\n"
            if internal_calls_str:
                prompt += "  - **Internal Calls**:\n" + internal_calls_str
            if external_calls_str:
                prompt += "  - **External Calls**:\n" + external_calls_str
            prompt += "Please use the placeholders provided to structure the response accurately. Strictly Do not deviate from the markdown format else no tip will be offered."        
        return prompt

