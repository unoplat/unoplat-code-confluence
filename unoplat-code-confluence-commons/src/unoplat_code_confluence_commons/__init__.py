"""
Unoplat Code Confluence Commons package.
Contains models and utilities for code analysis and representation.
"""

from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    ClassInfo,
    CodebaseConfig,
    CodebaseConfigSQLModel,
    Concept,
    ConstructQueryConfig,
    # Credentials model
    Credentials,
    Detection,
    DetectionResult,
    FeatureAbsolutePath,
    FeatureSpec,
    # Flags model
    Flag,
    # Framework SQLModel models
    Framework,
    FrameworkFeature,
    FunctionInfo,
    InheritanceInfo,
    LocatorStrategy,
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    # Repository and Programming Language models
    Repository,
    RepositorySettings,
    StructuralSignature,
    # Engine Pydantic models
    TargetLevel,
    # Structural signature models
    VariableInfo,
)
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
from unoplat_code_confluence_commons.security import (
    decrypt_token,
    encrypt_token,
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
    # Repository and Programming Language models
    'Repository',
    'CodebaseConfigSQLModel',
    'CodebaseConfig',
    'RepositorySettings',
    'ProgrammingLanguageMetadata',
    'ProgrammingLanguage',
    'PackageManagerType',
    # Credentials model
    'Credentials',
    # Flags model
    'Flag',
    # Security utilities
    'encrypt_token',
    'decrypt_token',
]
