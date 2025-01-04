from neomodel import (
    StringProperty,
    IntegerProperty,
    JSONProperty,
    UniqueIdProperty,
    AsyncRelationshipTo,
    AsyncRelationshipFrom,
    AsyncRelationship,
    AsyncZeroOrMore,
    AsyncOne
)
from .base_models import AnnotatedRelationship, BaseNode,ContainsRelationship
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
    annotations = AsyncRelationship(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=AnnotatedRelationship,cardinality=AsyncZeroOrMore)
    
    confluence_class = AsyncRelationshipTo(".code_confluence_class.CodeConfluenceClass", "PART_OF_CLASS",model=ContainsRelationship,cardinality=AsyncOne)
