from neomodel import (
    AsyncStructuredNode,
    StringProperty,
    AsyncRelationship,
    AsyncZeroOrMore
)

from unoplat_code_confluence_commons.graph_models.base_models import AnnotatedRelationship

class CodeConfluenceAnnotation(AsyncStructuredNode):
    """
    Represents an annotation node based on ChapiAnnotation.
    """
    name = StringProperty(required=True,unique_index=True)      # Name
    # key_values can be stored as JSON if you don’t need them as separate nodes
    annotated_classes = AsyncRelationship('.code_confluence_class.CodeConfluenceClass', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=AsyncZeroOrMore)
    annotated_functions = AsyncRelationship('.code_confluence_internal_function.CodeConfluenceInternalFunction', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=AsyncZeroOrMore)