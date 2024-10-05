from enum import Enum

class ConfluenceUserIntent(Enum):
    CODE_SUMMARIZATION = "User wants an overview or summary of the codebase."
    CODE_FEATURE = "User is looking for specific features that can be answered by going through the package summaries."
    FUNCTIONAL_IMPLEMENTATION = "User wants detailed understanding at the function level."

