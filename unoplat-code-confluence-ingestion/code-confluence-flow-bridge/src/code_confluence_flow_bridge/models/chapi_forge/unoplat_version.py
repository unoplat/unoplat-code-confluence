# # Standard Library
# from typing import Optional
# 
# # Third Party
# from pydantic import BaseModel, Field
# 
# 
# class UnoplatVersion(BaseModel):
#     specifier: Optional[str] = Field(default=None, description="The specifier of the version")
#     minimum_version: Optional[str] = Field(default=None, description="The minimum version of the project")
#     maximum_version: Optional[str] = Field(default=None, description="The maximum version of the project")
#     current_version: Optional[str] = Field(default=None, description="The current version of the project")
