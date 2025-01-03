from neomodel import (
    StructuredNode,
    StringProperty,
    IntegerProperty,
    JSONProperty,
    UniqueIdProperty,
    RelationshipTo,
    RelationshipFrom,
    ZeroOrMore,
    One
)
from unoplat_code_confluence_commons.graph_models.base_models import BaseNode,ContainsRelationship
class CodeConfluenceInternalFunction(BaseNode):
    """
    Represents a function-like node, combining fields from:
      - ChapiFunction
      - UnoplatChapiForgeFunction
    """
    # From ChapiFunction
    name = StringProperty(required=False)              # Name
    return_type = StringProperty(required=False)       # ReturnType
    # function_calls, parameters, local_variables can be stored as JSON
    function_calls = JSONProperty(default=[])          # FunctionCalls
    parameters = JSONProperty(default=[])              # Parameters
    position = JSONProperty(required=False)            # Position
    body_hash = IntegerProperty(required=False)        # BodyHash
    content = StringProperty(required=False)           # Content
    comments_description = StringProperty(required=False) # CommentsDescription

    # RELATIONSHIPS
    annotations = RelationshipTo(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    confluence_class = RelationshipFrom(".code_confluence_class.CodeConfluenceClass", "PART_OF_CLASS",model=ContainsRelationship,cardinality=One)
