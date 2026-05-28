"""Shared tree-sitter source context construction primitives."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List

from pydantic import BaseModel, ConfigDict
import tree_sitter
from tree_sitter_language_pack import (
    ProcessConfig,
    SupportedLanguage,
    get_parser,
    process,
)

if TYPE_CHECKING:
    from tree_sitter_language_pack import ProcessResult


class BaseSourceContext(BaseModel):
    """Base Pydantic model for parsed source contexts."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    source_bytes: bytes
    tree: tree_sitter.Tree
    root_node: tree_sitter.Node
    imports: List[str]
    import_aliases: Dict[str, str]


class ImportAliasStrategy(ABC):
    """Strategy for resolving raw import statements into import aliases."""

    @abstractmethod
    def build_import_aliases(self, imports: List[str]) -> Dict[str, str]:
        """Build fully-qualified import path -> local alias mappings."""
        raise NotImplementedError


class LanguagePackImportExtractor(BaseModel):
    """Extract raw import statements using tree-sitter-language-pack intelligence."""

    model_config = ConfigDict(frozen=True)

    language_name: str

    def extract_imports(self, source_bytes: bytes) -> List[str]:
        """Return raw import statement strings for downstream alias extraction."""
        source_text = source_bytes.decode("utf-8", errors="ignore")
        result: ProcessResult = process(
            source_text,
            ProcessConfig(
                language=self.language_name,
                structure=False,
                imports=True,
                exports=False,
                comments=False,
                docstrings=False,
                symbols=False,
                diagnostics=False,
            ),
        )

        imports: List[str] = []
        for import_info in result.get("imports", []):
            span = import_info["span"]
            imports.append(
                source_bytes[span["start_byte"] : span["end_byte"]].decode(
                    "utf-8", errors="ignore"
                )
            )

        return imports


class SourceContextBuilder(BaseModel):
    """Template Method for creating fully-populated source contexts."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    language_name: SupportedLanguage
    import_extractor: LanguagePackImportExtractor
    alias_strategy: ImportAliasStrategy

    def from_bytes(self, source_bytes: bytes) -> BaseSourceContext:
        """Parse once, extract imports, resolve aliases, and build a context."""
        tree = get_parser(self.language_name).parse(source_bytes)
        root_node = tree.root_node
        imports = self.import_extractor.extract_imports(source_bytes)
        import_aliases = self.alias_strategy.build_import_aliases(imports)
        return BaseSourceContext(
            source_bytes=source_bytes,
            tree=tree,
            root_node=root_node,
            imports=imports,
            import_aliases=import_aliases,
        )
