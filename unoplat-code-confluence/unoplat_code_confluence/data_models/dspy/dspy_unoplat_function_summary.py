# Standard Library
from typing import List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_function import \
    ChapiUnoplatFunction


class DspyUnoplatFunctionSummary(ChapiUnoplatFunction):
    qualified_name: str = Field(required=True, alias="QualifiedName",description="The qualified name of the function that contains the entire hierarchy of the class")
    objective: Optional[str] = Field(default=None, alias="Objective",description="This should include high level objective of what function does based on function content and function metadata. Should not be more than 3 lines.")
    implementation_summary: Optional[str] = Field(default=None, alias="ImplementationSummary",description="This should include implementation details of the function. make sure if this function makes internal calls to other functions of same class and to external calls to other classes/libs is also covered. Use all metadata shared for the function to answer .")
    function_objective_embedding: List[float] = Field(default_factory=list, alias="FunctionObjectiveEmbedding")
    function_implementation_summary_embedding: List[float] = Field(default_factory=list, alias="FunctionImplementationSummaryEmbedding")
    
