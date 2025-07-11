"""
Unit tests for the new schema-driven custom grammar engine.

Tests the detection of FastAPI, Pydantic, SQLAlchemy and other frameworks
using the new engine architecture without external dependencies.
"""

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from src.code_confluence_flow_bridge.engine.custom_grammar_factory import (
    CustomGrammarFactory,
)
from src.code_confluence_flow_bridge.engine.integration import (
    create_feature_spec_from_db_model,
    detect_frameworks_from_schema,
)
from src.code_confluence_flow_bridge.engine.models import (
    DetectionResult,
    FeatureSpec,
    LocatorStrategy,
    TargetLevel,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    ProgrammingLanguage,
)


class TestSchemaDrivenEngine:
    """Test the new schema-driven detection engine."""

    @pytest.fixture
    def fastapi_schema(self) -> Dict[str, Any]:
        """Schema for FastAPI detection."""
        return {
            "fastapi": {
                "language": "python",
                "features": {
                    "endpoint": {
                        "target_level": "function",
                        "concept": "AnnotationLike",
                        "locator_strategy": "VariableBound",
                        "absolute_paths": [
                            "fastapi.FastAPI",
                            "fastapi.applications.FastAPI"
                        ],
                        "construct_query": {
                            "python": {
                                "method_regex": "(get|post|put|patch|delete|options|head)"
                            }
                        },
                        "description": "HTTP endpoint decorator"
                    }
                }
            }
        }

    @pytest.fixture
    def pydantic_schema(self) -> Dict[str, Any]:
        """Schema for Pydantic detection."""
        return {
            "pydantic": {
                "language": "python",
                "features": {
                    "model": {
                        "target_level": "class",
                        "concept": "Inheritance",
                        "locator_strategy": "Direct",
                        "absolute_paths": [
                            "pydantic.BaseModel",
                            "pydantic.main.BaseModel"
                        ],
                        "description": "Pydantic model class"
                    }
                }
            }
        }

    @pytest.fixture
    def complete_schema(self, fastapi_schema, pydantic_schema) -> Dict[str, Any]:
        """Combined schema with multiple frameworks."""
        schema = {}
        schema.update(fastapi_schema)
        schema.update(pydantic_schema)
        schema["sqlalchemy"] = {
            "language": "python",
            "features": {
                "declarative_model": {
                    "target_level": "class",
                    "concept": "Inheritance",
                    "locator_strategy": "VariableBound",
                    "absolute_paths": [
                        "sqlalchemy.ext.declarative.declarative_base",
                        "sqlalchemy.orm.declarative_base"
                    ],
                    "description": "SQLAlchemy declarative model"
                }
            }
        }
        return schema

    def test_basic_fastapi_detection(self, fastapi_schema):
        """Improved FastAPI endpoint detection using the real application module.

        This test now analyses the full FastAPI application defined in
        ``src/code_confluence_flow_bridge/main.py`` instead of the previous
        minimal example. The assertions have been updated to automatically
        calculate the expected number of HTTP endpoint decorators so that the
        test remains robust even if new routes are added or removed in the
        application code.
        """

        # Dynamically load the source code of the real FastAPI application
        from pathlib import Path
        import re

        source_path = (
            Path(__file__).resolve().parent.parent.parent
            / "src"
            / "code_confluence_flow_bridge"
            / "main.py"
        )

        source_code = source_path.read_text(encoding="utf-8")

        # Detect FastAPI endpoints using the schema-driven engine
        results = detect_frameworks_from_schema(source_code, fastapi_schema)

        # Basic presence checks
        assert "fastapi" in results
        assert "endpoint" in results["fastapi"]

        # Calculate the expected number of endpoint decorators in the source
        decorator_regex = re.compile(r"@app\.(get|post|put|patch|delete|options|head)\s*\(")
        expected_count = len(decorator_regex.findall(source_code))

        # Ensure the engine detected exactly the expected number of endpoints
        assert len(results["fastapi"]["endpoint"]) == expected_count

        # Additional sanity check – confirm detection of a known route
        detections = results["fastapi"]["endpoint"]
        decorators = [d["match_text"] for d in detections]
        assert any("/ingest-token" in d or "/repos" in d for d in decorators)

    def test_pydantic_model_detection(self, pydantic_schema):
        """Test Pydantic BaseModel detection."""
        source_code = '''
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

class Product(BaseModel):
    sku: str
    price: float
'''
        results = detect_frameworks_from_schema(source_code, pydantic_schema)
        
        assert "pydantic" in results
        assert "model" in results["pydantic"]
        assert len(results["pydantic"]["model"]) == 2
        
        # Check class names
        detections = results["pydantic"]["model"]
        class_names = [d["match_text"] for d in detections]
        assert any("class User(BaseModel)" in c for c in class_names)
        assert any("class Product(BaseModel)" in c for c in class_names)

    def test_multi_framework_detection(self, complete_schema):
        """Test detection of multiple frameworks in one file."""
        source_code = '''
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()
Base = declarative_base()

class User(BaseModel):
    id: int
    name: str

class UserDB(Base):
    __tablename__ = 'users'

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id}
'''
        results = detect_frameworks_from_schema(source_code, complete_schema)
        
        # Verify all frameworks detected
        assert "fastapi" in results
        assert "pydantic" in results
        assert "sqlalchemy" in results
        
        # Verify counts
        assert len(results["fastapi"]["endpoint"]) >= 1
        assert len(results["pydantic"]["model"]) == 1
        assert "declarative_model" in results["sqlalchemy"]
        assert len(results["sqlalchemy"]["declarative_model"]) >= 1

    def test_import_alias_handling(self, fastapi_schema):
        """Test detection with various import aliases."""
        source_code = '''
import fastapi as fp
from fastapi import FastAPI as WebAPI
from fastapi.applications import FastAPI as AppFastAPI

api1 = fp.FastAPI()
api2 = WebAPI()
api3 = AppFastAPI()

@api1.get("/v1")
def v1_endpoint():
    return {"version": 1}

@api2.post("/v2")
def v2_endpoint():
    return {"version": 2}

@api3.put("/v3")
def v3_endpoint():
    return {"version": 3}
'''
        results = detect_frameworks_from_schema(source_code, fastapi_schema)
        
        assert "fastapi" in results
        assert "endpoint" in results["fastapi"]
        assert len(results["fastapi"]["endpoint"]) == 3

    def test_member_assignment(self, fastapi_schema):
        """Test detection with member assignments (self.app)."""
        source_code = '''
from fastapi import FastAPI

class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.get("/health")
        def health_check():
            return {"status": "healthy"}
'''
        results = detect_frameworks_from_schema(source_code, fastapi_schema)
        
        assert "fastapi" in results
        assert "endpoint" in results["fastapi"]
        assert len(results["fastapi"]["endpoint"]) >= 1

    def test_nested_imports(self, complete_schema):
        """Test detection with nested module imports."""
        source_code = '''
import fastapi
from pydantic import main
import sqlalchemy.orm

app = fastapi.FastAPI()
Base = sqlalchemy.orm.declarative_base()

class User(main.BaseModel):
    id: int

@app.get("/test")
def test():
    return {}
'''
        results = detect_frameworks_from_schema(source_code, complete_schema)
        
        assert "fastapi" in results
        assert "pydantic" in results
        assert "sqlalchemy" in results

    def test_empty_source_code(self, complete_schema):
        """Test with empty source code."""
        results = detect_frameworks_from_schema("", complete_schema)
        
        # Should return empty results, not error
        assert isinstance(results, dict)
        for framework in results:
            for feature in results[framework]:
                assert len(results[framework][feature]) == 0

    def test_no_matching_frameworks(self, complete_schema):
        """Test with code that doesn't match any frameworks."""
        source_code = '''
import os
import sys

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
'''
        results = detect_frameworks_from_schema(source_code, complete_schema)
        
        # Should have framework keys but empty detections
        for framework in ["fastapi", "pydantic", "sqlalchemy"]:
            if framework in results:
                for feature in results[framework]:
                    assert len(results[framework][feature]) == 0

    def test_feature_spec_creation(self):
        """Test creating FeatureSpec from parameters."""
        spec = FeatureSpec(
            feature_key="test_feature",
            absolute_paths=["test.module.Class"],
            target_level="function",
            concept="AnnotationLike",
            locator_strategy="VariableBound",
            construct_query={
                "python": {
                    "method_regex": "test"
                }
            },
            description="Test feature"
        )
        
        assert spec.feature_key == "test_feature"
        assert spec.absolute_paths == ["test.module.Class"]
        assert spec.target_level == TargetLevel.FUNCTION
        assert spec.concept == "AnnotationLike"
        assert spec.locator_strategy == LocatorStrategy.VARIABLE_BOUND

    def test_custom_grammar_factory_direct(self):
        """Test CustomGrammarFactory.detect_features directly."""
        # Create a simple feature spec
        spec = FeatureSpec(
            feature_key="fastapi_endpoint",
            absolute_paths=["fastapi.FastAPI"],
            target_level="function",
            concept="AnnotationLike",
            locator_strategy="VariableBound",
            construct_query={
                "python": {
                    "method_regex": "get"
                }
            },
            description="FastAPI GET endpoint"
        )
        
        source_code = '''
from fastapi import FastAPI
app = FastAPI()

@app.get("/test")
def test_endpoint():
    return {"test": True}
'''
        
        result = CustomGrammarFactory.detect_features(
            language=ProgrammingLanguage.PYTHON,
            source_code=source_code,
            feature_specs=[spec]
        )
        
        assert result.success
        assert "fastapi_endpoint" in result.detections
        assert len(result.detections["fastapi_endpoint"]) == 1
        assert result.detections["fastapi_endpoint"][0].match_text == '@app.get("/test")'

    def test_error_handling(self):
        """Test error handling for invalid configurations."""
        # Invalid language
        invalid_schema = {
            "test": {
                "language": "invalid_language",
                "features": {
                    "test": {
                        "target_level": "function",
                        "concept": "AnnotationLike",
                        "locator_strategy": "Direct",
                        "absolute_paths": ["test"]
                    }
                }
            }
        }
        
        results = detect_frameworks_from_schema("test code", invalid_schema)
        # Should handle gracefully, not crash
        assert isinstance(results, dict)

    @pytest.mark.parametrize("locator_strategy,expected_count", [
        ("VariableBound", 2),  # Should find both decorators
        ("Direct", 0),  # Direct strategy won't work for decorators
    ])
    def test_locator_strategies(self, locator_strategy, expected_count):
        """Test different locator strategies."""
        schema = {
            "fastapi": {
                "language": "python",
                "features": {
                    "endpoint": {
                        "target_level": "function",
                        "concept": "AnnotationLike",
                        "locator_strategy": locator_strategy,
                        "absolute_paths": ["fastapi.FastAPI"],
                        "construct_query": {
                            "python": {
                                "method_regex": "(get|post)"
                            }
                        }
                    }
                }
            }
        }
        
        source_code = '''
from fastapi import FastAPI
app = FastAPI()

@app.get("/one")
def one(): pass

@app.post("/two")
def two(): pass
'''
        
        results = detect_frameworks_from_schema(source_code, schema)
        detections = results.get("fastapi", {}).get("endpoint", [])
        assert len(detections) == expected_count