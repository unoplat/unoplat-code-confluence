"""
Integration tests for framework detection using PostgreSQL database fixtures.

This module tests the simplified framework detection implementation that uses
PostgreSQL to store framework definitions and the new SimplifiedPythonDetector
that works with structural signatures instead of re-parsing source code.
"""

from pathlib import Path
import tempfile

from fastapi.testclient import TestClient
import pytest
from src.code_confluence_flow_bridge.engine.python.import_alias_extractor import (
    extract_imports_from_source,
)
from src.code_confluence_flow_bridge.engine.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.parser.language_processors.python_processor import (
    build_python_extractor_config,
)
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterPythonStructuralSignatureExtractor,
)


@pytest.mark.integration
class TestFrameworkDetectionWithPostgres:
    """Integration tests for framework detection using PostgreSQL database."""

    def get_detection_service(self) -> PythonFrameworkDetectionService:
        """Create Python framework detection service."""
        return PythonFrameworkDetectionService()

    def get_structural_extractor(self) -> TreeSitterPythonStructuralSignatureExtractor:
        """Create Tree-sitter structural signature extractor."""
        config = build_python_extractor_config()
        return TreeSitterPythonStructuralSignatureExtractor(
            language_name="python", config=config
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_detect_fastapi_endpoints_main_py(self, test_client: TestClient):
        """Test FastAPI endpoint detection using the real main.py file."""

        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()

        # Load framework definitions first (wrap sync operation in asyncio.to_thread)

        # Read the actual main.py file
        main_py_path = (
            Path(__file__).parent.parent.parent
            / "src"
            / "code_confluence_flow_bridge"
            / "main.py"
        )
        assert main_py_path.exists(), f"main.py not found at {main_py_path}"

        source_code = main_py_path.read_text(encoding="utf-8")

        # Extract structural signature
        with open(main_py_path, "rb") as f:
            content = f.read()
        structural_signature = structural_extractor.extract_structural_signature(
            content
        )

        # Run framework detection (keep async business logic)
        detections = await detection_service.detect_features(
            source_code=source_code,
            imports=extract_imports_from_source(source_code),
            structural_signature=structural_signature,
            programming_language="python",
        )

        # Verify FastAPI endpoints were detected
        fastapi_detections = [d for d in detections if d.feature_key == "http_endpoint"]
        assert len(fastapi_detections) > 0, "No FastAPI endpoints detected in main.py"

        # Log line numbers for each detection
        print("\n=== FastAPI Endpoint Detection Line Numbers ===")
        for i, detection in enumerate(fastapi_detections):
            start_line = detection.start_line
            end_line = detection.end_line
            match_text = detection.match_text
            feature_key = detection.feature_key
            print(f"Detection {i}: {feature_key}")
            print(f"  Match text: {match_text}")
            print(f"  Line range: {start_line}-{end_line}")
            print(f"  Span: {end_line - start_line + 1} lines")

        # Check that we found expected endpoints
        endpoint_texts = [d.match_text for d in fastapi_detections]

        # Should find some of the known endpoints in main.py
        assert any("/repos" in text for text in endpoint_texts), (
            "Expected /repos endpoint"
        )
        assert any("get" in text.lower() for text in endpoint_texts), (
            "Expected GET endpoints"
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_instance_variable_binding(self, test_client: TestClient):
        """Test detection of instance variable binding patterns like self.app = FastAPI()."""

        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()

        # Test source code with instance variable pattern
        test_source = """
from fastapi import FastAPI

class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/health")
        def health_check():
            return {"status": "healthy"}
        
        @self.app.post("/data")
        def create_data():
            return {"created": True}
"""

        # Create a temporary file for extraction
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_source)
            temp_path = f.name

        try:
            # Extract structural signature
            with open(temp_path, "rb") as f:
                content = f.read()
            structural_signature = structural_extractor.extract_structural_signature(
                content
            )

            # Extract imports
            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python",
            )

            # Verify instance variable endpoints were detected
            fastapi_detections = [
                d for d in detections if d.feature_key == "http_endpoint"
            ]
            assert len(fastapi_detections) >= 2, (
                f"Expected at least 2 endpoints, got {len(fastapi_detections)}"
            )

            # Log line numbers for instance variable binding detections
            print("\n=== Instance Variable Binding Detection Line Numbers ===")
            for i, detection in enumerate(fastapi_detections):
                start_line = detection.start_line
                end_line = detection.end_line
                match_text = detection.match_text
                feature_key = detection.feature_key
                print(f"Detection {i}: {feature_key}")
                print(f"  Match text: {match_text}")
                print(f"  Line range: {start_line}-{end_line}")
                print(f"  Span: {end_line - start_line + 1} lines")

            # Check decorator patterns
            endpoint_texts = [d.match_text for d in fastapi_detections]
            assert any("@self.app.get" in text for text in endpoint_texts), (
                "Expected @self.app.get pattern"
            )
            assert any("@self.app.post" in text for text in endpoint_texts), (
                "Expected @self.app.post pattern"
            )

        finally:
            # Clean up temp file
            Path(temp_path).unlink()

    @pytest.mark.asyncio(loop_scope="session")
    async def test_detect_pydantic_models(self, test_client: TestClient):
        """Test Pydantic model detection."""

        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()

        test_source = """
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

class Product(BaseModel):
    sku: str
    price: float
    description: str
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_source)
            temp_path = f.name

        try:
            with open(temp_path, "rb") as f:
                content = f.read()
            structural_signature = structural_extractor.extract_structural_signature(
                content
            )

            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python",
            )

            # Look for Pydantic model detections
            pydantic_detections = [
                d for d in detections if "data_model" in d.feature_key.lower()
            ]
            assert len(pydantic_detections) >= 2, (
                f"Expected at least 2 data_model models, got {len(pydantic_detections)}"
            )

            # Log line numbers for Pydantic model detections
            print("\n=== Pydantic Model Detection Line Numbers ===")
            for i, detection in enumerate(pydantic_detections):
                start_line = detection.start_line
                end_line = detection.end_line
                match_text = detection.match_text
                feature_key = detection.feature_key
                print(f"Detection {i}: {feature_key}")
                print(f"  Match text: {match_text}")
                print(f"  Line range: {start_line}-{end_line}")
                print(f"  Span: {end_line - start_line + 1} lines")

        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio(loop_scope="session")
    async def test_multi_framework_detection(self, test_client: TestClient):
        """Test detection of multiple frameworks in one file."""

        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()

        test_source = """
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlmodel import SQLModel, Field

app = FastAPI()

class UserModel(BaseModel):
    id: int
    name: str

class UserDB(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

def get_db():
    return "db"

@app.get("/users/{user_id}")
async def get_user(user_id: int, db=Depends(get_db)):
    return {"id": user_id}

@app.post("/users")
async def create_user(user: UserModel, db=Depends(get_db)):
    return {"created": True}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_source)
            temp_path = f.name

        try:
            with open(temp_path, "rb") as f:
                content = f.read()
            structural_signature = structural_extractor.extract_structural_signature(
                content
            )

            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python",
            )

            # Group detections by framework
            framework_features = {}
            for detection in detections:
                framework_features.setdefault(detection.feature_key, []).append(
                    detection
                )

            # Log line numbers for multi-framework detection
            print("\n=== Multi-Framework Detection Line Numbers ===")

            # FastAPI endpoints
            if "http_endpoint" in framework_features:
                print("\nFastAPI HTTP Endpoints:")
                for i, detection in enumerate(framework_features["http_endpoint"]):
                    start_line = detection.start_line
                    end_line = detection.end_line
                    match_text = detection.match_text
                    print(f"  [{i}] {match_text} | Lines: {start_line}-{end_line}")

            # Dependency injection
            if "dependency_injection" in framework_features:
                print("\nDependency Injection:")
                for i, detection in enumerate(
                    framework_features["dependency_injection"]
                ):
                    start_line = detection.start_line
                    end_line = detection.end_line
                    match_text = detection.match_text
                    print(f"  [{i}] {match_text} | Lines: {start_line}-{end_line}")

            # SQLModel models
            sql_model_detections = [
                d for d in detections if "db_data_model" in d.feature_key.lower()
            ]
            if sql_model_detections:
                print("\nSQLModel Models:")
                for i, detection in enumerate(sql_model_detections):
                    start_line = detection.start_line
                    end_line = detection.end_line
                    match_text = detection.match_text
                    print(f"  [{i}] {match_text} | Lines: {start_line}-{end_line}")

            # Pydantic models
            pydantic_detections = [
                d for d in detections if d.feature_key.lower() == "data_model"
            ]
            if pydantic_detections:
                print("\nPydantic Models:")
                for i, detection in enumerate(pydantic_detections):
                    start_line = detection.start_line
                    end_line = detection.end_line
                    match_text = detection.match_text
                    print(f"  [{i}] {match_text} | Lines: {start_line}-{end_line}")

            # Should detect FastAPI endpoints
            assert "http_endpoint" in framework_features, (
                "FastAPI endpoints not detected"
            )
            assert len(framework_features["http_endpoint"]) >= 2, (
                "Expected multiple FastAPI endpoints"
            )

            # Should detect dependency injection
            if "dependency_injection" in framework_features:
                assert len(framework_features["dependency_injection"]) >= 1, (
                    "Expected dependency injection"
                )

            # Should detect SQLModel models (inheritance detection)
            assert len(sql_model_detections) == 1, "Expected model detections"

            assert len(pydantic_detections) == 1, "Expected model detections"

        finally:
            Path(temp_path).unlink()
