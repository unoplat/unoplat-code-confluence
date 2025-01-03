from neomodel import (
    StructuredNode,
    StringProperty,
    JSONProperty,
    UniqueIdProperty,
    RelationshipTo,
    ZeroOrMore
)

from unoplat_code_confluence_commons.graph_models.base_models import AnnotatedRelationship

class CodeConfluenceAnnotation(StructuredNode):
    """
    Represents an annotation node based on ChapiAnnotation.
    """
    name = StringProperty()      # Name
    # key_values can be stored as JSON if you don’t need them as separate nodes
    key_values = JSONProperty()      # KeyValues (list[ChapiAnnotationKeyVal])
    annotated_classes = RelationshipTo('.code_confluence_class.CodeConfluenceClass', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
    annotated_functions = RelationshipTo('.code_confluence_internal_function.CodeConfluenceInternalFunction', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)