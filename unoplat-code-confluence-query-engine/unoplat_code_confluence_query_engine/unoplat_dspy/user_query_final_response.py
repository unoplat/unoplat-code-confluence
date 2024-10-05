from typing import Dict
import dspy



class CodeConfluenceUserQueryResponseSignature(dspy.Signature):
    """Generate a comprehensive response to the user query using the code metadata."""
    user_query: str = dspy.InputField(desc="The user's original query.")
    code_metadata: str = dspy.InputField(desc="The code metadata relevant to the user query.")
    existing_respone : str = dspy.InputField(default="No existing response yet",desc="The existing response to the user query based on multiple code metadata. It will be empty in the first instance or if there is just one relevant code metadata for user query")
    final_response: str = dspy.OutputField(desc="final response based on user_query , code metadata and existing_response if it exists")

class CodeConfluenceUserQueryResponseModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.response_module = dspy.ChainOfThought(CodeConfluenceUserQueryResponseSignature)

    def forward(self, user_query: str, code_metadata: Dict[str,str]):
        final_response = ""
        for name in code_metadata.keys():
            if final_response is None:
                final_response = self.response_module(user_query=user_query, code_metadata=code_metadata[name],existing_respone="No existing response yet").final_response
            else:
                final_response = self.response_module(user_query=user_query, code_metadata=code_metadata[name], existing_respone=final_response).final_response

        return dspy.Prediction(answer=final_response)
