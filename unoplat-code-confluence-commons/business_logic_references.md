# Business Logic References

## Domain Summary
This codebase is for a “code confluence” platform that ingests repositories and codebases, then stores repository, file, and workflow metadata in PostgreSQL. Its main business logic revolves around analyzing source code structure, tracking Python/TypeScript signatures and data model spans, and defining framework features and query rules to detect library usage across codebases. It also manages agent execution history, progress snapshots, package-manager/language metadata, credentials, feature flags, and AGENTS.md publication metadata.

## Data Model References
### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/data_model_position.py#L8-L14` — `class DataModelPosition(BaseModel):
    """Represents positions of data models detected in a file."""

    positions: Dict[str, Tuple[int, int]] = Field(
        default_factory=dict,
        description="Map of data model names to their (start_position, end_position) in the file",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L51-L76` — `class ConstructQueryConfig(BaseModel):
    """Typed construct query configuration matching JSON schema structure."""

    method_regex: Optional[str] = Field(
        None, description="Regex for method names (AnnotationLike)"
    )
    annotation_name_regex: Optional[str] = Field(
        None, description="Regex for annotation names"
    )
    attribute_regex: Optional[str] = Field(
        None, description="Regex for attribute patterns"
    )
    callee_regex: Optional[str] = Field(
        None, description="Regex for call expression callees"
    )
    superclass_regex: Optional[str] = Field(
        None, description="Regex for superclass names (Inheritance)"
    )
    function_name_regex: Optional[str] = Field(
        None, description="Regex for function declaration names (FunctionDefinition)"
    )
    export_name_regex: Optional[str] = Field(
        None, description="Regex for exported symbol names (FunctionDefinition)"
    )

    model_config = ConfigDict(extra="forbid")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L99-L169` — `class FeatureSpec(BaseModel):
    """Strongly-typed feature specification from schema."""

    capability_key: str = Field(
        ...,
        min_length=1,
        description="Capability family this feature belongs to",
    )
    operation_key: str = Field(
        ...,
        min_length=1,
        description="Operation identifier within the capability",
    )
    library: str = Field(
        ..., description="Library/framework name this feature belongs to"
    )
    absolute_paths: List[str] = Field(
        ..., min_length=1, description="Fully qualified import paths"
    )
    target_level: TargetLevel = Field(..., description="function or class")
    concept: Concept = Field(
        ...,
        description="Semantic concept (AnnotationLike, CallExpression, Inheritance, etc.)",
    )
    locator_strategy: LocatorStrategy = Field(
        ..., description="VariableBound or Direct"
    )
    construct_query: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Language-specific tweaks for ConceptQuery construction (new schema field)",
    )

    @property
    def construct_query_typed(self) -> Optional[ConstructQueryConfig]:
        """Get construct_query as typed configuration."""
        if not self.construct_query:
            return None
        try:
            return ConstructQueryConfig.model_validate(self.construct_query)
        except Exception:
            return None

    @construct_query_typed.setter
    def construct_query_typed(self, value: Optional[ConstructQueryConfig]) -> None:
        """Set construct_query from typed configuration."""
        if value is None:
            self.construct_query = None
        else:
            self.construct_query = value.model_dump(exclude_none=True)

    description: Optional[str] = Field(None, description="Human-readable description")
    base_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Baseline confidence for CallExpression feature definitions",
    )
    startpoint: bool = Field(
        default=False,
        description="Indicates whether this feature represents a starting point or entry point in the application",
    )

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)

    @model_validator(mode="after")
    def validate_base_confidence_scope(self) -> Self:
        _validate_base_confidence_scope(self.concept, self.base_confidence)
        return self`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L172-L214` — `class FrameworkFeaturePayload(BaseModel):
    """JSONB payload shape for framework_feature.feature_definition."""

    description: Optional[str] = Field(None, description="Human-readable description")
    absolute_paths: List[str] = Field(
        default_factory=list,
        description="Fully qualified import paths",
    )
    target_level: TargetLevel = Field(
        default=TargetLevel.FUNCTION,
        description="function or class",
    )
    concept: Concept = Field(
        default=Concept.ANNOTATION_LIKE,
        description="Semantic concept",
    )
    locator_strategy: LocatorStrategy = Field(
        default=LocatorStrategy.VARIABLE_BOUND,
        description="VariableBound or Direct",
    )
    construct_query: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Language-specific tweaks for ConceptQuery construction",
    )
    base_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Baseline confidence for CallExpression feature definitions",
    )
    startpoint: bool = Field(
        default=False,
        description="Feature is a starting point",
    )
    notes: Optional[str] = Field(default=None, description="Contributor notes, caveats, disambiguation guidance")
    docs_url: Optional[str] = Field(default=None, description="Operation-specific documentation URL")

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    @model_validator(mode="after")
    def validate_base_confidence_scope(self) -> Self:
        _validate_base_confidence_scope(self.concept, self.base_confidence)
        return self`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L217-L235` — `class FeatureUsagePayload(BaseModel):
    """Typed payload for detected feature usage confidence metadata."""

    match_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for a single detected usage",
    )
    validation_status: ValidationStatus = Field(
        default=ValidationStatus.COMPLETED,
        description="Validation lifecycle state for the usage row",
    )
    evidence_json: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Structured evidence payload supporting usage classification",
    )

    model_config = ConfigDict(use_enum_values=True)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L238-L264` — `class Detection(BaseModel):
    """Result of feature detection in source code."""

    capability_key: str = Field(
        ...,
        min_length=1,
        description="Capability family for the detected feature",
    )
    operation_key: str = Field(
        ...,
        min_length=1,
        description="Operation identifier for the detected feature",
    )
    library: str = Field(
        ..., description="Library/framework name this feature belongs to"
    )
    match_text: str = Field(..., description="The actual text that matched")
    start_line: int = Field(..., description="Starting line number (1-indexed)")
    end_line: int = Field(..., description="Ending line number (1-indexed)")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/engine_models.py#L267-L286` — `class DetectionResult(BaseModel):
    """Complete detection result returned by an engine run."""

    success: bool = Field(..., description="Whether detection completed successfully")
    detections: Dict[str, List[Detection]] = Field(
        default_factory=dict,
        description="Feature key to list of detections",
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Critical errors that prevented detection",
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-critical issues encountered during detection",
    )
    unsupported_features: List[str] = Field(
        default_factory=list,
        description="Features that couldn't be processed by the engine",
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L32-L54` — `class Framework(SQLBase):
    """Language-library combo ("python-fastapi", etc.)."""

    __tablename__ = "framework"
    __table_args__ = {"extend_existing": True}

    language: Mapped[str] = mapped_column(
        primary_key=True, comment="Programming language"
    )
    library: Mapped[str] = mapped_column(
        primary_key=True, comment="Library / framework"
    )
    docs_url: Mapped[Optional[str]] = mapped_column(default=None, comment="Docs URL")
    description: Mapped[Optional[str]] = mapped_column(
        default=None, comment="Framework/library description"
    )

    # Relationships
    features: Mapped[List["FrameworkFeature"]] = relationship(
        back_populates="framework",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L60-L217` — `class FrameworkFeature(SQLBase):
    """Per-feature metadata keyed by capability + operation."""

    __tablename__ = "framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(  # FK → Framework
            ["language", "library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        Index(
            "framework_feature_definition_gin_idx",
            "feature_definition",
            postgresql_using="gin",
            postgresql_ops={"feature_definition": "jsonb_path_ops"},
        ),
        Index(
            "framework_feature_startpoint_bool_idx",
            text("coalesce((feature_definition['startpoint'])::boolean, false)"),
        ),
        {"extend_existing": True},
    )

    # Composite PK = language + library + capability_key + operation_key
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    capability_key: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Capability family this feature belongs to",
    )
    operation_key: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Operation identifier within the capability",
    )

    feature_definition: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
        comment="Source-of-truth JSONB payload for feature schema fields",
    )

    # Relationships
    framework: Mapped[Framework] = relationship(back_populates="features")
    absolute_paths: Mapped[List["FeatureAbsolutePath"]] = relationship(
        back_populates="feature",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)

    @property
    def description(self) -> Optional[str]:
        """Return description from feature_definition."""
        value = self.feature_definition.get("description")
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise TypeError("feature_definition.description must be a string")

    @property
    def target_level(self) -> TargetLevel:
        """Return target level from feature_definition."""
        value = self.feature_definition["target_level"]
        if isinstance(value, TargetLevel):
            return value
        if isinstance(value, str):
            return TargetLevel(value)
        raise TypeError("feature_definition.target_level must be a string enum value")

    @property
    def concept(self) -> Concept:
        """Return concept from feature_definition."""
        value = self.feature_definition["concept"]
        if isinstance(value, Concept):
            return value
        if isinstance(value, str):
            return Concept(value)
        raise TypeError("feature_definition.concept must be a string enum value")

    @property
    def locator_strategy(self) -> LocatorStrategy:
        """Return locator strategy from feature_definition."""
        value = self.feature_definition["locator_strategy"]
        if isinstance(value, LocatorStrategy):
            return value
        if isinstance(value, str):
            return LocatorStrategy(value)
        raise TypeError(
            "feature_definition.locator_strategy must be a string enum value"
        )

    @property
    def construct_query(self) -> Optional[dict[str, object]]:
        """Return construct_query from feature_definition."""
        value = self.feature_definition.get("construct_query")
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        raise TypeError("feature_definition.construct_query must be an object")

    @property
    def startpoint(self) -> bool:
        """Return startpoint from feature_definition."""
        value = self.feature_definition["startpoint"]
        if isinstance(value, bool):
            return value
        raise TypeError("feature_definition.startpoint must be a boolean")

    @property
    def base_confidence(self) -> float | None:
        """Return base confidence from feature_definition when present."""
        value = self.feature_definition.get("base_confidence")
        if value is None:
            return None
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        raise TypeError("feature_definition.base_confidence must be a number")

    @classmethod
    def concept_sql_expression(cls) -> ColumnElement[str]:
        """SQL expression for concept reads/grouping."""
        return cls.feature_definition["concept"].astext

    @classmethod
    def startpoint_sql_expression(cls) -> ColumnElement[bool]:
        """SQL expression for startpoint reads/filtering."""
        return func.coalesce(cls.feature_definition["startpoint"].as_boolean(), False)

    @property
    def construct_query_typed(self) -> Optional[ConstructQueryConfig]:
        """Get construct_query as typed configuration."""
        construct_query = self.construct_query
        if not construct_query:
            return None
        try:
            return ConstructQueryConfig.model_validate(construct_query)
        except Exception:
            return None

    @construct_query_typed.setter
    def construct_query_typed(self, value: Optional[ConstructQueryConfig]) -> None:
        """Set construct_query from typed configuration."""
        updated_feature_definition = dict(self.feature_definition)
        if value is None:
            updated_feature_definition.pop("construct_query", None)
        else:
            updated_feature_definition["construct_query"] = value.model_dump(
                exclude_none=True
            )
        self.feature_definition = updated_feature_definition`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/framework_models.py#L223-L265` — `class FeatureAbsolutePath(SQLBase):
    """Maps each absolute import path to its feature."""

    __tablename__ = "feature_absolute_path"
    __table_args__ = (
        ForeignKeyConstraint(  # FK → FrameworkFeature
            ["language", "library", "capability_key", "operation_key"],
            [
                "framework_feature.language",
                "framework_feature.library",
                "framework_feature.capability_key",
                "framework_feature.operation_key",
            ],
            ondelete="CASCADE",
        ),
        # Fast lookup by path + covering columns for an index-only probe
        Index(
            "path_lookup_idx",
            "absolute_path",
            postgresql_include=(
                "language",
                "library",
                "capability_key",
                "operation_key",
            ),
        ),
        {"extend_existing": True},
    )

    # Composite PK = language + library + capability_key + operation_key + absolute_path
    language: Mapped[str] = mapped_column(primary_key=True)
    library: Mapped[str] = mapped_column(primary_key=True)
    capability_key: Mapped[str] = mapped_column(primary_key=True)
    operation_key: Mapped[str] = mapped_column(primary_key=True)
    absolute_path: Mapped[str] = mapped_column(primary_key=True, comment="Import path")

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(self.capability_key, self.operation_key)

    # Relationship back to metadata
    feature: Mapped[FrameworkFeature] = relationship(back_populates="absolute_paths")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L11-L15` — `class PythonVariableInfo(BaseModel):
    """Information about a global variable declaration."""
    start_line: int = Field(..., description="Starting line number of variable declaration")
    end_line: int = Field(..., description="Ending line number of variable declaration")
    signature: str = Field(..., description="Complete variable declaration line(s)")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L18-L26` — `class PythonFunctionInfo(BaseModel):
    """Information about a function or method."""
    start_line: int = Field(..., description="Line number where the function starts")
    end_line: int = Field(..., description="Line number where the function ends")
    signature: str = Field(..., description="Complete function declaration including decorators, def/async def, parameters, return type")
    docstring: Optional[str] = Field(None, description="Function docstring")
    function_calls: List[str] = Field(default_factory=list, description="Fully-qualified names of function calls inside the function body, in order of appearance")
    nested_functions: List['PythonFunctionInfo'] = Field(default_factory=list, description="Nested functions declarations")
    instance_variables: List['PythonVariableInfo'] = Field(default_factory=list, description="Instance variable assignments (self.*) within this method")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L29-L37` — `class PythonClassInfo(BaseModel):
    """Information about a class definition."""
    start_line: int = Field(..., description="Line number where the class starts")
    end_line: int = Field(..., description="Line number where the class ends")
    signature: str = Field(..., description="Complete class declaration including decorators and inheritance")
    docstring: Optional[str] = Field(None, description="Class docstring")
    vars: List[PythonVariableInfo] = Field(default_factory=list, description="Class and instance variables")
    methods: List[PythonFunctionInfo] = Field(default_factory=list, description="Class methods")
    nested_classes: List['PythonClassInfo'] = Field(default_factory=list, description="Nested class declarations")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/python_structural_signature.py#L40-L51` — `class PythonStructuralSignature(BaseModel):
    """
    Structural signature of a Python source code file.

    This model captures the high-level structure and outline of a source file,
    including module-level constructs, functions, classes, and their
    positions within the file.
    """
    module_docstring: Optional[str] = Field(None, description="Module-level docstring")
    global_variables: List[PythonVariableInfo] = Field(default_factory=list, description="Module-level variables")
    functions: List[PythonFunctionInfo] = Field(default_factory=list, description="Module-level functions")
    classes: List[PythonClassInfo] = Field(default_factory=list, description="Class definitions")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L11-L25` — `class TypeScriptVariableInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L28-L34` — `class TypeScriptParameterInfo(BaseModel):
    """Information about function/method parameters."""

    name: str = Field(..., description="Parameter name")
    type_annotation: Optional[str] = Field(None, description="Type annotation if present")
    optional: bool = Field(default=False, description="Whether parameter is optional")
    default_value: Optional[str] = Field(None, description="Default value if present")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L37-L54` — `class TypeScriptFunctionInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L71-L86` — `class TypeScriptMethodInfo(BaseModel):
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
    #is_async: bool = Field(default=False, description="Whether method is async")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L89-L95` — `class TypeScriptInterfacePropertyInfo(BaseModel):
    """Information about interface property signatures."""

    name: str = Field(..., description="Property name")
    signature: Optional[str] = Field(
        default=None, description="Complete property signature with type"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L98-L104` — `class TypeScriptInterfaceMethodInfo(BaseModel):
    """Information about interface method signatures."""

    name: str = Field(..., description="Method name")
    signature: Optional[str] = Field(
        default=None, description="Complete method signature with parameters and return type"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L107-L126` — `class TypeScriptInterfaceInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L129-L141` — `class TypeScriptTypeAliasInfo(BaseModel):
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
    docstring: Optional[str] = Field(None, description="Type alias TSDoc comment")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L144-L169` — `class TypeScriptClassInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L172-L176` — `class TypeScriptEnumMemberInfo(BaseModel):
    """Information about enum member."""

    name: str = Field(..., description="Enum member name")
    value: Optional[str] = Field(None, description="Enum member value if present")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L179-L195` — `class TypeScriptEnumInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L198-L213` — `class TypeScriptNamespaceInfo(BaseModel):
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
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L216-L223` — `class TypeScriptExportInfo(BaseModel):
    """Information about export statements."""

    export_type: str = Field(
        ..., description="Export type: named, default, all, or declaration"
    )
    exported_names: List[str] = Field(default_factory=list, description="Exported identifier names")
    source: Optional[str] = Field(None, description="Source module for re-exports")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L226-L233` — `class TypeScriptImportInfo(BaseModel):
    """Information about import statements."""

    import_type: str = Field(
        ..., description="Import type: named, default, namespace, or side-effect"
    )
    imported_names: List[str] = Field(default_factory=list, description="Imported identifier names")
    source: str = Field(..., description="Source module path")`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/base_models/typescript_structural_signature.py#L236-L276` — `class TypeScriptStructuralSignature(BaseModel):
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
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py#L10-L19` — `class CodebaseConfig(BaseModel):
    """Pydantic model for codebase configuration in JSON config files."""
    codebase_folder: str  
    root_packages: Optional[list[str]] = Field(
        default=None,
        description=(
            "Relative paths (POSIX) to each root package inside codebase_folder."
        ),
    )
    programming_language_metadata: ProgrammingLanguageMetadata`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/configuration_models.py#L22-L26` — `class RepositorySettings(BaseModel):
    """Pydantic model for repository settings in JSON config files."""
    git_url: str
    output_path: str
    codebases: List[CodebaseConfig]`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/credentials.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/credentials.py#L20-L48` — `class Credentials(SQLBase):
    """Model for storing encrypted credentials with support for multiple credential types."""

    __tablename__ = "credentials"
    __table_args__ = (
        # Add unique constraint on credential_key for multi-key credential support
        Index(
            "uq_credentials_namespace_provider_secret",
            "namespace",
            "provider_key",
            "secret_kind",
            unique=True,
        ),
        # Keep existing unique constraint on token_hash for backward compatibility
    )
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    namespace: Mapped[CredentialNamespace] = mapped_column(nullable=False)
    provider_key: Mapped[ProviderKey] = mapped_column(nullable=False)
    secret_kind: Mapped[SecretKind] = mapped_column(nullable=False)
    token_hash: Mapped[str] = mapped_column(comment="Encrypted credential value")
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, default=None, comment="Provider specific metadata", nullable=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), default=None
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/flags.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/flags.py#L8-L15` — `class Flag(SQLBase):
    """Model for storing feature flags."""
    
    __tablename__ = "flag"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    status: Mapped[bool] = mapped_column(default=False)`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/pr_metadata_model.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/pr_metadata_model.py#L7-L27` — `class PrMetadata(BaseModel):
    """Persisted metadata for a manual AGENTS.md PR publication.

    Stored as JSONB on RepositoryAgentMdSnapshot.pr_metadata.
    One row per (owner, repo, workflow_run_id) — one-shot semantics
    mean the first successful publish writes this; subsequent calls
    for the same run are no-ops.
    """

    pr_number: int | None = Field(default=None)
    pr_url: str | None = Field(default=None)
    branch_name: str | None = Field(default=None)
    status: Literal["modified", "no_changes"] = Field(...)
    changed_files: list[str] = Field(default_factory=list)
    message: str = Field(...)
    created_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: AwareDatetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/programming_language_metadata.py#L32-L41` — `class ProgrammingLanguageMetadata(BaseModel):
    language: ProgrammingLanguage
    package_manager: Optional[PackageManagerType] = None
    language_version: Optional[str] = None
    manifest_path: Optional[str] = None
    project_name: Optional[str] = None
    package_manager_provenance: Optional[PackageManagerProvenance] = None
    workspace_root: Optional[str] = None
    workspace_orchestrator: Optional[WorkspaceOrchestratorType] = None
    workspace_orchestrator_config_path: Optional[str] = None`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L13-L36` — `class UnoplatCodeConfluenceGitRepository(SQLBase):
    """Git repository stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_git_repository"
    __table_args__ = (
        Index("uq_cc_git_repo_url", "repository_url", unique=True),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_url: Mapped[str] = mapped_column(nullable=False)
    repository_name: Mapped[str] = mapped_column(nullable=False)
    repository_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    domain: Mapped[Optional[str]] = mapped_column(default=None)
    github_organization: Mapped[Optional[str]] = mapped_column(default=None)

    codebases: Mapped[List["UnoplatCodeConfluenceCodebase"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L39-L81` — `class UnoplatCodeConfluenceCodebase(SQLBase):
    """Codebase stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_codebase"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_qualified_name"],
            ["code_confluence_git_repository.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    qualified_name: Mapped[str] = mapped_column(primary_key=True)
    repository_qualified_name: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    readme: Mapped[Optional[str]] = mapped_column(default=None)
    root_packages: Mapped[Optional[List[str]]] = mapped_column(JSONB, default=None)
    codebase_path: Mapped[str] = mapped_column(nullable=False)
    codebase_folder: Mapped[Optional[str]] = mapped_column(default=None)
    programming_language: Mapped[Optional[str]] = mapped_column(default=None)

    repository: Mapped[UnoplatCodeConfluenceGitRepository] = relationship(
        back_populates="codebases"
    )
    package_manager_metadata: Mapped[
        Optional["UnoplatCodeConfluencePackageManagerMetadata"]
    ] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )
    files: Mapped[List["UnoplatCodeConfluenceFile"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    frameworks: Mapped[List["UnoplatCodeConfluenceCodebaseFramework"]] = relationship(
        back_populates="codebase",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L84-L111` — `class UnoplatCodeConfluencePackageManagerMetadata(SQLBase):
    """Package manager metadata stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_package_manager_metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        Index(
            "uq_cc_pkg_metadata_codebase",
            "codebase_qualified_name",
            unique=True,
        ),
        {"extend_existing": True},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    dependencies: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    other_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)
    package_manager: Mapped[str] = mapped_column(nullable=False)
    programming_language: Mapped[str] = mapped_column(nullable=False)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="package_manager_metadata"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L114-L146` — `class UnoplatCodeConfluenceFile(SQLBase):
    """Source file stored in PostgreSQL for Code Confluence."""

    __tablename__ = "code_confluence_file"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    codebase_qualified_name: Mapped[str] = mapped_column(nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(default=None)
    structural_signature: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None
    )
    imports: Mapped[List[str]] = mapped_column(JSONB, default=list)
    has_data_model: Mapped[bool] = mapped_column(default=False)
    data_model_positions: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="files"
    )
    framework_features: Mapped[List["UnoplatCodeConfluenceFileFrameworkFeature"]] = (
        relationship(
            back_populates="file",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L149-L173` — `class UnoplatCodeConfluenceCodebaseFramework(SQLBase):
    """Join table linking codebases to frameworks."""

    __tablename__ = "code_confluence_codebase_framework"
    __table_args__ = (
        ForeignKeyConstraint(
            ["codebase_qualified_name"],
            ["code_confluence_codebase.qualified_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["framework_language", "framework_library"],
            ["framework.language", "framework.library"],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    codebase_qualified_name: Mapped[str] = mapped_column(primary_key=True)
    framework_language: Mapped[str] = mapped_column(primary_key=True)
    framework_library: Mapped[str] = mapped_column(primary_key=True)

    codebase: Mapped[UnoplatCodeConfluenceCodebase] = relationship(
        back_populates="frameworks"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/relational_models/unoplat_code_confluence.py#L181-L236` — `class UnoplatCodeConfluenceFileFrameworkFeature(SQLBase):
    """Join table linking files to framework features with span metadata."""

    __tablename__ = "code_confluence_file_framework_feature"
    __table_args__ = (
        ForeignKeyConstraint(
            ["file_path"],
            ["code_confluence_file.file_path"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "feature_language",
                "feature_library",
                "feature_capability_key",
                "feature_operation_key",
            ],
            [
                "framework_feature.language",
                "framework_feature.library",
                "framework_feature.capability_key",
                "framework_feature.operation_key",
            ],
            ondelete="CASCADE",
        ),
        {"extend_existing": True},
    )

    file_path: Mapped[str] = mapped_column(primary_key=True)
    feature_language: Mapped[str] = mapped_column(primary_key=True)
    feature_library: Mapped[str] = mapped_column(primary_key=True)
    feature_capability_key: Mapped[str] = mapped_column(primary_key=True)
    feature_operation_key: Mapped[str] = mapped_column(primary_key=True)
    start_line: Mapped[int] = mapped_column(primary_key=True)
    end_line: Mapped[int] = mapped_column(primary_key=True)
    match_text: Mapped[Optional[str]] = mapped_column(Text, default=None)
    match_confidence: Mapped[float] = mapped_column(default=1.0)
    validation_status: Mapped[str] = mapped_column(
        default=ValidationStatus.COMPLETED.value,
    )
    evidence_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
    )

    @property
    def feature_key(self) -> str:
        """Return the dotted convenience key derived from structured identity."""
        return _compose_feature_key(
            self.feature_capability_key,
            self.feature_operation_key,
        )

    file: Mapped[UnoplatCodeConfluenceFile] = relationship(
        back_populates="framework_features"
    )`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L42-L76` — `class Repository(SQLBase):
    """SQLModel for repository table in code_confluence schema."""

    __tablename__ = "repository"

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_provider: Mapped[ProviderKey] = mapped_column(
        SQLEnum(ProviderKey, name="repository_provider_type", native_enum=False),
        default=ProviderKey.GITHUB_OPEN,
        nullable=False,
        comment="Provider key for this repository (e.g., GITHUB_OPEN, GITHUB_ENTERPRISE, GITLAB_CE, GITLAB_ENTERPRISE)",
    )

    # Relationships - will be populated after class definitions
    workflow_runs: Mapped[List["RepositoryWorkflowRun"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    configs: Mapped[List["CodebaseConfig"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    agent_md_snapshot: Mapped[Optional["RepositoryAgentMdSnapshot"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L79-L115` — `class CodebaseConfig(SQLBase):
    """SQLModel for codebase_config table in code_confluence schema."""

    __tablename__ = "codebase_config"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, comment="Path to codebase folder relative to repo root"
    )
    root_packages: Mapped[Optional[List[str]]] = mapped_column(
        JSONB, default=None, comment="List of root packages within the codebase folder"
    )
    programming_language_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Language-specific metadata for this codebase like programming language, package manager etc",
    )

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="configs")
    workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="codebase_config",
        viewonly=True,
        overlaps="repository_workflow_run,workflow_runs",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L118-L194` — `class RepositoryWorkflowRun(SQLBase):
    """SQLModel for repository_workflow_run table in code_confluence schema."""

    __tablename__ = "repository_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING','ERROR','CANCELLED')",
            name="status_check",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True, comment="The run ID of the repository workflow"
    )
    repository_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the repository workflow"
    )
    operation: Mapped[RepositoryWorkflowOperation] = mapped_column(
        SQLEnum(
            RepositoryWorkflowOperation,
            name="repository_workflow_operation_type",
            native_enum=False,
        ),
        default=RepositoryWorkflowOperation.INGESTION,
        nullable=False,
        comment="Operation this workflow run performs (e.g., INGESTION, AGENTS_GENERATION, AGENT_MD_UPDATE)",
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED.",
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None, comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this repository workflow run",
    )
    feedback_issue_url: Mapped[Optional[str]] = mapped_column(
        String,
        default=None,
        nullable=True,
        comment="GitHub issue URL for user feedback on agent generation",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the workflow run started",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed",
    )

    # Relationships
    repository: Mapped[Repository] = relationship(back_populates="workflow_runs")
    codebase_workflow_runs: Mapped[List["CodebaseWorkflowRun"]] = relationship(
        back_populates="repository_workflow_run",
        viewonly=True,
        overlaps="codebase_config,workflow_runs",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L197-L277` — `class CodebaseWorkflowRun(SQLBase):
    """SQLModel for codebase_workflow_run table in code_confluence schema."""

    __tablename__ = "codebase_workflow_run"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED','RUNNING','FAILED','TIMED_OUT','COMPLETED','RETRYING','ERROR','CANCELLED')",
            name="codebase_status_check",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "codebase_folder"],
            [
                "codebase_config.repository_name",
                "codebase_config.repository_owner_name",
                "codebase_config.codebase_folder",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name", "repository_workflow_run_id"],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    codebase_folder: Mapped[str] = mapped_column(
        primary_key=True, comment="FK to codebase_config - path to codebase folder"
    )
    codebase_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Unique identifier for this specific run of the codebase workflow",
    )
    codebase_workflow_id: Mapped[str] = mapped_column(
        comment="The ID of the codebase workflow"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        comment="Link back to parent repository workflow run"
    )
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Status of the workflow run. One of: SUBMITTED, RUNNING, FAILED, TIMED_OUT, COMPLETED, RETRYING, ERROR, CANCELLED.",
    )
    error_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB, default=None, comment="Error report if the workflow run failed"
    )
    issue_tracking: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=None,
        comment="GitHub issue tracking info for this codebase workflow run",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when the workflow run started",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp when the workflow run completed",
    )

    # Relationships
    codebase_config: Mapped[CodebaseConfig] = relationship(
        back_populates="workflow_runs"
    )
    repository_workflow_run: Mapped[RepositoryWorkflowRun] = relationship(
        back_populates="codebase_workflow_runs"
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L280-L373` — `class RepositoryAgentCodebaseProgress(SQLBase):
    """Live per-codebase progress row for repository agent execution."""

    __tablename__ = "repository_agent_codebase_progress"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "repository_name",
                "repository_owner_name",
                "repository_workflow_run_id",
            ],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
        Index(
            "ix_repository_agent_codebase_progress_run",
            "repository_owner_name",
            "repository_name",
            "repository_workflow_run_id",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The run ID of the repository workflow this progress row belongs to",
    )
    codebase_name: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Codebase identifier/path relative to the repository root",
    )
    next_event_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="Next monotonic event ID to allocate for this codebase stream",
    )
    latest_event_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        default=None,
        comment="Most recently allocated event ID for this codebase stream",
    )
    event_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of persisted events for this codebase stream",
    )
    progress: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0,
        comment="Progress percentage for this codebase stream",
    )
    completed_namespaces: Mapped[List[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        comment="Sorted list of completion namespaces already finished for this codebase",
    )
    latest_event_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp of the most recent persisted event for this codebase",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the row was first inserted",
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the row was last updated",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L376-L488` — `class RepositoryAgentEvent(SQLBase):
    """Durable append-only repository agent event history row."""

    __tablename__ = "repository_agent_event"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "repository_name",
                "repository_owner_name",
                "repository_workflow_run_id",
            ],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "repository_name",
                "repository_owner_name",
                "repository_workflow_run_id",
                "codebase_name",
            ],
            [
                "repository_agent_codebase_progress.repository_name",
                "repository_agent_codebase_progress.repository_owner_name",
                "repository_agent_codebase_progress.repository_workflow_run_id",
                "repository_agent_codebase_progress.codebase_name",
            ],
            ondelete="CASCADE",
        ),
        Index(
            "ix_repository_agent_event_run_codebase_order",
            "repository_owner_name",
            "repository_name",
            "repository_workflow_run_id",
            "codebase_name",
            "event_id",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The run ID of the repository workflow this event belongs to",
    )
    codebase_name: Mapped[str] = mapped_column(
        primary_key=True,
        comment="Codebase identifier/path relative to the repository root",
    )
    event_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        comment="Monotonic event ID within a repository workflow run and codebase",
    )
    event: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Event namespace or agent name that emitted this row",
    )
    phase: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Lifecycle phase for the event (tool.call, tool.result, result)",
    )
    message: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
        comment="Human-readable event message when present",
    )
    tool_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
        comment="Tool name for tool-related events when present",
    )
    tool_call_id: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
        comment="Tool call identifier when present",
    )
    tool_args: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Structured tool arguments when available",
    )
    tool_result_content: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        default=None,
        comment="Captured tool result content when available",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the event row was inserted",
    )`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/repo_models.py#L491-L570` — `class RepositoryAgentMdSnapshot(SQLBase):
    """SQLModel for repository_agent_md_snapshot table in code_confluence schema."""

    __tablename__ = "repository_agent_md_snapshot"
    __table_args__ = (
        ForeignKeyConstraint(
            ["repository_name", "repository_owner_name"],
            ["repository.repository_name", "repository.repository_owner_name"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "repository_name",
                "repository_owner_name",
                "repository_workflow_run_id",
            ],
            [
                "repository_workflow_run.repository_name",
                "repository_workflow_run.repository_owner_name",
                "repository_workflow_run.repository_workflow_run_id",
            ],
            ondelete="CASCADE",
        ),
    )

    repository_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository"
    )
    repository_owner_name: Mapped[str] = mapped_column(
        primary_key=True, comment="The name of the repository owner"
    )
    repository_workflow_run_id: Mapped[str] = mapped_column(
        primary_key=True,
        comment="The run ID of the repository workflow this snapshot belongs to",
    )
    agent_md_output: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Complete final payload from agent execution containing per-codebase agent data",
    )
    statistics: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Aggregated usage and pricing statistics for the latest agent workflow",
    )
    overall_progress: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        default=None,
        comment="Cached overall progress percentage for fast polling",
    )
    latest_event_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        comment="Timestamp of the most recent appended event for this run",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Timestamp when the row was first inserted",
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the latest overwrite occurred",
    )
    pr_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        default=None,
        comment="Persisted PR metadata from manual AGENTS.md PR creation/update",
    )

    # Relationships
    repository: Mapped["Repository"] = relationship(back_populates="agent_md_snapshot")`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py#L13-L47` — `class ParentWorkflowDbActivityEnvelope(BaseModel):
    """Envelope for parent workflow status DB updates."""

    repository_name: str = Field(..., description="The name of the repository")
    repository_owner_name: str = Field(
        ..., description="The name of the repository owner"
    )
    workflow_id: Optional[str] = Field(
        default=None, description="Temporal workflow ID"
    )
    workflow_run_id: str = Field(..., description="Unique workflow run ID")
    status: str = Field(..., description="JobStatus value")
    operation: RepositoryWorkflowOperation = Field(
        default=RepositoryWorkflowOperation.INGESTION,
        description="Operation type for this workflow run",
    )
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error details if workflow failed"
    )
    trace_id: Optional[str] = Field(
        default=None, description="Trace ID for distributed tracing"
    )
    repository_metadata: Optional[List[CodebaseConfig]] = Field(
        default=None, description="List of codebase configurations for the repository"
    )
    provider_key: ProviderKey = Field(
        default=ProviderKey.GITHUB_OPEN,
        description="Provider key for credential and repository provider lookup",
    )
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_envelopes.py#L50-L75` — `class CodebaseWorkflowDbActivityEnvelope(BaseModel):
    """Envelope for codebase workflow status DB updates."""

    repository_name: str = Field(..., description="The name of the repository")
    repository_owner_name: str = Field(
        ..., description="The name of the repository owner"
    )
    codebase_folder: str = Field(
        ..., description="Path to codebase folder (same as codebase_name for POC)"
    )
    repository_workflow_run_id: str = Field(
        ..., description="Parent repository workflow run ID"
    )
    codebase_workflow_id: str = Field(..., description="Temporal workflow ID")
    codebase_workflow_run_id: str = Field(..., description="Unique codebase run ID")
    status: str = Field(..., description="JobStatus value")
    error_report: Optional[ErrorReport] = Field(
        default=None, description="Error details if workflow failed"
    )
    trace_id: str = Field(default="", description="Trace ID for distributed tracing")
    model_config = ConfigDict(extra="allow")

    @property
    def extras(self) -> dict[str, Any]:
        """Return any extra fields passed to the model (required for Temporal)."""
        return dict(self.model_extra or {})`

### `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_models.py`
- `/opt/unoplat/repositories/unoplat-code-confluence/unoplat-code-confluence-commons/src/unoplat_code_confluence_commons/workflow_models.py#L22-L31` — `class ErrorReport(BaseModel):
    """Detailed error report capturing context of workflow failure."""

    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(
        default=None, description="Stack trace of the error, if available"
    )
    metadata: Optional[dict[str, object]] = Field(
        default=None, description="Additional error metadata"
    )`
