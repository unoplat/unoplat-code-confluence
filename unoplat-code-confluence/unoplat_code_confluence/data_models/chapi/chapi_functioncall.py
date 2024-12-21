


# Standard Library
# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_parameter import ChapiParameter
from unoplat_code_confluence.data_models.chapi.chapi_position import Position


class ChapiFunctionCall(BaseModel):
    """
    FunctionCall is a data model for a function call being made in a function.
    """
    package: Optional[str] = Field(default=None, alias="Package",description="package name of the function call")
    type: Optional[str] = Field(default=None, alias="Type",description="type of the function call")
    node_name: Optional[str] = Field(default=None, alias="NodeName",description="name of the class being called")
    function_name: Optional[str] = Field(default=None, alias="FunctionName",description="name of the function being called")
    parameters: List[ChapiParameter] = Field(default_factory=list, alias="Parameters",description="parameters of the function call")
    position: Optional[Position] = Field(default=None, alias="Position",exclude=True,description="position of the function call in the code")
 