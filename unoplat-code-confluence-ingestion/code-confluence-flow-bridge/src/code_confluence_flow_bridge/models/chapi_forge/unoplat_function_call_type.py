# Standard Library
from enum import Enum


class FunctionCallType(Enum):
    SAME_FILE = "SAME_FILE"  # Function calls to functions/methods within the same file
    INTERNAL_CODEBASE = "INTERNAL_CODEBASE"  # Function calls to functions/methods in other files within the same codebase
    EXTERNAL = "EXTERNAL"  # Function calls to external libraries
    UNKNOWN = "UNKNOWN"  # Function calls where the type couldn't be determined 