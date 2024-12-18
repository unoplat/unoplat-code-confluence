from unoplat_code_confluence.data_models.chapi.chapi_node import ChapiNode

from unoplat_code_confluence.data_models.chapi_forge.unoplat_chapi_forge_function import UnoplatChapiForgeFunction
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import import UnoplatImport
from unoplat_code_confluence.data_models.chapi_forge.unoplat_import_type import ImportType
from pydantic import Field
from typing import Any, Optional, Dict, List

class UnoplatChapiForgeNode(ChapiNode):
    
    qualified_name: str = Field(default=None, alias="QualifiedName",exclude=True,description="name of class with absolute path")
    comments_description: Optional[str] = Field(default=None, alias="CommentsDescription",description="description of the node from comments")
    segregated_imports: Optional[Dict[ImportType,List[UnoplatImport]]] = Field(default=None,alias="SegregatedImports", description="SegregatedImports in terms of internal ,external ,standard and local libraries")
    dependent_internal_classes: Optional[List['UnoplatChapiForgeNode']] = Field(default_factory=list,alias="DependentInternalClasses",description="list of classes that this node is dependent on")
    functions: Optional[List[UnoplatChapiForgeFunction]] = Field(default_factory=list,alias="Functions",description="functions of the node") #type: ignore
    
    
    @classmethod 
    def from_chapi_node(cls, chapi_node: ChapiNode, **additional_fields):
        chapi_node_data: dict[str,Any] = chapi_node.model_dump(by_alias=True)
        
        # Check for qualified_name (assuming this is required)
        if "qualified_name" in additional_fields and additional_fields["qualified_name"]:
            chapi_node_data.update({"QualifiedName": additional_fields["qualified_name"]})
        
        # More thorough checking for segregated_imports
        if "segregated_imports" in additional_fields and additional_fields["segregated_imports"] is not None:
            chapi_node_data.update({"SegregatedImports": additional_fields["segregated_imports"]})
        
        # Check functions if they exist
        if chapi_node_data.get("Functions"):  # Using .get() is safer than direct access
            for function in chapi_node_data["Functions"]:
                func_qualified_name = f"{additional_fields['qualified_name']}.{function['Name']}"
                function["QualifiedName"] = func_qualified_name
        
        # Create new child instance with combined data
        return cls.model_validate(chapi_node_data)
        
        
UnoplatChapiForgeNode.model_rebuild()     