"""Common Pydantic and SQLModel base models for unoplat-code-confluence projects."""

# Data model position models
from unoplat_code_confluence_commons.base_models.data_model_position import (
    DataModelPosition,
)

# Structural signature models
# Engine Pydantic models
from unoplat_code_confluence_commons.base_models.engine_models import (
    AnnotationLikeInfo,
    CallExpressionInfo,
    Concept,
    ConstructQueryConfig,
    Detection,
    DetectionResult,
    FeatureSpec,
    InheritanceInfo,
    LocatorStrategy,
    TargetLevel,
)

# Framework SQLModel models
from unoplat_code_confluence_commons.base_models.framework_models import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)
from unoplat_code_confluence_commons.base_models.python_structural_signature import (
    PythonClassInfo,
    PythonFunctionInfo,
    PythonStructuralSignature,
    PythonVariableInfo,
)

# SQL Base class
from unoplat_code_confluence_commons.base_models.sql_base import (
    SQLBase,
)

# Structural signature utilities
from unoplat_code_confluence_commons.base_models.structural_signature_utils import (
    StructuralSignatureUnion,
    deserialize_structural_signature,
    get_signature_type_for_language,
)

# TypeScript structural signature models
from unoplat_code_confluence_commons.base_models.typescript_structural_signature import (
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
)
from unoplat_code_confluence_commons.configuration_models import (
    CodebaseConfig,
    RepositorySettings,
)

# Credentials model
from unoplat_code_confluence_commons.credentials import (
    Credentials,
)

# Flags model
from unoplat_code_confluence_commons.flags import (
    Flag,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Repository and Programming Language models
from unoplat_code_confluence_commons.repo_models import (
    CodebaseConfig as CodebaseConfigSQLModel,
    CodebaseWorkflowRun,
    Repository,
    RepositoryWorkflowOperation,
    RepositoryWorkflowRun,
)

__all__ = [
    # Data model position models
    "DataModelPosition",
    # Python Structural signature models
    "PythonVariableInfo",
    "PythonFunctionInfo",
    "PythonClassInfo",
    "PythonStructuralSignature",
    # TypeScript Structural signature models
    "TypeScriptVariableInfo",
    "TypeScriptParameterInfo",
    "TypeScriptFunctionInfo",
    "TypeScriptMethodInfo",
    "TypeScriptInterfacePropertyInfo",
    "TypeScriptInterfaceMethodInfo",
    "TypeScriptInterfaceInfo",
    "TypeScriptTypeAliasInfo",
    "TypeScriptClassInfo",
    "TypeScriptEnumMemberInfo",
    "TypeScriptEnumInfo",
    "TypeScriptNamespaceInfo",
    "TypeScriptExportInfo",
    "TypeScriptImportInfo",
    "TypeScriptStructuralSignature",
    # Structural signature utilities
    "StructuralSignatureUnion",
    "deserialize_structural_signature",
    "get_signature_type_for_language",
    # Engine Pydantic models
    "TargetLevel",
    "LocatorStrategy",
    "Concept",
    "ConstructQueryConfig",
    "FeatureSpec",
    "Detection",
    "DetectionResult",
    "AnnotationLikeInfo",
    "CallExpressionInfo",
    "InheritanceInfo",
    # Framework SQLModel models
    "Framework",
    "FrameworkFeature",
    "FeatureAbsolutePath",
    # Repository and Programming Language models
    "Repository",
    "CodebaseConfigSQLModel",
    "CodebaseConfig",
    "RepositorySettings",
    "RepositoryWorkflowRun",
    "RepositoryWorkflowOperation",
    "CodebaseWorkflowRun",
    "ProgrammingLanguageMetadata",
    "ProgrammingLanguage",
    "PackageManagerType",
    # Credentials model
    "Credentials",
    # Flags model
    "Flag",
    # SQL Base class
    "SQLBase",
]
