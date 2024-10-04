import dspy 
from typing import Dict
from textual import log

class CodeConfluenceUserQueryReRankSignature(dspy.Signature):
    """Based on user query and possible answers, return the most relevant names as a dict with score as value and key as name based on the description matching with user query"""
    user_query: str = dspy.InputField(desc="This will contain user query")
    possible_answers: Dict[str,str] = dspy.InputField(desc="this will contain list of possibly relevant answers with name and their description ")
    relevant_answers: Dict[str,int] = dspy.OutputField(default_factory=dict,desc="return  the most relevant names from the list based on the descriptions matching with user query with score from 1 to 10 with 10 being the highest match ")
   
class CodeConfluenceUserQueryReRankModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.rerank_module = dspy.ChainOfThought(CodeConfluenceUserQueryReRankSignature)

    def forward(self, user_query: str, possible_answers: Dict[str,str]):
        rerank_answers = self.rerank_module(user_query=user_query,possible_answers=possible_answers)
        return dspy.Prediction(answer=rerank_answers)