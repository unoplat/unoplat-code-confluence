# # Standard Library
# # First Party
# from src.code_confluence_flow_bridge.models.chapi.chapi_annotation_key_val import ChapiAnnotationKeyVal
# from src.code_confluence_flow_bridge.models.chapi.chapi_position import Position

# from typing import Optional

# # Third Party
# from pydantic import BaseModel, Field


# class ChapiAnnotation(BaseModel):
#     name: Optional[str] = Field(default=None, alias="Name")
#     key_values: Optional[list[ChapiAnnotationKeyVal]] = Field(default_factory=list, alias="KeyValues")
#     position: Optional[Position] = Field(default=None, alias="Position")
