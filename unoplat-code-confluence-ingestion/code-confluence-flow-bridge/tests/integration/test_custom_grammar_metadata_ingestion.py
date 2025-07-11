"""
Integration tests for custom grammar metadata ingestion using testcontainers.

This module tests the optimized bulk insert script for custom grammar metadata
with a real PostgreSQL database running in a testcontainer. It validates the
parsing logic, performance improvements, and data integrity.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest
import pytest_asyncio
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, delete

from src.code_confluence_flow_bridge.processor.db.postgres.custom_grammar_metadata import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import (
    AsyncSessionLocal,
    async_engine,
    create_db_and_tables,
    get_session_cm,
)

# Test data file path
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data" / "custom_grammar"
LIBRARY_SCHEMA_FILE = TEST_DATA_DIR / "library-schema.json"




# Helper function updated for new schema format
def parse_json_data(data: Dict[str, Any]) -> tuple[List[Framework], List[FrameworkFeature], List[FeatureAbsolutePath]]:
    """Parse JSON data and transform to normalized database records."""
    frameworks = []
    features = []
    absolute_paths = []
    
    # Track unique frameworks to avoid duplicates
    seen_frameworks = set()
    
    # Parse new schema structure: language -> library -> features
    for language, language_data in data.items():
        for library_name, library_data in language_data.items():
            docs_url = library_data.get("docs_url")
            
            # Create Framework record (deduplicated)
            framework_key = (language, library_name)
            if framework_key not in seen_frameworks:
                frameworks.append(Framework(
                    language=language,
                    library=library_name,
                    docs_url=docs_url
                ))
                seen_frameworks.add(framework_key)
            
            # Process features
            features_data = library_data.get("features", {})
            for feature_key, feature_data in features_data.items():
                # Create FrameworkFeature record with new schema fields
                features.append(FrameworkFeature(
                    language=language,
                    library=library_name,
                    feature_key=feature_key,
                    description=feature_data.get("description"),
                    target_level=feature_data.get("target_level", "function"),
                    concept=feature_data.get("concept", "AnnotationLike"),
                    locator_strategy=feature_data.get("locator_strategy", "VariableBound"),
                    construct_query=feature_data.get("construct_query")
                ))
                
                # Create FeatureAbsolutePath records for each absolute path
                absolute_paths_data = feature_data.get("absolute_paths", [])
                for absolute_path in absolute_paths_data:
                    absolute_paths.append(FeatureAbsolutePath(
                        language=language,
                        library=library_name,
                        feature_key=feature_key,
                        absolute_path=absolute_path
                    ))
    
    return frameworks, features, absolute_paths


async def seed_custom_grammar_metadata(json_data: Dict[str, Any], session) -> Dict[str, Any]:
    """
    Optimized seed function with clear + repopulate strategy.
    Returns metrics about the operation.
    """
    start_time = time.time()
    
    # Parse JSON data into normalized records
    frameworks, features, absolute_paths = parse_json_data(json_data)
    parsing_time = time.time() - start_time
    
    # Atomic operation: clear existing + repopulate
    db_start_time = time.time()
    
    # Clear in correct order (foreign key dependencies)
    await session.execute(delete(FeatureAbsolutePath))
    await session.execute(delete(FrameworkFeature))
    await session.execute(delete(Framework))
    
    # Bulk insert all records
    session.add_all(frameworks)
    session.add_all(features)
    session.add_all(absolute_paths)
    
    # Single commit
    await session.commit()
    
    db_time = time.time() - db_start_time
    total_time = time.time() - start_time
    
    return {
        "parsing_time": parsing_time,
        "db_time": db_time,
        "total_time": total_time,
        "frameworks_count": len(frameworks),
        "features_count": len(features),
        "absolute_paths_count": len(absolute_paths),
    }


@pytest.mark.integration
class TestCustomGrammarMetadataIngestion:
    """Integration tests for custom grammar metadata ingestion with real PostgreSQL."""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_schema_creation_and_structure(self, postgres_session):
        """Test that database tables are created correctly with proper structure."""
        session = postgres_session
        
        # Verify all three tables exist
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('framework', 'framework_feature', 'feature_absolute_path')
            ORDER BY table_name
        """))
        rows =  result.fetchall()
        tables = [row[0] for row in rows]
        
        assert len(tables) == 3, f"Expected 3 tables, got {len(tables)}: {tables}"
        assert "framework" in tables
        assert "framework_feature" in tables  
        assert "feature_absolute_path" in tables
        
        # Verify foreign key constraints exist
        fk_result = await session.execute(text("""
            SELECT constraint_name, table_name 
            FROM information_schema.table_constraints 
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_name IN ('framework_feature', 'feature_absolute_path')
        """))
        foreign_keys = fk_result.fetchall()
        
        assert len(foreign_keys) >= 2, f"Expected at least 2 foreign keys, got {len(foreign_keys)}"
        

    @pytest.mark.asyncio
    async def test_json_parsing_accuracy(self):
        """Test that JSON parsing logic transforms data correctly."""
        # Load test data
        assert LIBRARY_SCHEMA_FILE.exists(), f"Test data file not found: {LIBRARY_SCHEMA_FILE}"
        test_data = json.loads(LIBRARY_SCHEMA_FILE.read_text())
        
        # Parse data
        frameworks, features, absolute_paths = parse_json_data(test_data)
        
        # Validate parsing results
        assert len(frameworks) == 1, f"Expected 1 framework, got {len(frameworks)}"
        assert len(features) == 1, f"Expected 1 feature, got {len(features)}"
        assert len(absolute_paths) == 2, f"Expected 2 absolute paths, got {len(absolute_paths)}"
        
        # Validate framework data
        framework = frameworks[0]
        assert framework.language == "python"
        assert framework.library == "fastapi"
        assert framework.docs_url == "https://fastapi.tiangolo.com"
        
        # Validate feature data
        feature = features[0]
        assert feature.language == "python"
        assert feature.library == "fastapi"
        assert feature.feature_key == "endpoint"
        assert feature.description == "HTTP verb decorator that registers a route"
        assert feature.target_level == "function"
        assert feature.concept == "AnnotationLike"
        assert feature.locator_strategy == "VariableBound"
        assert isinstance(feature.construct_query, dict)
        assert "python" in feature.construct_query
        
        # Validate absolute paths
        expected_paths = ["fastapi.FastAPI", "fastapi.applications.FastAPI"]
        actual_paths = [ap.absolute_path for ap in absolute_paths]
        assert set(actual_paths) == set(expected_paths)
        
        # Validate all absolute paths have correct metadata
        for ap in absolute_paths:
            assert ap.language == "python"
            assert ap.library == "fastapi"
            assert ap.feature_key == "endpoint"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_bulk_insert_performance(self,postgres_session):
        """Test that bulk insert operation meets performance requirements."""
        session = postgres_session
        # Load test data
        test_data = json.loads(LIBRARY_SCHEMA_FILE.read_text())
            
        metrics = await seed_custom_grammar_metadata(test_data, session)
        
        # Validate performance (should be well under 2 seconds for this small dataset)
        assert metrics["total_time"] < 2.0, f"Operation took {metrics['total_time']:.3f}s, expected < 2.0s"
        assert metrics["db_time"] < 1.0, f"Database operations took {metrics['db_time']:.3f}s, expected < 1.0s"
        
        # Validate data was inserted
        assert metrics["frameworks_count"] == 1
        assert metrics["features_count"] == 1  
        assert metrics["absolute_paths_count"] == 2
        
        # Verify data exists in database
        framework_count = await session.scalar(select(func.count(Framework.language)))
        feature_count = await session.scalar(select(func.count(FrameworkFeature.language)))
        path_count = await session.scalar(select(func.count(FeatureAbsolutePath.language)))
        
        assert framework_count == 1
        assert feature_count == 1
        assert path_count == 2
        

    @pytest.mark.asyncio(loop_scope="session")
    async def test_foreign_key_relationships(self,postgres_session):
        """Test that foreign key relationships work correctly."""
        session = postgres_session
        
        # Load and seed test data
        test_data = json.loads(LIBRARY_SCHEMA_FILE.read_text())
        
        
        await seed_custom_grammar_metadata(test_data, session)
        # Test framework -> feature relationship
        framework_with_features = await session.execute(
            select(Framework).where(
                Framework.language == "python",
                Framework.library == "fastapi"
            )
        )
        framework = framework_with_features.scalar_one()
        
        # Load related features (test relationship)
        related_features = await session.execute(
            select(FrameworkFeature).where(
                FrameworkFeature.language == framework.language,
                FrameworkFeature.library == framework.library
            )
        )
        features_list =  related_features.scalars().all()
        
        assert len(features_list) == 1
        feature = features_list[0]
        assert feature.feature_key == "endpoint"
        
        # Test feature -> absolute paths relationship  
        related_paths = await session.execute(
            select(FeatureAbsolutePath).where(
                FeatureAbsolutePath.language == feature.language,
                FeatureAbsolutePath.library == feature.library,
                FeatureAbsolutePath.feature_key == feature.feature_key
            )
        )
        paths_list =  related_paths.scalars().all()
        
        assert len(paths_list) == 2
        path_values = [p.absolute_path for p in paths_list]
        assert "fastapi.FastAPI" in path_values
        assert "fastapi.applications.FastAPI" in path_values