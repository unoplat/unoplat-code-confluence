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

from .base_models import BaseNode, ContainsRelationship

class CodeConfluenceClass(BaseNode):
    """
    Represents a class-like node, combining fields from:
      - ChapiNode
      - UnoplatChapiForgeNode
    """
    # From ChapiNode
    node_name = StringProperty()       # NodeName
    type_ = StringProperty()           # Type (renamed to avoid Python 'type' shadowing)
    file_path = StringProperty()       # FilePath
    module = StringProperty()          # Module
    multiple_extend = ArrayProperty(StringProperty(), default=[])  # MultipleExtend
    fields = JSONProperty()                # Fields (list of ClassGlobalFieldModel)
    extend = StringProperty()          # Extend
    position = JSONProperty()          # Position
    content = StringProperty()         # Content

    # From UnoplatChapiForgeNode
    comments_description = StringProperty()  # CommentsDescription
    segregated_imports = JSONProperty()      # SegregatedImports
    dependent_internal_classes = ArrayProperty(StringProperty(), default=[])  # DependentInternalClasses
    global_variables = JSONProperty(default=[])            # GlobalVariables

    # RELATIONSHIPS
    # "Functions" from either ChapiNode or UnoplatChapiForgeNode become a relationship
    functions = RelationshipTo(".code_confluence_internal_function.CodeConfluenceInternalFunction", "HAS_FUNCTION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    # Classes can also have annotations
    annotations = RelationshipTo(".code_confluence_annotation.CodeConfluenceAnnotation", "HAS_ANNOTATION",model=ContainsRelationship,cardinality=ZeroOrMore)
    
    # relation to package
    package = RelationshipFrom(".code_confluence_package.CodeConfluencePackage", "PART_OF_PACKAGE",model=ContainsRelationship,cardinality=One)