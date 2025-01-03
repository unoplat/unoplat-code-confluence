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
from .base_models import BaseNode,ContainsRelationship
class CodeConfluenceInternalFunction(BaseNode):
    """
    Represents a function-like node, combining fields from:
      - ChapiFunction
      - UnoplatChapiForgeFunction
    """
    # From ChapiFunction
    name = StringProperty()              # Name
    return_type = StringProperty()       # ReturnType
    # function_calls, parameters, local_variables can be stored as JSON
    function_calls = JSONProperty(default=[])          # FunctionCalls
    parameters = JSONProperty(default=[])              # Parameters
    position = JSONProperty()            # Position
    body_hash = IntegerProperty()        # BodyHash
    content = StringProperty()           # Content
    comments_description = StringProperty() # CommentsDescription

    # RELATIONSHIPS
    annotations = RelationshipTo(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    confluence_class = RelationshipFrom(".code_confluence_class.CodeConfluenceClass", "PART_OF_CLASS",model=ContainsRelationship,cardinality=One)
