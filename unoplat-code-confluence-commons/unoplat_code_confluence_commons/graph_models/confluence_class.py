from unoplat_code_confluence_commons.graph_models.base_models import BaseNode, ContainsRelationship, AnnotatedRelationship
from neomodel import  RelationshipTo, StringProperty,ZeroOrMore,One,ArrayProperty,FloatProperty,JSONProperty,Relationship

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
    imports = Relationship('.confluence_import.ConfluenceImport', 'IMPORTS', cardinality=ZeroOrMore)
    annotations = Relationship('.confluence_annotation.ConfluenceAnnotation', 'HAS_ANNOTATION', model=AnnotatedRelationship, cardinality=ZeroOrMore)
    fields = RelationshipTo('.confluence_class_field.ConfluenceClassField', 'CONTAINS', model=ContainsRelationship, cardinality=ZeroOrMore)
