from data_models.chapi_unoplat_position import Position
from pydantic import BaseModel, Field
from typing import Optional


class Annotation(BaseModel):
    name: Optional[str] = Field(default=None, alias="Name")
    position: Optional[Position] = Field(default=None, alias="Position")
