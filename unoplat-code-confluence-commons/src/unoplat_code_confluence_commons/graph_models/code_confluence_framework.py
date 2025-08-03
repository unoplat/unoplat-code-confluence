
from unoplat_code_confluence_commons.graph_models.base_models import (
    BaseNode,
    ContainsRelationship,
)

from neomodel import (
    AsyncRelationshipFrom,
    AsyncRelationshipTo,
    AsyncStructuredRel,
    AsyncZeroOrMore,
    IntegerProperty,
    StringProperty,
)


class UsesFeatureRelationship(AsyncStructuredRel):
    """Relationship from CodeConfluenceFile to FrameworkFeature storing line span."""

    start_line = IntegerProperty()
    end_line = IntegerProperty()


class CodeConfluenceFramework(BaseNode):
    """Minimal node representing a programming language + library/framework pair."""

    language = StringProperty(required=True, index=True)
    library = StringProperty(required=True, index=True)

    # Relationships
    features = AsyncRelationshipTo(
        '.code_confluence_framework.CodeConfluenceFrameworkFeature',
        'HAS_FEATURE',
        model=ContainsRelationship,
        cardinality=AsyncZeroOrMore,
    )
    codebases = AsyncRelationshipTo(
        '.code_confluence_codebase.CodeConfluenceCodebase',
        'USED_BY',
        model=ContainsRelationship,
    )


class CodeConfluenceFrameworkFeature(BaseNode):
    """Node representing a single feature of a framework."""

    language = StringProperty(required=True, index=True)
    library = StringProperty(required=True, index=True)
    feature_key = StringProperty(required=True, index=True)

    # Relationships
    framework = AsyncRelationshipFrom(
        '.code_confluence_framework.CodeConfluenceFramework',
        'HAS_FEATURE',
        model=ContainsRelationship,
    )

    files = AsyncRelationshipFrom(
        '.code_confluence_file.CodeConfluenceFile',
        'USES_FEATURE',
        model=UsesFeatureRelationship,
    ) 