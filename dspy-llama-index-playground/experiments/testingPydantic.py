from pydantic import BaseModel, ValidationError, validator
from typing import Optional

class Position(BaseModel):
    StartLine: int = None
    StopLine: Optional[int] = None

class Node(BaseModel):
    Position: Optional[Position] 

    # @validator('Position', pre=True, always=True)
    # def check_position(cls, v):
    #     # Add custom logic if needed
    #     return v

# Test the model with different inputs
try:
    node = Node(Position={'StartLine': 10, 'StopLine': 20})
    print(node)
except ValidationError as e:
    print(e)

try:
    node = Node(Position={'StartLine': 10})
    print(node)
except ValidationError as e:
    print(e)


try:
    node = Node(Position=None)
    print(node)
except ValidationError as e:
    print(e)