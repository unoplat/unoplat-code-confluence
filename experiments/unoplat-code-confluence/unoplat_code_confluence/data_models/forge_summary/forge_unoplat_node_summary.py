# Standard Library
from typing import List, Optional

# Third Party
from pydantic import Field

# First Party
from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_node import UnoplatChapiForgeNode
from unoplat_code_confluence.data_models.forge_summary.forge_unoplat_function_summary import DspyUnoplatFunctionSummary


class DspyUnoplatNodeSummary(UnoplatChapiForgeNode):
    node_summary: str = Field(alias="NodeSummary",description="A summary of the class")
    node_objective: str = Field(alias="NodeObjective",description="The objective of the class")
    functions_summary: Optional[List[DspyUnoplatFunctionSummary]] = Field(default=None, alias="FunctionsSummary",description="A list of functions in the class")
    class_objective_embedding: List[float] = Field(default_factory=list, alias="ClassObjectiveEmbedding")
    class_implementation_summary_embedding: List[float] = Field(default_factory=list, alias="ClassImplementationSummaryEmbedding")
    
    