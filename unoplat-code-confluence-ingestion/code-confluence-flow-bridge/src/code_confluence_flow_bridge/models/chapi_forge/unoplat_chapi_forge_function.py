# # Standard Library
# # First Party
# from src.code_confluence_flow_bridge.models.chapi.chapi_function import ChapiFunction
# 
# from typing import Optional
# 
# # Third Party
# from pydantic import Field
# 
# 
# class UnoplatChapiForgeFunction(ChapiFunction):
#     qualified_name: str = Field(alias="QualifiedName", description="The qualified name of the function")
#     comments_description: Optional[str] = Field(default=None, alias="CommentsDescription", description="description of the function from comments")
#     parent_function_name: Optional[str] = Field(default=None, alias="ParentFunctionName", description="The name of the parent function if the function is nested")
