from neomodel import StructuredNode, StringProperty, RelationshipTo, ZeroOrMore

from unoplat_code_confluence_commons.graph_models.base_models import AnnotatedRelationship


class ConfluenceClassField(StructuredNode):
    field_type = StringProperty()
    field_name = StringProperty()
    annotations = RelationshipTo('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
