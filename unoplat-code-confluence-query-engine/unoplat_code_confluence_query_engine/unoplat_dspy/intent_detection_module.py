from typing import List, Dict
import dspy
from textual import log

class IntentDescriptions:
    DESCRIPTIONS: Dict[str, str] = {
        "CODE_SUMMARIZATION": "User wants an overview or summary of the codebase.",
        "CODE_FEATURE": "User is looking for specific features that can be answered by going through the package summaries.",
        "FUNCTIONAL_IMPLEMENTATION": "User wants detailed understanding at the function level."
    }

class CodeConfluenceUserQuerySignature(dspy.Signature):
    """Based on user query and context of intents, return the user_intent_result."""
    user_query: str = dspy.InputField(desc="This will contain user query", default=None, alias="UserQuery")
    intent_descriptions: Dict[str, str] = dspy.InputField(desc="This will contain intents and their respective descriptions", default=None, alias="IntentDescriptions")
    user_intent_result: List[str] = dspy.OutputField(desc="This will strictly return list of items from intents", alias="UserIntentResult")

class CodeConfluenceIntentDetectionModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.intent_detection = dspy.ChainOfThought(CodeConfluenceUserQuerySignature)

    def forward(self, user_query: str) -> dspy.Prediction:
        intent_detection = self.intent_detection(
            user_query=user_query,
            intent_descriptions=IntentDescriptions.DESCRIPTIONS
        )
        log.debug(f"Intent detection result: {intent_detection.user_intent_result}")
        return dspy.Prediction(answer=intent_detection.user_intent_result)
