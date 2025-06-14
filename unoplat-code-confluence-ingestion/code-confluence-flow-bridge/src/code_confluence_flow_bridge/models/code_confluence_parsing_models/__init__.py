"""
Code Confluence Parsing Models

A unified package containing all data models for code parsing, analysis, and repository management.
This package consolidates all Chapi and Chapi Forge models into a single, coherent structure
for the Code Confluence parsing system.
"""

# Base utility models
from .position import Position

# Version and dependency models
from .unoplat_version import UnoplatVersion
from .unoplat_project_dependency import UnoplatProjectDependency
from .unoplat_package_manager_metadata import UnoplatPackageManagerMetadata

# Structural signature models
from .import_info import ImportInfo
from .variable_info import VariableInfo
from .function_info import FunctionInfo
from .class_info import ClassInfo
from .structural_signature import StructuralSignature

# File and package models
from .unoplat_file import UnoplatFile
from .unoplat_package import UnoplatPackage
from .unoplat_codebase import UnoplatCodebase
from .unoplat_git_repository import UnoplatGitRepository

# File processing models
from .file_processing_data import FileProcessingData
from .processing_batch import ProcessingBatch
from .processing_status import ProcessingStatus

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