"""
Unoplat Code Confluence Commons package.
Contains models and utilities for code analysis and representation.
"""

from unoplat_code_confluence_commons.base_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
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
    InheritanceInfo,
    LocatorStrategy,
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
    # Python structural signature models
    PythonClassInfo,
    PythonFunctionInfo,
    PythonStructuralSignature,
    PythonVariableInfo,
    # Repository and Programming Language models
    Repository,
    RepositorySettings,
    # Structural signature utilities
    StructuralSignatureUnion,
    # Engine Pydantic models
    TargetLevel,
    # TypeScript structural signature models
    TypeScriptClassInfo,
    TypeScriptEnumInfo,
    TypeScriptEnumMemberInfo,
    TypeScriptExportInfo,
    TypeScriptFunctionInfo,
    TypeScriptImportInfo,
    TypeScriptInterfaceInfo,
    TypeScriptInterfaceMethodInfo,
    TypeScriptInterfacePropertyInfo,
    TypeScriptMethodInfo,
    TypeScriptNamespaceInfo,
    TypeScriptParameterInfo,
    TypeScriptPropertyInfo,
    TypeScriptStructuralSignature,
    TypeScriptTypeAliasInfo,
    TypeScriptVariableInfo,
    deserialize_structural_signature,
    get_signature_type_for_language,
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
from unoplat_code_confluence_commons.repo_models import (
    RepoAgentSnapshotStatus,
    RepositoryAgentMdSnapshot,
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
    # Python structural signature models
    'PythonVariableInfo',
    'PythonFunctionInfo',
    'PythonClassInfo',
    'PythonStructuralSignature',
    # TypeScript structural signature models
    'TypeScriptVariableInfo',
    'TypeScriptParameterInfo',
    'TypeScriptFunctionInfo',
    'TypeScriptPropertyInfo',
    'TypeScriptMethodInfo',
    'TypeScriptInterfacePropertyInfo',
    'TypeScriptInterfaceMethodInfo',
    'TypeScriptInterfaceInfo',
    'TypeScriptTypeAliasInfo',
    'TypeScriptClassInfo',
    'TypeScriptEnumMemberInfo',
    'TypeScriptEnumInfo',
    'TypeScriptNamespaceInfo',
    'TypeScriptExportInfo',
    'TypeScriptImportInfo',
    'TypeScriptStructuralSignature',
    # Structural signature utilities
    'StructuralSignatureUnion',
    'deserialize_structural_signature',
    'get_signature_type_for_language',
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
    'RepositoryAgentMdSnapshot',
    'RepoAgentSnapshotStatus',
    # Credentials model
    'Credentials',
    # Flags model
    'Flag',
    # Security utilities
    'encrypt_token',
    'decrypt_token',
]
