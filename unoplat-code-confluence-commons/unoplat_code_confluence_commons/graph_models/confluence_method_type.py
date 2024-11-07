from pydantic import BaseModel
from typing import ClassVar, Dict

class MethodTypeChoices(BaseModel):
    """Defines method type choices for use in Neomodel properties."""
    
    EXTERNAL: ClassVar[str] = 'external'
    UTILITY: ClassVar[str] = 'utility'
    
    choices: ClassVar[Dict[str, str]] = {
        EXTERNAL: 'External',
        UTILITY: 'Programming Language Utility'
    }