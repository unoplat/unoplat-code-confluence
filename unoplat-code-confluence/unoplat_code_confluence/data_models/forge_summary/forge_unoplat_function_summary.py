# Standard Library
from typing import List, Optional

# Third Party
from pydantic import Field
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction

# First Party



class DspyUnoplatFunctionSummary(UnoplatChapiForgeFunction):
    objective: Optional[str] = Field(default=None, alias="Objective",description="This should include high level objective of what function does based on function content and function metadata. Should not be more than 3 lines.")
    implementation_summary: Optional[str] = Field(default=None, alias="ImplementationSummary",description="This should include implementation details of the function. make sure if this function makes internal calls to other functions of same class and to external calls to other classes/libs is also covered. Use all metadata shared for the function to answer .")
    function_objective_embedding: List[float] = Field(default_factory=list, alias="FunctionObjectiveEmbedding")
    function_implementation_summary_embedding: List[float] = Field(default_factory=list, alias="FunctionImplementationSummaryEmbedding")
    
