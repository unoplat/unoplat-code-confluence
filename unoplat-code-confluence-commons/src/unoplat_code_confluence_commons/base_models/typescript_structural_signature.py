"""Pydantic models for TypeScript/JavaScript file structural signatures.

Based on tree-sitter-typescript grammar and comprehensive query patterns.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class TypeScriptVariableInfo(BaseModel):
    """Information about a variable declaration (const, let, var)."""

    start_line: Optional[int] = Field(
        default=None, description="Starting line number of variable declaration"
    )
    end_line: Optional[int] = Field(
        default=None, description="Ending line number of variable declaration"
    )
    signature: Optional[str] = Field(
        default=None, description="Complete variable declaration including type annotation"
    )
    kind: Optional[str] = Field(
        default=None, description="Variable kind: const, let, or var"
    )


class TypeScriptParameterInfo(BaseModel):
    """Information about function/method parameters."""

    name: str = Field(..., description="Parameter name")
    type_annotation: Optional[str] = Field(None, description="Type annotation if present")
    optional: bool = Field(default=False, description="Whether parameter is optional")
    default_value: Optional[str] = Field(None, description="Default value if present")


class TypeScriptFunctionInfo(BaseModel):
    """Information about a function or method."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the function starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the function ends"
    )
    signature: Optional[str] = Field(
        default=None,
        description="Complete function declaration including async/function/arrow syntax, type parameters, parameters, return type",
    )
    docstring: Optional[str] = Field(None, description="JSDoc or TSDoc comment")
    #is_async: bool = Field(default=False, description="Whether function is async")
    nested_functions: List["TypeScriptFunctionInfo"] = Field(
        default_factory=list, description="Nested function declarations"
    )
    

#todo: enable later not in scope right now
# class TypeScriptPropertyInfo(BaseModel):
#     """Information about class properties/fields."""

#     start_line: Optional[int] = Field(
#         default=None, description="Line number where the property starts"
#     )
#     end_line: Optional[int] = Field(
#         default=None, description="Line number where the property ends"
#     )
#     signature: Optional[str] = Field(
#         default=None, description="Complete property declaration with modifiers and type"
#     )
    
class TypeScriptMethodInfo(BaseModel):
    """Information about class methods."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the method starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the method ends"
    )
    signature: Optional[str] = Field(
        default=None,
        description="Complete method declaration including modifiers, type parameters, parameters, return type",
    )
    docstring: Optional[str] = Field(None, description="JSDoc or TSDoc comment")
    #todo: enable later not in scope right now
    #is_async: bool = Field(default=False, description="Whether method is async")
    
    
class TypeScriptInterfacePropertyInfo(BaseModel):
    """Information about interface property signatures."""

    name: str = Field(..., description="Property name")
    signature: Optional[str] = Field(
        default=None, description="Complete property signature with type"
    )
   

class TypeScriptInterfaceMethodInfo(BaseModel):
    """Information about interface method signatures."""

    name: str = Field(..., description="Method name")
    signature: Optional[str] = Field(
        default=None, description="Complete method signature with parameters and return type"
    )


class TypeScriptInterfaceInfo(BaseModel):
    """Information about a TypeScript interface definition."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the interface starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the interface ends"
    )
    signature: Optional[str] = Field(
        default=None,
        description="Complete interface declaration including type parameters and extends clause",
    )
    docstring: Optional[str] = Field(None, description="Interface TSDoc comment")
    properties: List[TypeScriptInterfacePropertyInfo] = Field(
        default_factory=list, description="Interface property signatures"
    )
    methods: List[TypeScriptInterfaceMethodInfo] = Field(
        default_factory=list, description="Interface method signatures"
    )


class TypeScriptTypeAliasInfo(BaseModel):
    """Information about a TypeScript type alias."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the type alias starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the type alias ends"
    )
    signature: Optional[str] = Field(
        default=None, description="Complete type alias declaration including type parameters"
    )
    docstring: Optional[str] = Field(None, description="Type alias TSDoc comment")


class TypeScriptClassInfo(BaseModel):
    """Information about a class definition."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the class starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the class ends"
    )
    signature: Optional[str] = Field(
        default=None,
        description="Complete class declaration including decorators, abstract modifier, type parameters, implements, and extends clauses",
    )
    docstring: Optional[str] = Field(None, description="Class JSDoc or TSDoc comment")
    #todo: enable later not in scope right now
    #is_abstract: bool = Field(default=False, description="Whether class is abstract")
    decorators: List[str] = Field(default_factory=list, description="Class decorator names")
    # properties: List[TypeScriptPropertyInfo] = Field(
    #     default_factory=list, description="Class properties and fields"
    # )
    methods: List[TypeScriptMethodInfo] = Field(
        default_factory=list, description="Class methods including constructor"
    )
    nested_classes: List["TypeScriptClassInfo"] = Field(
        default_factory=list, description="Nested class declarations"
    )


class TypeScriptEnumMemberInfo(BaseModel):
    """Information about enum member."""

    name: str = Field(..., description="Enum member name")
    value: Optional[str] = Field(None, description="Enum member value if present")


class TypeScriptEnumInfo(BaseModel):
    """Information about a TypeScript enum definition."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the enum starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the enum ends"
    )
    signature: Optional[str] = Field(
        default=None, description="Complete enum declaration"
    )
    docstring: Optional[str] = Field(None, description="Enum TSDoc comment")
    is_const: bool = Field(default=False, description="Whether enum is const")
    members: List[TypeScriptEnumMemberInfo] = Field(
        default_factory=list, description="Enum members"
    )


class TypeScriptNamespaceInfo(BaseModel):
    """Information about a TypeScript namespace/module declaration."""

    start_line: Optional[int] = Field(
        default=None, description="Line number where the namespace starts"
    )
    end_line: Optional[int] = Field(
        default=None, description="Line number where the namespace ends"
    )
    signature: Optional[str] = Field(
        default=None, description="Complete namespace declaration"
    )
    docstring: Optional[str] = Field(None, description="Namespace TSDoc comment")
    is_ambient: bool = Field(
        default=False, description="Whether namespace is ambient (declare namespace)"
    )


class TypeScriptExportInfo(BaseModel):
    """Information about export statements."""

    export_type: str = Field(
        ..., description="Export type: named, default, all, or declaration"
    )
    exported_names: List[str] = Field(default_factory=list, description="Exported identifier names")
    source: Optional[str] = Field(None, description="Source module for re-exports")


class TypeScriptImportInfo(BaseModel):
    """Information about import statements."""

    import_type: str = Field(
        ..., description="Import type: named, default, namespace, or side-effect"
    )
    imported_names: List[str] = Field(default_factory=list, description="Imported identifier names")
    source: str = Field(..., description="Source module path")


class TypeScriptStructuralSignature(BaseModel):
    """
    Structural signature of a TypeScript/JavaScript source code file.

    This model captures the high-level structure and outline of a source file,
    including module-level constructs, functions, classes, interfaces, types,
    enums, namespaces, and their positions within the file.

    Based on tree-sitter-typescript grammar patterns.
    """

    module_docstring: Optional[str] = Field(
        None, description="Module-level JSDoc or TSDoc comment"
    )
    imports: List[TypeScriptImportInfo] = Field(
        default_factory=list, description="Import statements"
    )
    exports: List[TypeScriptExportInfo] = Field(
        default_factory=list, description="Export statements"
    )
    global_variables: List[TypeScriptVariableInfo] = Field(
        default_factory=list, description="Module-level variables (const, let, var)"
    )
    functions: List[TypeScriptFunctionInfo] = Field(
        default_factory=list, description="Module-level functions"
    )
    classes: List[TypeScriptClassInfo] = Field(
        default_factory=list, description="Class definitions"
    )
    interfaces: List[TypeScriptInterfaceInfo] = Field(
        default_factory=list, description="TypeScript interface definitions"
    )
    type_aliases: List[TypeScriptTypeAliasInfo] = Field(
        default_factory=list, description="TypeScript type alias definitions"
    )
    enums: List[TypeScriptEnumInfo] = Field(
        default_factory=list, description="TypeScript enum definitions"
    )
    namespaces: List[TypeScriptNamespaceInfo] = Field(
        default_factory=list, description="TypeScript namespace/module declarations"
    )


# Handle self-references for nested types
TypeScriptFunctionInfo.model_rebuild()
TypeScriptClassInfo.model_rebuild()
