from unoplat_code_confluence_commons.graph_models.base_models import (
    ContainsRelationship,
)
from unoplat_code_confluence_commons.graph_models.code_confluence_framework import (
    UsesFeatureRelationship,
)

from neomodel import (
    ArrayProperty,
    AsyncOne,
    AsyncRelationshipTo,
    AsyncStructuredNode,
    AsyncZeroOrMore,
    BooleanProperty,
    JSONProperty,
    StringProperty,
)


# ⬇️  insert just above class `CodeConfluencePackage`
class CodeConfluenceFile(AsyncStructuredNode):
    """
    Graph node representing a single source file.

    Relationships
    ─────────────
    package  (PART_OF_PACKAGE)  -> CodeConfluencePackage
    """
    file_path = StringProperty(required=True, unique_index=True)
    content = StringProperty()
    checksum  = StringProperty()
    structural_signature = JSONProperty()
    imports = ArrayProperty(
        StringProperty(),
        default=[],
        index=True
    )
    global_variables = ArrayProperty(
        StringProperty(),
        default=[]
    )
    class_variables = JSONProperty(default={})
    has_data_model = BooleanProperty(default=False, index=True)
    data_model_positions = JSONProperty(default={})
    # Relationship to framework features detected in this file
      # local import to avoid cycles

    features = AsyncRelationshipTo(
        '.code_confluence_framework.CodeConfluenceFrameworkFeature',
        'USES_FEATURE',
        model=UsesFeatureRelationship,
        cardinality=AsyncZeroOrMore,
    )
    package = AsyncRelationshipTo(
        '.code_confluence_package.CodeConfluencePackage',
        'PART_OF_PACKAGE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )