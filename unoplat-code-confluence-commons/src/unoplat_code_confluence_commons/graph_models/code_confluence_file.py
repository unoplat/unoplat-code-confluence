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


# Graph node representing a single source file.
class CodeConfluenceFile(AsyncStructuredNode):
    """Graph node representing a single source file."""
    file_path = StringProperty(required=True, unique_index=True)
    content = StringProperty()
    checksum  = StringProperty()
    structural_signature = JSONProperty(default=None)
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
    # Relationship to framework features detected in this file (local import avoids cycles)
    features = AsyncRelationshipTo(
        '.code_confluence_framework.CodeConfluenceFrameworkFeature',
        'USES_FEATURE',
        model=UsesFeatureRelationship,
        cardinality=AsyncZeroOrMore,
    )
    codebase = AsyncRelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'PART_OF_CODEBASE',
        model=ContainsRelationship,
        cardinality=AsyncOne,
    )
