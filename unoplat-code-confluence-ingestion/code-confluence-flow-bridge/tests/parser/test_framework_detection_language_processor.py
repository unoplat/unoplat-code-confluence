"""End-to-end framework detection tests using PythonLanguageProcessor.

Tests verify custom_features_list is populated correctly when:
1. PythonLanguageProcessor has framework_detection_service injected
2. extract_file_data() is called on files with framework features
3. Results include proper feature_key, library, and line numbers

These tests cover all currently supported framework definitions:
- Pydantic (data_model via Inheritance)
- SQLAlchemy (db_data_model via Inheritance)
- SQLModel (db_data_model via Inheritance)
- FastAPI (http_endpoint via AnnotationLike)
"""

# Standard Library
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient
# Third Party
import pytest

# First Party
from src.code_confluence_flow_bridge.engine.programming_language.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)
from src.code_confluence_flow_bridge.parser.language_processors.python_processor import (
    PythonLanguageProcessor,
)
from unoplat_code_confluence_commons.programming_language_metadata import (
    PackageManagerType,
    ProgrammingLanguage,
    ProgrammingLanguageMetadata,
)

# Test data directory containing sample files with framework features
FRAMEWORK_SAMPLES_DIR = Path(__file__).parent.parent / "test_data" / "framework_samples"


@pytest.fixture
def python_language_metadata() -> ProgrammingLanguageMetadata:
    """Create Python language metadata for tests."""
    return ProgrammingLanguageMetadata(
        language=ProgrammingLanguage.PYTHON,
        package_manager=PackageManagerType.PIP,
    )


@pytest.fixture
def language_processor_context(
    test_client: TestClient,  # Ensures database is ready with framework definitions loaded
    python_language_metadata: ProgrammingLanguageMetadata,
) -> LanguageProcessorContext:
    """Create language processor context with framework detection enabled.

    The test_client fixture ensures:
    - Docker services are running (PostgreSQL, Temporal, Elasticsearch)
    - FRAMEWORK_DEFINITIONS_PATH is set
    - Framework definitions are loaded into PostgreSQL
    """
    env_config = EnvironmentSettings(EXTRACT_STRUCTURAL_SIGNATURES=False)

    return LanguageProcessorContext(
        codebase_name="test-codebase",
        codebase_path=FRAMEWORK_SAMPLES_DIR,
        root_packages=["test"],
        programming_language_metadata=python_language_metadata,
        env_config=env_config,
        framework_detection_service=PythonFrameworkDetectionService(),
        concurrency_limit=1,
        increment_files_processed=Mock(),
    )


@pytest.mark.integration
class TestFrameworkDetectionLanguageProcessor:
    """Integration tests for framework detection through PythonLanguageProcessor."""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_pydantic_data_model_detection_github_repo(
        self,
        language_processor_context: LanguageProcessorContext,
    ) -> None:
        """Test Pydantic BaseModel detection produces data_model feature spans.

        File: github_repo.py contains multiple Pydantic models:
        - GitHubOwner (BaseModel)
        - GitHubLicense (BaseModel)
        - GitHubRepo (BaseModel)
        - RepositoryRequestConfiguration (BaseModel)

        Expected: At least 3 pydantic data_model detections with valid line numbers.
        """
        processor = PythonLanguageProcessor(language_processor_context)

        file_path = str(
            FRAMEWORK_SAMPLES_DIR
            / "code_confluence_flow_bridge"
            / "models"
            / "github"
            / "github_repo.py"
        )

        result = await processor.extract_file_data(file_path)

        assert result is not None, "extract_file_data returned None"
        assert result.custom_features_list is not None, "custom_features_list is None"
        assert len(result.custom_features_list) > 0, "custom_features_list is empty"

        # Find pydantic data_model detections
        pydantic_detections = [
            d
            for d in result.custom_features_list
            if d.feature_key == "data_model" and d.library == "pydantic"
        ]

        # Log detections for debugging
        print("\n=== Pydantic Data Model Detections (github_repo.py) ===")
        for i, detection in enumerate(pydantic_detections):
            print(f"Detection {i}: {detection.feature_key} ({detection.library})")
            print(f"  Match text: {detection.match_text}")
            print(f"  Line range: {detection.start_line}-{detection.end_line}")

        # github_repo.py has GitHubOwner, GitHubLicense, GitHubRepo, etc.
        assert len(pydantic_detections) >= 3, (
            f"Expected at least 3 Pydantic models, got {len(pydantic_detections)}: "
            f"{[d.match_text for d in pydantic_detections]}"
        )

        # Verify detection has required fields with valid values
        for detection in pydantic_detections:
            assert detection.start_line > 0, "start_line should be positive"
            assert (
                detection.end_line >= detection.start_line
            ), "end_line should be >= start_line"
            assert detection.match_text is not None, "match_text should not be None"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_sqlalchemy_and_pydantic_mixed_detection(
        self,
        language_processor_context: LanguageProcessorContext,
    ) -> None:
        """Test SQLAlchemy db_data_model + Pydantic BaseModel in same file.

        File: github_app/models.py contains:
        - GithubAppManifestRecord (inherits from SQLBase - detected as db_data_model)
        - ManifestGenerationRequest (Pydantic BaseModel)
        - ManifestGenerationResponse (Pydantic BaseModel)

        Expected: Both SQLAlchemy db_data_model and Pydantic data_model detections.
        """
        processor = PythonLanguageProcessor(language_processor_context)

        file_path = str(
            FRAMEWORK_SAMPLES_DIR
            / "code_confluence_flow_bridge"
            / "github_app"
            / "models.py"
        )

        result = await processor.extract_file_data(file_path)

        assert result is not None, "extract_file_data returned None"
        assert result.custom_features_list is not None, "custom_features_list is None"

        # Find SQLAlchemy db_data_model detections (Inheritance-based)
        sqlalchemy_detections = [
            d
            for d in result.custom_features_list
            if d.feature_key == "db_data_model" and d.library == "sqlalchemy"
        ]

        # Log SQLAlchemy detections
        print("\n=== SQLAlchemy Detections (github_app/models.py) ===")
        for i, detection in enumerate(sqlalchemy_detections):
            print(f"Detection {i}: {detection.feature_key} ({detection.library})")
            print(f"  Match text: {detection.match_text}")
            print(f"  Line range: {detection.start_line}-{detection.end_line}")

        assert len(sqlalchemy_detections) >= 1, (
            f"Expected SQLAlchemy db_data_model detections, "
            f"got {len(sqlalchemy_detections)}"
        )

        # Also verify Pydantic detections (file has both)
        pydantic_detections = [
            d
            for d in result.custom_features_list
            if d.feature_key == "data_model" and d.library == "pydantic"
        ]

        # Log Pydantic detections
        print("\n=== Pydantic Detections (github_app/models.py) ===")
        for i, detection in enumerate(pydantic_detections):
            print(f"Detection {i}: {detection.feature_key} ({detection.library})")
            print(f"  Match text: {detection.match_text}")
            print(f"  Line range: {detection.start_line}-{detection.end_line}")

        assert len(pydantic_detections) >= 1, (
            f"Expected Pydantic model detections, got {len(pydantic_detections)}"
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_pure_sqlalchemy_relational_models(
        self,
        language_processor_context: LanguageProcessorContext,
    ) -> None:
        """Test pure SQLAlchemy file detects db_data_model via Inheritance.

        File: relational_models/unoplat_code_confluence.py contains:
        - Multiple SQLAlchemy models inheriting from SQLBase

        Expected: SQLAlchemy db_data_model detections for each model class.
        """
        processor = PythonLanguageProcessor(language_processor_context)

        file_path = str(
            FRAMEWORK_SAMPLES_DIR
            / "unoplat_code_confluence_commons"
            / "relational_models"
            / "unoplat_code_confluence.py"
        )

        result = await processor.extract_file_data(file_path)

        assert result is not None, "extract_file_data returned None"
        assert result.custom_features_list is not None, "custom_features_list is None"

        # Find SQLAlchemy db_data_model detections (Inheritance-based)
        sqlalchemy_detections = [
            d
            for d in result.custom_features_list
            if d.library == "sqlalchemy" and d.feature_key == "db_data_model"
        ]

        # Log SQLAlchemy detections
        print("\n=== SQLAlchemy Detections (unoplat_code_confluence.py) ===")
        for i, detection in enumerate(sqlalchemy_detections):
            print(f"Detection {i}: {detection.feature_key} ({detection.library})")
            print(f"  Match text: {detection.match_text}")
            print(f"  Line range: {detection.start_line}-{detection.end_line}")

        # File should have multiple SQLAlchemy model classes inheriting from SQLBase
        assert len(sqlalchemy_detections) >= 1, (
            f"Expected at least 1 SQLAlchemy db_data_model detection, "
            f"got {len(sqlalchemy_detections)}"
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_fastapi_http_endpoint_detection(
        self,
        language_processor_context: LanguageProcessorContext,
    ) -> None:
        """Test FastAPI http_endpoint detection through PythonLanguageProcessor.

        File: main.py contains FastAPI application with @app.get(), @app.post()
        decorators that should be detected as http_endpoint features.

        Expected: At least 1 FastAPI http_endpoint detection with valid line numbers.
        """
        processor = PythonLanguageProcessor(language_processor_context)

        file_path = str(
            FRAMEWORK_SAMPLES_DIR / "code_confluence_flow_bridge" / "main.py"
        )

        result = await processor.extract_file_data(file_path)

        assert result is not None, "extract_file_data returned None"
        assert result.custom_features_list is not None, "custom_features_list is None"

        # Find FastAPI http_endpoint detections
        fastapi_detections = [
            d
            for d in result.custom_features_list
            if d.feature_key == "http_endpoint" and d.library == "fastapi"
        ]

        # Log FastAPI detections
        print("\n=== FastAPI HTTP Endpoint Detections (main.py) ===")
        for i, detection in enumerate(fastapi_detections):
            print(f"Detection {i}: {detection.feature_key} ({detection.library})")
            print(f"  Match text: {detection.match_text}")
            print(f"  Line range: {detection.start_line}-{detection.end_line}")

        assert len(fastapi_detections) >= 1, (
            f"Expected at least 1 FastAPI endpoint, got {len(fastapi_detections)}"
        )

        # Verify line numbers are present
        for detection in fastapi_detections:
            assert detection.start_line > 0, "start_line should be positive"
            assert (
                detection.end_line >= detection.start_line
            ), "end_line should be >= start_line"
