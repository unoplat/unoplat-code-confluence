# Standard Library
from typing import Optional

# Third Party
from pydantic import Field

# First Party
from unoplat_code_confluence.data_models.chapi.chapi_function import ChapiFunction


class UnoplatChapiForgeFunction(ChapiFunction):
    qualified_name: str = Field(alias="QualifiedName", description="The qualified name of the function")
    comments_description: Optional[str] = Field(default=None, alias="CommentsDescription", description="description of the function from comments")
    

    