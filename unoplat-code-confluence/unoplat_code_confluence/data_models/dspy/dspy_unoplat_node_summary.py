# Standard Library
from typing import Any, Dict, List, Optional

# Third Party
from pydantic import BaseModel, Field

# First Party
from unoplat_code_confluence.data_models.chapi_unoplat_class_fieldmodel import \
    ClassFieldModel
from unoplat_code_confluence.data_models.chapi_unoplat_node import \
    ChapiUnoplatNode
from unoplat_code_confluence.data_models.dspy.dspy_unoplat_function_summary import \
    DspyUnoplatFunctionSummary


class DspyUnoplatNodeSummary(ChapiUnoplatNode):
    qualified_name: str = Field(required=True, alias="QualifiedName",description="The qualified name of the class that contains the entire hierarchy of the class")
    node_summary: str = Field(required=True, alias="NodeSummary",description="A summary of the class")
    node_objective: str = Field(required=True, alias="NodeObjective",description="The objective of the class")
    functions_summary: Optional[List[DspyUnoplatFunctionSummary]] = Field(default=None, alias="FunctionsSummary",description="A list of functions in the class")
    class_objective_embedding: List[float] = Field(default_factory=list, alias="ClassObjectiveEmbedding")
    class_implementation_summary_embedding: List[float] = Field(default_factory=list, alias="ClassImplementationSummaryEmbedding")
    
    
