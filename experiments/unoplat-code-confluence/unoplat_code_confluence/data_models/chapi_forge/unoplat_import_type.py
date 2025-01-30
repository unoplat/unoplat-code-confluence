# Standard Library
from enum import Enum


#TODO: This will change when we move to ruff
class ImportType(Enum):
    INTERNAL = "INTERNAL"  # First party imports
    EXTERNAL = "EXTERNAL"  # Third party imports
    STANDARD = "STANDARD"  # Standard library imports
    LOCAL = "LOCAL"
    
