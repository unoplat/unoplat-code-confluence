"""
Integration tests for framework detection using PostgreSQL database fixtures.

This module tests the simplified framework detection implementation that uses
PostgreSQL to store framework definitions and the new SimplifiedPythonDetector
that works with structural signatures instead of re-parsing source code.
"""

import asyncio
from pathlib import Path
from typing import Dict, List

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from src.code_confluence_flow_bridge.engine.python.python_framework_detection_service import (
    PythonFrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.configuration.settings import EnvironmentSettings
from src.code_confluence_flow_bridge.parser.tree_sitter_structural_signature import (
    TreeSitterStructuralSignatureExtractor,
)
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
from src.code_confluence_flow_bridge.engine.python.import_alias_extractor import (
    build_import_aliases,
    extract_imports_from_source,
)


@pytest.mark.integration
class TestFrameworkDetectionWithPostgres:
    """Integration tests for framework detection using PostgreSQL database."""

    def get_framework_loader(self) -> FrameworkDefinitionLoader:
        """Create framework definition loader with test environment."""
        # Use the actual framework definitions directory with absolute path
        framework_definitions_dir = Path(__file__).parent.parent.parent / "framework-definitions"
        
        # Create environment settings with test database connection details
        env_settings = EnvironmentSettings(
            NEO4J_HOST="localhost",
            NEO4J_PORT=7687,
            NEO4J_USERNAME="neo4j",
            NEO4J_PASSWORD=SecretStr("password"),
            FRAMEWORK_DEFINITIONS_PATH=str(framework_definitions_dir.resolve())
        )
        return FrameworkDefinitionLoader(env_settings)

    def get_detection_service(self) -> PythonFrameworkDetectionService:
        """Create Python framework detection service."""
        return PythonFrameworkDetectionService()

    def get_structural_extractor(self) -> TreeSitterStructuralSignatureExtractor:
        """Create Tree-sitter structural signature extractor."""
        return TreeSitterStructuralSignatureExtractor("python")

    @pytest.mark.asyncio(loop_scope="session")
    async def test_load_framework_definitions(self, test_client: TestClient, postgres_session):
        """Test loading framework definitions into PostgreSQL database."""
        framework_loader = self.get_framework_loader()
        
        # Load framework definitions into database
        session = postgres_session
        result = await framework_loader.load_framework_definitions_at_startup(session)
        
        # Verify definitions were loaded
        assert isinstance(result, dict)
        assert result.get("frameworks_count", 0) > 0
        assert result.get("features_count", 0) > 0
        assert result.get("absolute_paths_count", 0) > 0
        
        # Should have FastAPI, Pydantic, SQLAlchemy, SQLModel frameworks
        assert result["frameworks_count"] >= 4
        
        # FastAPI should have multiple features (http_endpoint, dependency_injection, etc.)
        assert result["features_count"] >= 8

    @pytest.mark.asyncio(loop_scope="session")
    async def test_detect_fastapi_endpoints_main_py(self, test_client: TestClient, postgres_session):
        """Test FastAPI endpoint detection using the real main.py file."""
        framework_loader = self.get_framework_loader()
        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()
        
        # Load framework definitions first
        session = postgres_session
        await framework_loader.load_framework_definitions_at_startup(session)
        
        # Read the actual main.py file
        main_py_path = Path(__file__).parent.parent.parent / "src" / "code_confluence_flow_bridge" / "main.py"
        assert main_py_path.exists(), f"main.py not found at {main_py_path}"
        
        source_code = main_py_path.read_text(encoding="utf-8")
        
        # Extract structural signature
        structural_signature = await asyncio.to_thread(
            structural_extractor.extract_structural_signature, 
            str(main_py_path)
        )
        # Run framework detection
        detections = await detection_service.detect_features(
            source_code=source_code,
            imports=extract_imports_from_source(source_code),
            structural_signature=structural_signature,
            programming_language="python"
        )
        
        # Verify FastAPI endpoints were detected
        fastapi_detections = [d for d in detections if d.feature_key == "http_endpoint"]
        assert len(fastapi_detections) > 0, "No FastAPI endpoints detected in main.py"
        
        # Check that we found expected endpoints
        endpoint_texts = [d.match_text for d in fastapi_detections]
        
        # Should find some of the known endpoints in main.py
        assert any("/repos" in text for text in endpoint_texts), "Expected /repos endpoint"
        assert any("get" in text.lower() for text in endpoint_texts), "Expected GET endpoints"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_instance_variable_binding(self, test_client: TestClient, postgres_session):
        """Test detection of instance variable binding patterns like self.app = FastAPI()."""
        framework_loader = self.get_framework_loader()
        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()
        
        # Load framework definitions
        session = postgres_session
        await framework_loader.load_framework_definitions_at_startup(session)
        
        # Test source code with instance variable pattern
        test_source = '''
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
'''
        
        # Create a temporary file for extraction
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_source)
            temp_path = f.name
        
        try:
            # Extract structural signature
            structural_signature = await asyncio.to_thread(
                structural_extractor.extract_structural_signature,
                temp_path
            )
            
            # Extract imports
            import_strings = extract_imports_from_source(test_source)
            
            
            # Run framework detection
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python"
            )
            
            
            # Verify instance variable endpoints were detected
            fastapi_detections = [d for d in detections if d.feature_key == "http_endpoint"]
            assert len(fastapi_detections) >= 2, f"Expected at least 2 endpoints, got {len(fastapi_detections)}"
            
            # Check decorator patterns
            endpoint_texts = [d.match_text for d in fastapi_detections]
            assert any("@self.app.get" in text for text in endpoint_texts), "Expected @self.app.get pattern"
            assert any("@self.app.post" in text for text in endpoint_texts), "Expected @self.app.post pattern"
            
        finally:
            # Clean up temp file
            Path(temp_path).unlink()

    @pytest.mark.asyncio(loop_scope="session")
    async def test_detect_pydantic_models(self, test_client: TestClient, postgres_session):
        """Test Pydantic model detection."""
        framework_loader = self.get_framework_loader()
        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()
        
        # Load framework definitions
        session = postgres_session
        await framework_loader.load_framework_definitions_at_startup(session)
        
        test_source = '''
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
'''
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_source)
            temp_path = f.name
        
        try:
            structural_signature = await asyncio.to_thread(
                structural_extractor.extract_structural_signature,
                temp_path
            )
            
            import_strings = extract_imports_from_source(test_source)
            
            
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python"
            )
            
            # Look for Pydantic model detections
            pydantic_detections = [d for d in detections if "data_model" in d.feature_key.lower()]
            assert len(pydantic_detections) >= 2, f"Expected at least 2 data_model models, got {len(pydantic_detections)}"
            
        finally:
            Path(temp_path).unlink()


    @pytest.mark.asyncio(loop_scope="session")
    async def test_multi_framework_detection(self, test_client: TestClient, postgres_session):
        """Test detection of multiple frameworks in one file."""
        framework_loader = self.get_framework_loader()
        detection_service = self.get_detection_service()
        structural_extractor = self.get_structural_extractor()
        
        # Load framework definitions
        session = postgres_session
        await framework_loader.load_framework_definitions_at_startup(session)
        
        test_source = '''
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
'''
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_source)
            temp_path = f.name
        
        try:
            structural_signature = await asyncio.to_thread(
                structural_extractor.extract_structural_signature,
                temp_path
            )
            
            import_strings = extract_imports_from_source(test_source)
            
            
            detections = await detection_service.detect_features(
                source_code=test_source,
                imports=import_strings,
                structural_signature=structural_signature,
                programming_language="python"
            )
            
            # Group detections by framework
            framework_features = {}
            for detection in detections:
                framework_features.setdefault(detection.feature_key, []).append(detection)
            
            # Should detect FastAPI endpoints
            assert "http_endpoint" in framework_features, "FastAPI endpoints not detected"
            assert len(framework_features["http_endpoint"]) >= 2, "Expected multiple FastAPI endpoints"
            
            # Should detect dependency injection
            if "dependency_injection" in framework_features:
                assert len(framework_features["dependency_injection"]) >= 1, "Expected dependency injection"
            
            # Should detect SQLModel models (inheritance detection)
            sql_model_detections = [d for d in detections if "sqlmodel_base" in d.feature_key.lower()]
            assert len(sql_model_detections) == 1, "Expected model detections"
            
            pydantic_detections = [d for d in detections if "data_model" in d.feature_key.lower()]
            assert len(pydantic_detections) == 1, "Expected model detections"
            
            
            
        finally:
            Path(temp_path).unlink()

    