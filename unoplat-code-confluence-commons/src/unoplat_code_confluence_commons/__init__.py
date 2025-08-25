"""
Unoplat Code Confluence Commons package.
Contains models and utilities for code analysis and representation.
"""

from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    ClassInfo,
    Concept,
    ConstructQueryConfig,
    Detection,
    DetectionResult,
    FeatureAbsolutePath,
    FeatureSpec,
    # Framework SQLModel models
    Framework,
    FrameworkFeature,
    FunctionInfo,
    InheritanceInfo,
    LocatorStrategy,
    StructuralSignature,
    # Engine Pydantic models
    TargetLevel,
    # Structural signature models
    VariableInfo,
    # Repository and Programming Language models
    Repository,
    CodebaseConfigSQLModel,
    CodebaseConfig,
    RepositorySettings,
    ProgrammingLanguageMetadata,
    ProgrammingLanguage,
    PackageManagerType,
    # Credentials model
    Credentials,
    # Flags model
    Flag,
)
from unoplat_code_confluence_commons.security import (
    encrypt_token,
    decrypt_token,
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
