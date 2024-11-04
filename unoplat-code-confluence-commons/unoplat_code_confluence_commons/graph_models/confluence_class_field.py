from neomodel import StructuredNode, StringProperty, RelationshipTo, ZeroOrMore

class ConfluenceClassField(StructuredNode):
    field_type = StringProperty()
    field_name = StringProperty()
    annotations = RelationshipTo('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', cardinality=ZeroOrMore)