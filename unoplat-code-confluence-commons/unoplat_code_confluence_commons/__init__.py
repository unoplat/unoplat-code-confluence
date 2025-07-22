"""
Unoplat Code Confluence Commons package.
Contains models and utilities for code analysis and representation.
"""

from unoplat_code_confluence_commons.graph_models import (
    BaseNode,
    CodeConfluenceCodebase,
    CodeConfluenceFile,
    CodeConfluenceFramework,
    CodeConfluenceFrameworkFeature,
    CodeConfluenceGitRepository,
    CodeConfluencePackage,
    CodeConfluencePackageManagerMetadata,
    ContainsRelationship,
    UsesFeatureRelationship,
)

from unoplat_code_confluence_commons.base_models import (
    # Structural signature models
    VariableInfo,
    FunctionInfo,
    ClassInfo,
    StructuralSignature,
    # Engine Pydantic models
    TargetLevel,
    LocatorStrategy,
    Concept,
    ConstructQueryConfig,
    FeatureSpec,
    Detection,
    DetectionResult,
    AnnotationLikeInfo,
    CallExpressionInfo,
    InheritanceInfo,
    # Framework SQLModel models
    Framework,
    FrameworkFeature,
    FeatureAbsolutePath,
)

__all__ = [
    # Graph models
    'BaseNode',
    'CodeConfluenceCodebase',
    'CodeConfluenceFile',
    'CodeConfluenceFramework',
    'CodeConfluenceFrameworkFeature',
    'CodeConfluenceGitRepository',
    'CodeConfluencePackage',
    'CodeConfluencePackageManagerMetadata',
    'ContainsRelationship',
    'UsesFeatureRelationship',
    # Structural signature models
    'VariableInfo',
    'FunctionInfo',
    'ClassInfo',
    'StructuralSignature',
    # Engine Pydantic models
    'TargetLevel',
    'LocatorStrategy',
    'Concept',
    'ConstructQueryConfig',
    'FeatureSpec',
    'Detection',
    'DetectionResult',
    'AnnotationLikeInfo',
    'CallExpressionInfo',
    'InheritanceInfo',
    # Framework SQLModel models
    'Framework',
    'FrameworkFeature',
    'FeatureAbsolutePath',
]
