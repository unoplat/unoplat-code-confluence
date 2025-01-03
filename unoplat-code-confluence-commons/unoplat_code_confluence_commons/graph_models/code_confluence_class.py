from neomodel import (
    StructuredNode,
    StringProperty,
    ArrayProperty,
    JSONProperty,
    RelationshipTo,
    RelationshipFrom,
    ZeroOrMore,
    One
)

from unoplat_code_confluence_commons.graph_models.base_models import ContainsRelationship

class CodeConfluenceClass(StructuredNode):
    """
    Represents a class-like node, combining fields from:
      - ChapiNode
      - UnoplatChapiForgeNode
    """
    # From ChapiNode
    node_name = StringProperty(required=False)       # NodeName
    type_ = StringProperty(required=False)           # Type (renamed to avoid Python 'type' shadowing)
    file_path = StringProperty(required=False)       # FilePath
    module = StringProperty(required=False)          # Module
    multiple_extend = ArrayProperty(StringProperty(), default=[])  # MultipleExtend
    fields = JSONProperty(default=[])                # Fields (list of ClassGlobalFieldModel)
    extend = StringProperty(required=False)          # Extend
    position = JSONProperty(required=False)          # Position
    content = StringProperty(required=False)         # Content

    # From UnoplatChapiForgeNode
    qualified_name = StringProperty(required=True,unique_index=True)  # QualifiedName
    comments_description = StringProperty(required=False)  # CommentsDescription
    segregated_imports = JSONProperty(required=False)      # SegregatedImports
    dependent_internal_classes = ArrayProperty(StringProperty(), default=[])  # DependentInternalClasses
    global_variables = JSONProperty(default=[])            # GlobalVariables

    # RELATIONSHIPS
    # "Functions" from either ChapiNode or UnoplatChapiForgeNode become a relationship
    functions = RelationshipTo(".code_confluence_internal_function.CodeConfluenceInternalFunction", "HAS_FUNCTION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    # Classes can also have annotations
    annotations = RelationshipTo(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    # relation to package
    package = RelationshipFrom(".code_confluence_package.CodeConfluencePackage", "PART_OF_PACKAGE",model=ContainsRelationship,cardinality=One)