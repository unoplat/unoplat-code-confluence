from enum import Enum


class ImportType(str,Enum):
    INTERNAL = "internal"  # For imports within the same project/codebase
    EXTERNAL = "external"  # For third-party package imports
    SYSTEM = "system"
    
