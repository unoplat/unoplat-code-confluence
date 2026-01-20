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
    TypeScriptStructuralSignature,
    TypeScriptTypeAliasInfo,
    TypeScriptVariableInfo,
    deserialize_structural_signature,
    get_signature_type_for_language,
)
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
    SecretKind,
)
from unoplat_code_confluence_commons.repo_models import (
    RepositoryAgentMdSnapshot,
)
from unoplat_code_confluence_commons.relational_models import (
    UnoplatCodeConfluenceCodebase,
    UnoplatCodeConfluenceCodebaseFramework,
    UnoplatCodeConfluenceFile,
    UnoplatCodeConfluenceFileFrameworkFeature,
    UnoplatCodeConfluenceGitRepository,
    UnoplatCodeConfluencePackageManagerMetadata,
)
from unoplat_code_confluence_commons.security import (
    decrypt_token,
    encrypt_token,
)
from unoplat_code_confluence_commons.workflow_envelopes import (
    CodebaseWorkflowDbActivityEnvelope,
    ParentWorkflowDbActivityEnvelope,
)
from unoplat_code_confluence_commons.workflow_models import (
    ErrorReport,
    JobStatus,
)

__all__ = [
    # Python structural signature models
    'PythonVariableInfo',
    'PythonFunctionInfo',
    'PythonClassInfo',
    'PythonStructuralSignature',
    # TypeScript structural signature models
    'TypeScriptVariableInfo',
    'TypeScriptParameterInfo',
    'TypeScriptFunctionInfo',
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
    # Credentials and related enums
    'Credentials',
    'CredentialNamespace',
    'ProviderKey',
    'SecretKind',
    # Flags model
    'Flag',
    # Relational models (PostgreSQL)
    'UnoplatCodeConfluenceGitRepository',
    'UnoplatCodeConfluenceCodebase',
    'UnoplatCodeConfluencePackageManagerMetadata',
    'UnoplatCodeConfluenceFile',
    'UnoplatCodeConfluenceCodebaseFramework',
    'UnoplatCodeConfluenceFileFrameworkFeature',
    # Security utilities
    'encrypt_token',
    'decrypt_token',
    # Workflow models
    'JobStatus',
    'ErrorReport',
    # Workflow envelope models
    'ParentWorkflowDbActivityEnvelope',
    'CodebaseWorkflowDbActivityEnvelope',
]
