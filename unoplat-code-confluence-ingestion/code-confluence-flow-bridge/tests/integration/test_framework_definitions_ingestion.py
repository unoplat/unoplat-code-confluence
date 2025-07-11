"""
Integration tests for framework definitions ingestion using testcontainers.

This module tests the complete ingestion pipeline for our framework definitions
with a real PostgreSQL database running in a testcontainer.
"""

import json
import pathlib
import time
from typing import Any, Dict, List

import pytest
from sqlalchemy import func, select, text
from sqlmodel import SQLModel, delete

from src.code_confluence_flow_bridge.processor.db.postgres.custom_grammar_metadata import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import (
    async_engine,
    create_db_and_tables,
    get_session_cm,
)

# Framework definitions directory
FRAMEWORK_DEFINITIONS_DIR = pathlib.Path(__file__).parent.parent.parent / "framework-definitions" / "python"


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


def load_framework_definitions() -> Dict[str, Any]:
    """Load and combine all framework definition files."""
    if not FRAMEWORK_DEFINITIONS_DIR.exists():
        raise FileNotFoundError(f"Framework definitions directory not found: {FRAMEWORK_DEFINITIONS_DIR}")
    
    combined_data: Dict[str, Dict[str, Any]] = {}
    json_files = list(FRAMEWORK_DEFINITIONS_DIR.glob("*.json"))
    
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {FRAMEWORK_DEFINITIONS_DIR}")
    
    for json_file in json_files:
        file_data = json.loads(json_file.read_text())
        
        # Merge the data (each file has the language -> library -> features structure)
        for language, language_data in file_data.items():
            if language not in combined_data:
                combined_data[language] = {}
            combined_data[language].update(language_data)
    
    return combined_data


async def seed_framework_definitions(framework_data: Dict[str, Any], session) -> Dict[str, Any]:
    """
    Optimized seed function with clear + repopulate strategy.
    Returns metrics about the operation.
    """
    start_time = time.time()
    
    # Parse JSON data into normalized records
    frameworks, features, absolute_paths = parse_json_data(framework_data)
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
class TestFrameworkDefinitionsIngestion:
    """Integration tests for framework definitions ingestion with real PostgreSQL."""

    @pytest.mark.asyncio
    async def test_schema_creation_and_structure(self):
        """Test that database tables are created correctly with proper structure."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        # Use fresh session for this test
        async with get_session_cm() as session:
            
            # Verify all three tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('framework', 'framework_feature', 'feature_absolute_path')
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
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
    async def test_framework_definitions_loading(self):
        """Test that framework definitions can be loaded and parsed correctly."""
        # Load framework definitions
        framework_data = load_framework_definitions()
        
        # Validate structure
        assert "python" in framework_data, "Expected 'python' language in framework data"
        python_frameworks = framework_data["python"]
        
        expected_frameworks = {"fastapi", "pydantic", "sqlalchemy", "sqlmodel"}
        actual_frameworks = set(python_frameworks.keys())
        assert actual_frameworks == expected_frameworks, f"Expected {expected_frameworks}, got {actual_frameworks}"
        
        # Validate each framework has required structure
        for framework_name, framework_def in python_frameworks.items():
            assert "docs_url" in framework_def, f"Framework {framework_name} missing docs_url"
            assert "features" in framework_def, f"Framework {framework_name} missing features"
            assert len(framework_def["features"]) > 0, f"Framework {framework_name} has no features"
            
            # Validate feature structure
            for feature_key, feature_def in framework_def["features"].items():
                required_fields = ["description", "absolute_paths", "target_level", "concept", "locator_strategy"]
                for field in required_fields:
                    assert field in feature_def, f"Feature {framework_name}.{feature_key} missing {field}"

    @pytest.mark.asyncio
    async def test_bulk_insert_performance(self):
        """Test that bulk insert operation meets performance requirements."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        # Load framework definitions
        framework_data = load_framework_definitions()
        
        # Use fresh session for this test
        async with get_session_cm() as session:
            # Execute optimized seed function
            metrics = await seed_framework_definitions(framework_data, session)
            
            # Validate performance (should be well under 5 seconds for our framework data)
            assert metrics["total_time"] < 5.0, f"Operation took {metrics['total_time']:.3f}s, expected < 5.0s"
            assert metrics["db_time"] < 3.0, f"Database operations took {metrics['db_time']:.3f}s, expected < 3.0s"
            
            # Validate expected data counts
            assert metrics["frameworks_count"] == 4, f"Expected 4 frameworks, got {metrics['frameworks_count']}"
            assert metrics["features_count"] == 15, f"Expected 15 features, got {metrics['features_count']}"
            assert metrics["absolute_paths_count"] == 19, f"Expected 19 absolute paths, got {metrics['absolute_paths_count']}"
            
            # Verify data exists in database
            framework_count = await session.scalar(select(func.count(Framework.language)))
            feature_count = await session.scalar(select(func.count(FrameworkFeature.language)))
            path_count = await session.scalar(select(func.count(FeatureAbsolutePath.language)))
            
            assert framework_count == 4
            assert feature_count == 15
            assert path_count == 19

    @pytest.mark.asyncio  
    async def test_foreign_key_relationships(self):
        """Test that foreign key relationships work correctly."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        framework_data = load_framework_definitions()
        
        # Use fresh session for this test
        async with get_session_cm() as session:
            await seed_framework_definitions(framework_data, session)
            
            # Test framework -> feature relationship for FastAPI
            framework_result = await session.execute(
                select(Framework).where(
                    Framework.language == "python",
                    Framework.library == "fastapi"
                )
            )
            framework = framework_result.scalar_one()
            
            # Load related features
            related_features = await session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.language == framework.language,
                    FrameworkFeature.library == framework.library
                )
            )
            features_list = related_features.scalars().all()
            
            assert len(features_list) == 4, f"Expected 4 FastAPI features, got {len(features_list)}"
            
            # Test feature -> absolute paths relationship
            http_endpoint_feature = None
            for feature in features_list:
                if feature.feature_key == "http_endpoint":
                    http_endpoint_feature = feature
                    break
            
            assert http_endpoint_feature is not None, "FastAPI http_endpoint feature not found"
            
            related_paths = await session.execute(
                select(FeatureAbsolutePath).where(
                    FeatureAbsolutePath.language == http_endpoint_feature.language,
                    FeatureAbsolutePath.library == http_endpoint_feature.library,
                    FeatureAbsolutePath.feature_key == http_endpoint_feature.feature_key
                )
            )
            paths_list = related_paths.scalars().all()
            
            assert len(paths_list) == 2, f"Expected 2 absolute paths for http_endpoint, got {len(paths_list)}"
            path_values = [p.absolute_path for p in paths_list]
            assert "fastapi.FastAPI" in path_values
            assert "fastapi.applications.FastAPI" in path_values

    @pytest.mark.asyncio
    async def test_concept_and_locator_strategy_validation(self):
        """Test that concept and locator strategy fields are correctly stored."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        framework_data = load_framework_definitions()
        
        # Use fresh session for this test
        async with get_session_cm() as session:
            await seed_framework_definitions(framework_data, session)
            
            # Test different concept types
            concepts_query = await session.execute(
                select(FrameworkFeature.concept, func.count(FrameworkFeature.concept)).group_by(FrameworkFeature.concept)
            )
            concepts = dict(concepts_query.fetchall())
            
            # Should have all three concept types
            assert "AnnotationLike" in concepts
            assert "CallExpression" in concepts
            assert "Inheritance" in concepts
            
            # Test locator strategies
            strategies_query = await session.execute(
                select(FrameworkFeature.locator_strategy, func.count(FrameworkFeature.locator_strategy)).group_by(FrameworkFeature.locator_strategy)
            )
            strategies = dict(strategies_query.fetchall())
            
            # Should have both locator strategies
            assert "Direct" in strategies
            assert "VariableBound" in strategies

    @pytest.mark.asyncio
    async def test_construct_query_jsonb_storage(self):
        """Test that construct_query JSONB field is stored and retrieved correctly."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        framework_data = load_framework_definitions()
        
        # Use fresh session for this test
        async with get_session_cm() as session:
            await seed_framework_definitions(framework_data, session)
            
            # Find FastAPI http_endpoint feature which has construct_query
            feature_result = await session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.library == "fastapi",
                    FrameworkFeature.feature_key == "http_endpoint"
                )
            )
            feature = feature_result.scalar_one()
            
            assert feature.construct_query is not None
            assert "python" in feature.construct_query
            assert "method_regex" in feature.construct_query["python"]
            assert feature.construct_query["python"]["method_regex"] == "(get|post|put|delete|patch|head|options|trace)"

    @pytest.mark.asyncio
    async def test_clear_and_repopulate_idempotency(self):
        """Test that multiple runs produce the same result."""
        # Ensure fresh engine bound to current event loop
        await create_db_and_tables()
        
        framework_data = load_framework_definitions()
        
        # Run seed function multiple times with fresh sessions
        results = []
        for i in range(3):
            async with get_session_cm() as session:
                _metrics = await seed_framework_definitions(framework_data, session)
                
                # Capture current state
                frameworks = await session.execute(select(Framework))
                features = await session.execute(select(FrameworkFeature))
                paths = await session.execute(select(FeatureAbsolutePath))
                
                state = {
                    "frameworks": len(frameworks.scalars().all()),
                    "features": len(features.scalars().all()),
                    "paths": len(paths.scalars().all())
                }
                results.append(state)
        
        # All results should be identical
        expected_state = {"frameworks": 4, "features": 15, "paths": 19}
        for result in results:
            assert result == expected_state
        
        # Verify final state has correct data
        async with get_session_cm() as session:
            final_framework = await session.execute(
                select(Framework).where(Framework.library == "pydantic")
            )
            fw = final_framework.scalar_one()
            assert fw.language == "python"
            assert fw.docs_url == "https://docs.pydantic.dev"