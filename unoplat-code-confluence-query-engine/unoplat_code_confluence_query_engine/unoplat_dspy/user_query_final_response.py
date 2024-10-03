from typing import Dict
import dspy
from models.confluence_func_hiearchy import CodeConfluenceFunctionHiearchySub


class CodeConfluenceUserQueryResponseSignature(dspy.Signature):
    """Generate a comprehensive response to the user query using the code hierarchy data."""
    user_query: str = dspy.InputField(desc="The user's original query.")
    code_hierarchy: CodeConfluenceFunctionHiearchySub = dspy.InputField(desc="The code hierarchy data relevant to the user query.")
    existing_respone : str = dspy.InputField(default="No existing response yet",desc="The existing response to the user query based on multiple code hiearchy. It will be empty in the first instance or if there is just one relevant code hiearchy for user query")
    final_response: str = dspy.OutputField(desc="final response based on user_query , code_hierarchy and existing_response if it exists")

class CodeConfluenceUserQueryResponseModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.response_module = dspy.ChainOfThought(CodeConfluenceUserQueryResponseSignature)

    def forward(self, user_query: str, code_hierarchy_dict: Dict[str,CodeConfluenceFunctionHiearchySub]):
        final_response = ""
        for function_name in code_hierarchy_dict.keys():
            if final_response is None:
                final_response = self.response_module(user_query=user_query, code_hierarchy=code_hierarchy_dict[function_name],existing_respone="No existing response yet").final_response
            else:
                final_response = self.response_module(user_query=user_query, code_hierarchy=code_hierarchy_dict[function_name], existing_respone=final_response).final_response
        return dspy.Prediction(answer=final_response)
