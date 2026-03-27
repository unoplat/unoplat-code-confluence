"""Python-specific YAML rule configuration models."""

from pydantic import BaseModel, Field


class RuleSignatureConfig(BaseModel):
    """Typed YAML representation for a manager signature entry."""

    file: str | None = None
    contains: str | None = None
    contains_absence: list[str] | None = None
    glob: str | None = None


class RuleManagerConfig(BaseModel):
    """Typed YAML representation for a manager entry."""

    manager: str
    weight: int = 1
    signatures: list[str | RuleSignatureConfig] = Field(default_factory=list)
    workspace_field: str | None = None


class LanguageRulesConfig(BaseModel):
    """Typed YAML representation for the Python rules block."""

    ignores: list[str] = Field(default_factory=list)
    managers: list[RuleManagerConfig] = Field(default_factory=list)


class RulesFileConfig(BaseModel):
    """Typed YAML representation for the full rules file (Python section)."""

    python: LanguageRulesConfig = Field(default_factory=LanguageRulesConfig)
