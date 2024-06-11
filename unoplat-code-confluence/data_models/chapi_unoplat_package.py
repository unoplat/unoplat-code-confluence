from typing import List, Optional
from pydantic import BaseModel, Field

from data_models.chapi_unoplat_node import Node


class UnoplatPackage(BaseModel):
    package: Optional[str] = Field(default=None, alias="Package")
    summary: Optional[str] = Field(default=None, alias="Summary")
    nodes: List[Node] = Field(default_factory=list)
    