from typing import List, Dict
import dspy
from textual import log
from unoplat_code_confluence_query_engine.models.confluence_user_intent import ConfluenceUserIntent


class IntentDescriptions:
    DESCRIPTIONS: Dict[ConfluenceUserIntent, str] = {
        ConfluenceUserIntent.CODE_SUMMARIZATION: "The user query wants a high-level overview or summary of the entire codebase, including its main objectives and overall implementation.",
        ConfluenceUserIntent.PACKAGE_OVERVIEW: "The user query is interested in understanding the objectives or summaries of specific packages within the codebase.",
        ConfluenceUserIntent.CLASS_DETAILS: "The user query seeks detailed information about specific classes, including their purposes and how they fit within the packages.",
        ConfluenceUserIntent.FUNCTIONAL_IMPLEMENTATION: "The user query wants detailed understanding at the function level."
    }

class CodeConfluenceUserQuerySignature(dspy.Signature):
    """Based on user query and context of intents, return the user_intent_result."""
    user_query: str = dspy.InputField(desc="This will contain user query", default=None, alias="UserQuery")
    intent_descriptions: Dict[ConfluenceUserIntent, str] = dspy.InputField(desc="This will contain intents and their respective descriptions", default=None, alias="IntentDescriptions")
    user_intent_result: List[int] = dspy.OutputField(desc="This will strictly return list of confluent user intent enum values", alias="UserIntentResult")

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
