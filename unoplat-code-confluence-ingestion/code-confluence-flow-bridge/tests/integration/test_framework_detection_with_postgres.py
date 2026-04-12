"""
Integration tests for framework detection using PostgreSQL database fixtures.

This module tests framework detection using PostgreSQL-backed definitions and
tree-sitter source analysis (structural signatures are not required).
"""

from pathlib import Path
import tempfile

from fastapi.testclient import TestClient
import pytest
from src.code_confluence_flow_bridge.engine.programming_language.python.import_alias_extractor import (
    extract_imports_from_source,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)


@pytest.mark.integration
class TestFrameworkDetectionWithPostgres:
    """Integration tests for framework detection using PostgreSQL database."""

    def get_detection_service(self) -> PythonFrameworkDetectionService:
        """Create Python framework detection service."""
        return PythonFrameworkDetectionService()

    @pytest.mark.asyncio(loop_scope="session")
    async def test_detect_fastapi_endpoints_across_router_modules(
        self, test_client: TestClient
    ):
        """Test FastAPI endpoint detection across main.py and extracted routers."""

        detection_service = self.get_detection_service()
        source_root = (
            Path(__file__).parent.parent.parent / "src" / "code_confluence_flow_bridge"
        )
        fastapi_files = [
            source_root / "main.py",
            source_root / "routers" / "providers" / "router.py",
            source_root / "routers" / "credentials" / "router.py",
            source_root / "routers" / "flags" / "router.py",
        ]

        endpoint_texts: list[str] = []
        source_texts: list[str] = []
        main_source_code = ""

        for fastapi_file in fastapi_files:
            assert fastapi_file.exists(), f"FastAPI file not found at {fastapi_file}"

            source_code = fastapi_file.read_text(encoding="utf-8")
            source_texts.append(source_code)
            if fastapi_file.name == "main.py":
                main_source_code = source_code

            detections = await detection_service.detect_features(
                source_code=source_code,
                imports=extract_imports_from_source(source_code),
                structural_signature=None,
                programming_language="python",
            )
            fastapi_detections = [
                detection
                for detection in detections
<<<<<<< HEAD
                if detection.feature_key.startswith("rest_api.")
=======
                if detection.feature_key == "http_endpoint"
>>>>>>> origin/main
            ]
            endpoint_texts.extend(
                detection.match_text for detection in fastapi_detections
            )

        assert endpoint_texts, "No FastAPI endpoints detected across router modules"
        assert "app.include_router(credentials_router)" in main_source_code
        assert "app.include_router(flags_router)" in main_source_code
        assert "app.include_router(providers_router)" in main_source_code

        all_source_code = "\n".join(source_texts)

        assert any("/start-ingestion" in text for text in endpoint_texts), (
            "Expected FastAPI detector to find at least one main.py endpoint"
        )
        assert '/repos", response_model=PaginatedResponse' in all_source_code, (
            "Expected /repos endpoint declaration"
        )
        assert '/ingest-token", status_code=201' in all_source_code, (
            "Expected /ingest-token endpoint"
        )
        assert '/flags/{flag_name}", status_code=200' in all_source_code, (
            "Expected /flags/{flag_name} endpoint"
        )
        assert any("@router.get" in source for source in source_texts), (
            "Expected extracted router GET endpoints"
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_instance_variable_binding(self, test_client: TestClient):
        """Test detection of instance variable binding patterns like self.app = FastAPI()."""

        detection_service = self.get_detection_service()
        # Test source code with instance variable pattern
        test_source = """
from fastapi import FastAPI

class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
<<<<<<< HEAD

=======
    
>>>>>>> origin/main
    def setup_routes(self):
        @self.app.get("/health")
        def health_check():
            return {"status": "healthy"}
<<<<<<< HEAD

=======
        
>>>>>>> origin/main
        @self.app.post("/data")
        def create_data():
            return {"created": True}
"""

        # Create a temporary file for extraction
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_source)
            temp_path = f.name

        try:
            # Extract imports
            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=None,
                programming_language="python",
            )

            # Verify instance variable endpoints were detected
            fastapi_detections = [
<<<<<<< HEAD
                d for d in detections if d.feature_key.startswith("rest_api.")
=======
                d for d in detections if d.feature_key == "http_endpoint"
>>>>>>> origin/main
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
            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=None,
                programming_language="python",
            )

            # Look for Pydantic model detections
            pydantic_detections = [
<<<<<<< HEAD
                d for d in detections if d.feature_key == "data_model.data_model"
=======
                d for d in detections if "data_model" in d.feature_key.lower()
>>>>>>> origin/main
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
            import_strings = extract_imports_from_source(test_source)

            # Run framework detection (keep async business logic)
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=None,
                programming_language="python",
            )

            # Group detections by framework
<<<<<<< HEAD
            framework_features: dict[str, list[object]] = {}
=======
            framework_features = {}
>>>>>>> origin/main
            for detection in detections:
                framework_features.setdefault(detection.feature_key, []).append(
                    detection
                )

            # Log line numbers for multi-framework detection
            print("\n=== Multi-Framework Detection Line Numbers ===")

            # FastAPI endpoints
<<<<<<< HEAD
            rest_api_detections = [
                d for d in detections if d.feature_key.startswith("rest_api.")
            ]
            if rest_api_detections:
                print("\nFastAPI REST API Endpoints:")
                for i, detection in enumerate(rest_api_detections):
=======
            if "http_endpoint" in framework_features:
                print("\nFastAPI HTTP Endpoints:")
                for i, detection in enumerate(framework_features["http_endpoint"]):
>>>>>>> origin/main
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
<<<<<<< HEAD
                d for d in detections if d.feature_key == "relational_database.db_data_model"
=======
                d for d in detections if "db_data_model" in d.feature_key.lower()
>>>>>>> origin/main
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
<<<<<<< HEAD
                d for d in detections if d.feature_key == "data_model.data_model"
=======
                d for d in detections if d.feature_key.lower() == "data_model"
>>>>>>> origin/main
            ]
            if pydantic_detections:
                print("\nPydantic Models:")
                for i, detection in enumerate(pydantic_detections):
                    start_line = detection.start_line
                    end_line = detection.end_line
                    match_text = detection.match_text
                    print(f"  [{i}] {match_text} | Lines: {start_line}-{end_line}")

            # Should detect FastAPI endpoints
<<<<<<< HEAD
            assert len(rest_api_detections) >= 2, (
                f"Expected at least 2 FastAPI endpoints, got {len(rest_api_detections)}"
=======
            assert "http_endpoint" in framework_features, (
                "FastAPI endpoints not detected"
            )
            assert len(framework_features["http_endpoint"]) >= 2, (
                "Expected multiple FastAPI endpoints"
>>>>>>> origin/main
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
