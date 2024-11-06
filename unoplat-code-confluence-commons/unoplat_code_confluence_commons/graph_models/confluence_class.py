from .base_models import BaseNode, ContainsRelationship
from neomodel import RelationshipFrom, RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,VectorIndex,FloatProperty,JSONProperty

class ConfluenceClass(BaseNode):
    """Represents a class in a package"""
    class_name = StringProperty(required=True)
    implementation_summary = StringProperty(default="")
    objective = StringProperty(default="")
    class_objective_embedding = ArrayProperty(FloatProperty())
    class_implementation_summary_embedding = ArrayProperty(FloatProperty())
    node_type = StringProperty()
    file_path = StringProperty()
    module = StringProperty()
    extend = StringProperty()
    multiple_extend = ArrayProperty(StringProperty())
    position = JSONProperty()
    content = StringProperty()
    # Class relationships
    package = RelationshipTo('.confluence_package.ConfluencePackage', 'BELONGS_TO', model=ContainsRelationship, cardinality=One)
    methods = RelationshipTo('.confluence_internal_method.ConfluenceInternalMethod', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
    extends = RelationshipTo('.confluence_class.ConfluenceClass', 'EXTENDS', cardinality=ZeroOrMore)
    imports = RelationshipTo('.confluence_import.ConfluenceImport', 'IMPORTS', cardinality=ZeroOrMore)
    annotations = RelationshipTo('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', cardinality=ZeroOrMore)
    fields = RelationshipTo('.confluence_class_field.ConfluenceClassField', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)