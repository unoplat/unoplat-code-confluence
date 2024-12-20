from neomodel import StructuredNode, StringProperty, Relationship, ZeroOrMore, JSONProperty

from unoplat_code_confluence_commons.graph_models.base_models import AnnotatedRelationship


class ConfluenceAnnotation(StructuredNode):
    name = StringProperty(required=True)
    key_values = JSONProperty()
    # Relationships
    annotated_classes = Relationship('.confluence_class.ConfluenceClass', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
    annotated_methods = Relationship('.confluence_internal_method.ConfluenceInternalMethod', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
