"""
Code Confluence Parsing Models

A unified package containing all data models for code parsing, analysis, and repository management.
This package consolidates all Chapi and Chapi Forge models into a single, coherent structure
for the Code Confluence parsing system.
"""

# Base utility models
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.class_info import (
    ClassInfo,
)

# File processing models
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.file_processing_data import (
    FileProcessingData,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.function_info import (
    FunctionInfo,
)

# Structural signature models
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.import_info import (
    ImportInfo,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.position import (
    Position,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.processing_batch import (
    ProcessingBatch,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.processing_status import (
    ProcessingStatus,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.structural_signature import (
    StructuralSignature,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_codebase import (
    UnoplatCodebase,
)

# File and package models
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_git_repository import (
    UnoplatGitRepository,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package import (
    UnoplatPackage,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_package_manager_metadata import (
    UnoplatPackageManagerMetadata,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_project_dependency import (
    UnoplatProjectDependency,
)

# Version and dependency models
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_version import (
    UnoplatVersion,
)
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.variable_info import (
    VariableInfo,
)

__all__ = [
    # Base models
    "Position",
    "UnoplatVersion",
    "UnoplatProjectDependency", 
    "UnoplatPackageManagerMetadata",
    # Structural signature models
    "ImportInfo",
    "VariableInfo",
    "FunctionInfo",
    "ClassInfo", 
    "StructuralSignature",
    # File and package models
    "UnoplatFile",
    "UnoplatPackage",
    "UnoplatCodebase",
    "UnoplatGitRepository",
    # File processing models
    "FileProcessingData",
    "ProcessingBatch",
    "ProcessingStatus",
]