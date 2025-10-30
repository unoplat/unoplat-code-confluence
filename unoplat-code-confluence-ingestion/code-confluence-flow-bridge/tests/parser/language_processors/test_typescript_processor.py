# Standard Library
from pathlib import Path

# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from src.code_confluence_flow_bridge.parser.language_processors.typescript_processor import (
    TypeScriptLanguageProcessor,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)


@pytest.fixture()
def typescript_sample_path() -> Path:
    """Fixture pointing to the shared TypeScript sample file."""
    return (
        Path(__file__).resolve().parents[2]
        / "test_data"
        / "typescript_files"
        / "typescript_ast_sample.ts"
    )


@pytest.fixture()
def typescript_metadata() -> ProgrammingLanguageMetadata:
    """Minimal programming language metadata for TypeScript projects."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.TYPESCRIPT,
        package_manager=PackageManagerType.NPM,
        language_version=">=5.0.0",
        manifest_path="package.json",
    )


@pytest.fixture()
def typescript_context(
    typescript_metadata: ProgrammingLanguageMetadata, tmp_path: Path
) -> LanguageProcessorContext:
    """Construct a language processor context suitable for unit tests."""
    return LanguageProcessorContext(
        codebase_name="unit-test-typescript",
        codebase_path=tmp_path,
        root_packages=[],
        programming_language_metadata=typescript_metadata,
        env_config=EnvironmentSettings(),
        framework_detection_service=None,
        concurrency_limit=1,
        increment_files_processed=lambda _: None,
    )


def test_supported_extensions_excludes_tsx(
    typescript_context: LanguageProcessorContext,
) -> None:
    """Ensure TypeScript processor only registers `.ts` files in v1."""
    processor = TypeScriptLanguageProcessor(typescript_context)
    assert ".ts" in processor.supported_extensions
    assert ".tsx" not in processor.supported_extensions


def test_declaration_files_are_ignored(
    typescript_context: LanguageProcessorContext, tmp_path: Path
) -> None:
    """`.d.ts` declaration files should be skipped."""
    processor = TypeScriptLanguageProcessor(typescript_context)
    declaration_path = tmp_path / "types.d.ts"
    declaration_path.write_text("// type definitions")
    assert processor.should_ignore(declaration_path)


@pytest.mark.asyncio
async def test_extract_file_data_detects_data_models(
    typescript_context: LanguageProcessorContext,
    typescript_sample_path: Path,
) -> None:
    """TypeScript processor should surface interface/type ranges from sample."""
    processor = TypeScriptLanguageProcessor(typescript_context)

    file_data = await processor.extract_file_data(str(typescript_sample_path))

    assert file_data is not None
    assert file_data.file_path.endswith("typescript_ast_sample.ts")
    assert file_data.has_data_model is True

    positions = file_data.data_model_positions.positions
    # Expect well-known interfaces from the sample file
    assert positions.get("ApiResponse") == (70, 73)
    assert positions.get("ApiError") == (75, 80)

    # Imports are intentionally skipped in v1
    assert file_data.imports is None
