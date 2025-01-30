from enum import Enum, auto


class ConfluenceUserIntent(str, Enum):
    CODE_SUMMARIZATION = auto()
    PACKAGE_OVERVIEW = auto()
    CLASS_DETAILS = auto()
    FUNCTIONAL_IMPLEMENTATION = auto()

