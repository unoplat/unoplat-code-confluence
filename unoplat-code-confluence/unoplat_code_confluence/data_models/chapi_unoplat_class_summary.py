

from typing import Optional
from pydantic import BaseModel, Field

class ClassSummary(BaseModel):
    objective: Optional[str] = Field(default=None, alias="Objective",description="This should include high level objective of what function does based on function content and function metadata. It should capture function implementation and internal and external calls made inside the function in a concise manner. Should not be more than 3 lines.")
    summary: Optional[str] = Field(default=None, alias="Summary",description="This should capture what the class is doing using its fields inside functions across functions capturing events happening inside the class. It should make sure that all internal and external interactions happening in the class are captured well. Should be very concise but also very precise and accurate.")
    
    