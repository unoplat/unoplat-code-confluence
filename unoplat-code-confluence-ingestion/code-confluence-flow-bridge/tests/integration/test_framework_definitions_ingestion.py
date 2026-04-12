"""
Integration tests for framework definitions ingestion using testcontainers.

This module tests the complete ingestion pipeline for our framework definitions
with a real PostgreSQL database running in a testcontainer. It includes both:
<<<<<<< HEAD
1. Tests using real framework definition files from framework-definitions/
=======
1. Tests using real framework definition files from framework-definitions/python/
>>>>>>> origin/main
2. Comprehensive data validation and schema compliance tests
3. Performance benchmarks and idempotency verification
"""

<<<<<<< HEAD
import pathlib
from typing import Any, Dict

from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest
from sqlalchemy import func, select, text
from sqlmodel import delete
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
=======
import json
import pathlib
import time
from typing import Any, Dict, List

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import func, select, text
from sqlmodel import delete
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
>>>>>>> origin/main
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
<<<<<<< HEAD
=======
    FrameworkFeaturePayload,
>>>>>>> origin/main
    LocatorStrategy,
    TargetLevel,
)

from tests.utils.sync_db_utils import get_sync_postgres_session

<<<<<<< HEAD
# Framework definitions directory (all languages)
DEFINITIONS_DIR = pathlib.Path(__file__).parent.parent.parent / "framework-definitions"


def _build_loader() -> FrameworkDefinitionLoader:
    """Build a FrameworkDefinitionLoader pointed at the repo's definitions directory."""
    settings = EnvironmentSettings(FRAMEWORK_DEFINITIONS_PATH=str(DEFINITIONS_DIR))
    return FrameworkDefinitionLoader(settings)


def _seed(session, data: Dict[str, Any] | None = None) -> Dict[str, Any]:  # type: ignore[type-arg]
    """Seed framework definitions using production loader's parser."""
    loader = _build_loader()
    if data is None:
        data = loader.load_framework_definitions()
    frameworks, features, absolute_paths = loader.parse_json_data(data)

=======
# Removed unused async_engine import which was causing ImportError after db refactor

# Framework definitions directory
FRAMEWORK_DEFINITIONS_DIR = (
    pathlib.Path(__file__).parent.parent.parent / "framework-definitions" / "python"
)


def parse_json_data(
    data: Dict[str, Any],
) -> tuple[List[Framework], List[FrameworkFeature], List[FeatureAbsolutePath]]:
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
                frameworks.append(
                    Framework(
                        language=language, library=library_name, docs_url=docs_url
                    )
                )
                seen_frameworks.add(framework_key)

            # Process features
            features_data = library_data.get("features", {})
            for feature_key, feature_data in features_data.items():
                normalized_payload = normalize_feature_payload(feature_data)
                feature_definition = normalized_payload.model_dump(
                    mode="json", exclude_none=False
                )
                if feature_definition.get("concept") != "CallExpression":
                    feature_definition.pop("base_confidence", None)
                elif feature_definition.get("base_confidence") is None:
                    feature_definition.pop("base_confidence", None)

                # Create FrameworkFeature record with new schema fields
                features.append(
                    FrameworkFeature(
                        language=language,
                        library=library_name,
                        feature_key=feature_key,
                        feature_definition=feature_definition,
                    )
                )

                # Create FeatureAbsolutePath records for each absolute path
                absolute_paths_data = normalized_payload.absolute_paths
                for absolute_path in absolute_paths_data:
                    absolute_paths.append(
                        FeatureAbsolutePath(
                            language=language,
                            library=library_name,
                            feature_key=feature_key,
                            absolute_path=absolute_path,
                        )
                    )

    return frameworks, features, absolute_paths


def normalize_feature_payload(feature_data: Dict[str, Any]) -> FrameworkFeaturePayload:
    payload_data = dict(feature_data)

    if not isinstance(payload_data.get("absolute_paths"), list):
        payload_data["absolute_paths"] = []
    else:
        payload_data["absolute_paths"] = [
            value for value in payload_data["absolute_paths"] if isinstance(value, str)
        ]

    if not isinstance(payload_data.get("construct_query"), dict):
        payload_data["construct_query"] = None

    if payload_data.get("concept") not in {
        "AnnotationLike",
        "CallExpression",
        "Inheritance",
        "FunctionDefinition",
    }:
        payload_data["concept"] = "AnnotationLike"

    if payload_data.get("target_level") not in {"function", "class"}:
        payload_data["target_level"] = "function"

    if payload_data["concept"] == "CallExpression":
        base_confidence = payload_data.get("base_confidence")
        if not isinstance(base_confidence, (int, float)) or isinstance(
            base_confidence, bool
        ):
            raise ValueError(
                "CallExpression features must define explicit numeric base_confidence"
            )
        numeric_confidence = float(base_confidence)
        if not 0.0 <= numeric_confidence <= 1.0:
            raise ValueError(
                "CallExpression base_confidence must be between 0.0 and 1.0"
            )
        payload_data["base_confidence"] = numeric_confidence
    elif "base_confidence" in payload_data:
        raise ValueError(
            "base_confidence is supported only for CallExpression features"
        )

    if payload_data.get("locator_strategy") not in {
        "VariableBound",
        "Direct",
    }:
        payload_data["locator_strategy"] = "VariableBound"

    if not isinstance(payload_data.get("startpoint"), bool):
        payload_data["startpoint"] = False

    return FrameworkFeaturePayload.model_validate(payload_data)


def resolve_base_confidence(feature: FrameworkFeature) -> float | None:
    """Resolve normalized base_confidence from feature_definition payload."""
    if feature.concept != Concept.CALL_EXPRESSION:
        return None

    raw_value = feature.feature_definition.get("base_confidence")
    if raw_value is None:
        return None
    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
        numeric_value = float(raw_value)
        if 0.0 <= numeric_value <= 1.0:
            return numeric_value
    return None


def load_framework_definitions() -> Dict[str, Any]:
    """Load and combine all framework definition files."""
    if not FRAMEWORK_DEFINITIONS_DIR.exists():
        raise FileNotFoundError(
            f"Framework definitions directory not found: {FRAMEWORK_DEFINITIONS_DIR}"
        )

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


def seed_framework_definitions(
    framework_data: Dict[str, Any], session
) -> Dict[str, Any]:
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
>>>>>>> origin/main
    session.execute(delete(FeatureAbsolutePath))
    session.execute(delete(FrameworkFeature))
    session.execute(delete(Framework))

<<<<<<< HEAD
    session.add_all(frameworks)
    session.add_all(features)
    session.add_all(absolute_paths)
    session.commit()

    return {
=======
    # Bulk insert all records
    session.add_all(frameworks)
    session.add_all(features)
    session.add_all(absolute_paths)

    # Single commit
    session.commit()

    db_time = time.time() - db_start_time
    total_time = time.time() - start_time

    return {
        "parsing_time": parsing_time,
        "db_time": db_time,
        "total_time": total_time,
>>>>>>> origin/main
        "frameworks_count": len(frameworks),
        "features_count": len(features),
        "absolute_paths_count": len(absolute_paths),
    }


@pytest.mark.integration
class TestFrameworkDefinitionsIngestion:
    """
    Integration tests for framework definitions ingestion with real PostgreSQL.

    This test class validates the complete ingestion pipeline using real framework
    definition files from the framework-definitions/ directory. Tests include:
    - Schema creation and validation
    - Data loading from real JSON framework definitions
    - Performance benchmarks for bulk operations
    - Data integrity and relationship validation
    - Schema compliance and field validation
    - Idempotency and concurrent operation safety
    """

    def test_schema_creation_and_structure(
        self, test_client: TestClient, service_ports
    ):
        """Test that database tables are created correctly with proper structure."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            # Verify all three tables exist
            result = session.execute(
                text("""
<<<<<<< HEAD
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
=======
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
>>>>>>> origin/main
                AND table_name IN ('framework', 'framework_feature', 'feature_absolute_path')
                ORDER BY table_name
            """)
            )  # type: ignore
            tables = [row[0] for row in result.fetchall()]

            assert len(tables) == 3, f"Expected 3 tables, got {len(tables)}: {tables}"
            assert "framework" in tables
            assert "framework_feature" in tables
            assert "feature_absolute_path" in tables

            # Verify foreign key constraints exist
            fk_result = session.execute(
                text("""
<<<<<<< HEAD
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
=======
                SELECT constraint_name, table_name 
                FROM information_schema.table_constraints 
>>>>>>> origin/main
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_name IN ('framework_feature', 'feature_absolute_path')
            """)
            )  # type: ignore
            foreign_keys = fk_result.fetchall()

            assert len(foreign_keys) >= 2, (
                f"Expected at least 2 foreign keys, got {len(foreign_keys)}"
            )

            # Verify JSONB payload column exists
            column_result = session.execute(
                text("""
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'framework_feature'
                  AND column_name = 'feature_definition'
            """)
            )
            data_type = column_result.scalar_one()
            assert data_type == "jsonb"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_framework_definitions_loading(self):
        """Test that framework definitions can be loaded and parsed correctly."""
<<<<<<< HEAD
        loader = _build_loader()
        framework_data = loader.load_framework_definitions()
=======
        # Load framework definitions
        framework_data = load_framework_definitions()
>>>>>>> origin/main

        # Validate structure
        assert "python" in framework_data, (
            "Expected 'python' language in framework data"
        )
        python_frameworks = framework_data["python"]

        expected_frameworks = {
            "celery",
            "fastapi",
            "fastmcp",
            "litellm",
            "pydantic",
            "sqlalchemy",
            "sqlmodel",
        }
        actual_frameworks = set(python_frameworks.keys())
        assert actual_frameworks == expected_frameworks, (
            f"Expected {expected_frameworks}, got {actual_frameworks}"
        )

<<<<<<< HEAD
        # Validate each framework has required v4 structure
=======
        # Validate each framework has required structure
>>>>>>> origin/main
        for framework_name, framework_def in python_frameworks.items():
            assert "docs_url" in framework_def, (
                f"Framework {framework_name} missing docs_url"
            )
<<<<<<< HEAD
            assert "capabilities" in framework_def, (
                f"Framework {framework_name} missing capabilities"
            )
            assert len(framework_def["capabilities"]) > 0, (
                f"Framework {framework_name} has no capabilities"
            )

            # Validate capabilities -> operations structure
            for cap_key, cap_data in framework_def["capabilities"].items():
                for op_key, op_data in cap_data.get("operations", {}).items():
                    required_fields = [
                        "description",
                        "absolute_paths",
                        "target_level",
                        "concept",
                    ]
                    for field in required_fields:
                        assert field in op_data, (
                            f"Operation {framework_name}.{cap_key}.{op_key} missing {field}"
                        )
=======
            assert "features" in framework_def, (
                f"Framework {framework_name} missing features"
            )
            assert len(framework_def["features"]) > 0, (
                f"Framework {framework_name} has no features"
            )

            # Validate feature structure (schema v3: locator_strategy removed)
            for feature_key, feature_def in framework_def["features"].items():
                required_fields = [
                    "description",
                    "absolute_paths",
                    "target_level",
                    "concept",
                ]
                for field in required_fields:
                    assert field in feature_def, (
                        f"Feature {framework_name}.{feature_key} missing {field}"
                    )
>>>>>>> origin/main

    def test_bulk_insert_performance(self, test_client: TestClient, service_ports):
        """Test that bulk insert operation meets performance requirements."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            # Execute optimized seed function
            metrics = _seed(session)

            # Validate expected data counts for all framework definitions
            assert metrics["frameworks_count"] == 12, (
                f"Expected 12 frameworks, got {metrics['frameworks_count']}"
            )
            assert metrics["features_count"] == 59, (
                f"Expected 59 features, got {metrics['features_count']}"
            )
            assert metrics["absolute_paths_count"] == 129, (
                f"Expected 129 absolute paths, got {metrics['absolute_paths_count']}"
=======
            # Load framework definitions
            framework_data = load_framework_definitions()

            # Execute optimized seed function
            metrics = seed_framework_definitions(framework_data, session)

            # Validate performance (should be well under 5 seconds for our framework data)
            assert metrics["total_time"] < 5.0, (
                f"Operation took {metrics['total_time']:.3f}s, expected < 5.0s"
            )
            assert metrics["db_time"] < 3.0, (
                f"Database operations took {metrics['db_time']:.3f}s, expected < 3.0s"
            )

            # Validate expected data counts for python framework definitions
            assert metrics["frameworks_count"] == 7, (
                f"Expected 7 frameworks, got {metrics['frameworks_count']}"
            )
            assert metrics["features_count"] == 13, (
                f"Expected 13 features, got {metrics['features_count']}"
            )
            assert metrics["absolute_paths_count"] == 32, (
                f"Expected 32 absolute paths, got {metrics['absolute_paths_count']}"
>>>>>>> origin/main
            )

            # Verify data exists in database
            framework_count = session.scalar(select(func.count(Framework.language)))  # type: ignore
            feature_count = session.scalar(
                select(func.count(FrameworkFeature.language))
            )  # type: ignore
            path_count = session.scalar(
                select(func.count(FeatureAbsolutePath.language))
            )  # type: ignore

<<<<<<< HEAD
            assert framework_count == 12
            assert feature_count == 59
            assert path_count == 129
=======
            assert framework_count == 7
            assert feature_count == 13
            assert path_count == 32
>>>>>>> origin/main

    def test_foreign_key_relationships(self, test_client: TestClient, service_ports):
        """Test that foreign key relationships work correctly."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            _seed(session)
=======
            framework_data = load_framework_definitions()

            seed_framework_definitions(framework_data, session)
>>>>>>> origin/main

            # Test framework -> feature relationship for FastAPI
            framework_result = session.execute(
                select(Framework).where(
                    Framework.language == "python", Framework.library == "fastapi"
                )
            )
            framework = framework_result.scalar_one()

            # Load related features
            related_features = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.language == framework.language,
                    FrameworkFeature.library == framework.library,
                )
            )
            features_list = related_features.scalars().all()

<<<<<<< HEAD
            assert len(features_list) == 9, (
                f"Expected 9 FastAPI features, got {len(features_list)}"
            )

            # Test feature -> absolute paths relationship
            rest_api_get_feature = None
            for feature in features_list:
                if feature.feature_key == "rest_api.get":
                    rest_api_get_feature = feature
                    break

            assert rest_api_get_feature is not None, (
                "FastAPI rest_api.get feature not found"
=======
            assert len(features_list) == 3, (
                f"Expected 3 FastAPI features, got {len(features_list)}"
            )

            # Test feature -> absolute paths relationship
            http_endpoint_feature = None
            for feature in features_list:
                if feature.feature_key == "http_endpoint":
                    http_endpoint_feature = feature
                    break

            assert http_endpoint_feature is not None, (
                "FastAPI http_endpoint feature not found"
>>>>>>> origin/main
            )

            related_paths = session.execute(
                select(FeatureAbsolutePath).where(
<<<<<<< HEAD
                    FeatureAbsolutePath.language == rest_api_get_feature.language,
                    FeatureAbsolutePath.library == rest_api_get_feature.library,
                    FeatureAbsolutePath.capability_key
                    == rest_api_get_feature.capability_key,
                    FeatureAbsolutePath.operation_key
                    == rest_api_get_feature.operation_key,
=======
                    FeatureAbsolutePath.language == http_endpoint_feature.language,
                    FeatureAbsolutePath.library == http_endpoint_feature.library,
                    FeatureAbsolutePath.feature_key
                    == http_endpoint_feature.feature_key,
>>>>>>> origin/main
                )
            )
            paths_list = related_paths.scalars().all()

            assert len(paths_list) == 4, (
<<<<<<< HEAD
                f"Expected 4 absolute paths for rest_api.get, got {len(paths_list)}"
=======
                f"Expected 4 absolute paths for http_endpoint, got {len(paths_list)}"
>>>>>>> origin/main
            )
            path_values = [p.absolute_path for p in paths_list]
            assert "fastapi.FastAPI" in path_values
            assert "fastapi.applications.FastAPI" in path_values
            assert "fastapi.APIRouter" in path_values
            assert "fastapi.routing.APIRouter" in path_values

    def test_concept_validation(self, test_client: TestClient, service_ports):
<<<<<<< HEAD
        """Test that concept fields are correctly stored."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)
=======
        """Test that concept fields are correctly stored (schema v3: locator_strategy removed)."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            framework_data = load_framework_definitions()

            seed_framework_definitions(framework_data, session)
>>>>>>> origin/main

            # Test different concept types
            concept_expression = FrameworkFeature.concept_sql_expression()
            concepts_query = session.execute(
                select(concept_expression, func.count(concept_expression)).group_by(
                    concept_expression
                )
            )
            concepts = {
                row[0].value if hasattr(row[0], "value") else row[0]: row[1]
                for row in concepts_query.fetchall()
            }

<<<<<<< HEAD
            # Should have all four concept types
            assert "AnnotationLike" in concepts
            assert "CallExpression" in concepts
            assert "Inheritance" in concepts
            assert "FunctionDefinition" in concepts
=======
            # Should have all three concept types
            assert "AnnotationLike" in concepts
            assert "CallExpression" in concepts
            assert "Inheritance" in concepts
>>>>>>> origin/main

    def test_construct_query_jsonb_storage(
        self, test_client: TestClient, service_ports
    ):
        """Test that feature_definition JSONB stores construct_query correctly."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            _seed(session)

            # Find FastAPI rest_api.get feature which has construct_query
            feature_result = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.library == "fastapi",
                    FrameworkFeature.capability_key == "rest_api",
                    FrameworkFeature.operation_key == "get",
=======
            framework_data = load_framework_definitions()

            seed_framework_definitions(framework_data, session)

            # Find FastAPI http_endpoint feature which has construct_query
            feature_result = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.library == "fastapi",
                    FrameworkFeature.feature_key == "http_endpoint",
>>>>>>> origin/main
                )
            )
            feature = feature_result.scalar_one()

            assert "construct_query" in feature.feature_definition
            assert feature.construct_query is not None
            assert "method_regex" in feature.construct_query
<<<<<<< HEAD
            assert feature.construct_query["method_regex"] == "^get$"
=======
            assert (
                feature.construct_query["method_regex"]
                == "(get|post|put|delete|patch|head|options|trace)"
            )
>>>>>>> origin/main

    def test_clear_and_repopulate_idempotency(
        self, test_client: TestClient, service_ports
    ):
        """Test that multiple runs produce the same result."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            # Run seed function multiple times with the same session
            results = []
            for _i in range(3):
                _seed(session)
=======
            framework_data = load_framework_definitions()

            # Run seed function multiple times with the same session
            results = []
            for i in range(3):
                _metrics = seed_framework_definitions(framework_data, session)
>>>>>>> origin/main

                # Capture current state
                frameworks = session.execute(select(Framework))
                features = session.execute(select(FrameworkFeature))
                paths = session.execute(select(FeatureAbsolutePath))

                state = {
                    "frameworks": len(frameworks.scalars().all()),
                    "features": len(features.scalars().all()),
                    "paths": len(paths.scalars().all()),
                }
                results.append(state)

<<<<<<< HEAD
            # All results should be identical for all framework definitions
            expected_state = {"frameworks": 12, "features": 59, "paths": 129}
=======
            # All results should be identical for python framework definitions
            expected_state = {"frameworks": 7, "features": 13, "paths": 32}
>>>>>>> origin/main
            for result in results:
                assert result == expected_state

            # Verify final state has correct data
            final_framework = session.execute(
                select(Framework).where(Framework.library == "pydantic")
            )
            fw = final_framework.scalar_one()
            assert fw.language == "python"
            assert fw.docs_url == "https://docs.pydantic.dev"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_real_framework_data_parsing_accuracy(self):
        """Test parsing accuracy using real framework definition files to ensure schema compliance."""
<<<<<<< HEAD
        loader = _build_loader()
        framework_data = loader.load_framework_definitions()

        # Parse data using production logic
        frameworks, features, absolute_paths = loader.parse_json_data(framework_data)

        # Validate parsing results match expected production data for all definitions
        assert len(frameworks) == 12, f"Expected 12 frameworks, got {len(frameworks)}"
        assert len(features) == 59, f"Expected 59 features, got {len(features)}"
        assert len(absolute_paths) == 129, (
            f"Expected 129 absolute paths, got {len(absolute_paths)}"
=======
        # Load real framework definitions
        framework_data = load_framework_definitions()

        # Parse data using the same logic as production
        frameworks, features, absolute_paths = parse_json_data(framework_data)

        # Validate parsing results match expected production data for python definitions
        assert len(frameworks) == 7, f"Expected 7 frameworks, got {len(frameworks)}"
        assert len(features) == 13, f"Expected 13 features, got {len(features)}"
        assert len(absolute_paths) == 32, (
            f"Expected 32 absolute paths, got {len(absolute_paths)}"
>>>>>>> origin/main
        )

        # Test specific framework: FastAPI
        fastapi_framework = next(
            (f for f in frameworks if f.library == "fastapi"), None
        )
        assert fastapi_framework is not None, "FastAPI framework not found"
        assert fastapi_framework.language == "python"
        assert fastapi_framework.docs_url == "https://fastapi.tiangolo.com"

<<<<<<< HEAD
        # Test specific feature: FastAPI rest_api.get
        fastapi_features = [f for f in features if f.library == "fastapi"]
        assert len(fastapi_features) == 9, (
            f"Expected 9 FastAPI features, got {len(fastapi_features)}"
        )

        rest_api_get = next(
            (f for f in fastapi_features if f.feature_key == "rest_api.get"), None
        )
        assert rest_api_get is not None, (
            "FastAPI rest_api.get feature not found"
        )
        assert rest_api_get.description == "FastAPI GET route handler."
        assert rest_api_get.target_level == TargetLevel.FUNCTION
        assert rest_api_get.concept == Concept.ANNOTATION_LIKE
        assert rest_api_get.locator_strategy == LocatorStrategy.VARIABLE_BOUND
        assert rest_api_get.startpoint is True, (
            "rest_api.get should be marked as startpoint"
        )
        assert rest_api_get.construct_query is not None
        assert "method_regex" in rest_api_get.construct_query
        assert rest_api_get.construct_query["method_regex"] == "^get$"
        # AnnotationLike concept has no base_confidence
        assert rest_api_get.feature_definition.get("base_confidence") is None

        # Test absolute paths for rest_api.get
        rest_api_get_paths = [
            ap
            for ap in absolute_paths
            if ap.library == "fastapi" and ap.feature_key == "rest_api.get"
        ]
        assert len(rest_api_get_paths) == 4, (
            f"Expected 4 paths for rest_api.get, got {len(rest_api_get_paths)}"
        )
        path_values = [p.absolute_path for p in rest_api_get_paths]
=======
        # Test specific feature: FastAPI http_endpoint (should have startpoint=True)
        fastapi_features = [f for f in features if f.library == "fastapi"]
        assert len(fastapi_features) == 3, (
            f"Expected 3 FastAPI features, got {len(fastapi_features)}"
        )

        http_endpoint = next(
            (f for f in fastapi_features if f.feature_key == "http_endpoint"), None
        )
        assert http_endpoint is not None, "FastAPI http_endpoint feature not found"
        assert (
            http_endpoint.description
            == "HTTP verb decorator that registers a route handler"
        )
        assert http_endpoint.target_level == TargetLevel.FUNCTION
        assert http_endpoint.concept == Concept.ANNOTATION_LIKE
        assert http_endpoint.locator_strategy == LocatorStrategy.VARIABLE_BOUND
        assert http_endpoint.startpoint is True, (
            "http_endpoint should be marked as startpoint"
        )
        assert http_endpoint.construct_query is not None
        assert "method_regex" in http_endpoint.construct_query
        assert resolve_base_confidence(http_endpoint) is None

        # Test absolute paths for http_endpoint
        http_endpoint_paths = [
            ap
            for ap in absolute_paths
            if ap.library == "fastapi" and ap.feature_key == "http_endpoint"
        ]
        assert len(http_endpoint_paths) == 4, (
            f"Expected 4 paths for http_endpoint, got {len(http_endpoint_paths)}"
        )
        path_values = [p.absolute_path for p in http_endpoint_paths]
>>>>>>> origin/main
        assert "fastapi.FastAPI" in path_values
        assert "fastapi.applications.FastAPI" in path_values
        assert "fastapi.APIRouter" in path_values
        assert "fastapi.routing.APIRouter" in path_values

<<<<<<< HEAD
        # Test specific feature: FastMCP mcp_client.toolset_client
        fastmcp_features = [f for f in features if f.library == "fastmcp"]
        assert len(fastmcp_features) == 3, (
            f"Expected 3 FastMCP features, got {len(fastmcp_features)}"
        )

        fastmcp_toolset_client = next(
            (
                f
                for f in fastmcp_features
                if f.feature_key == "mcp_client.toolset_client"
            ),
            None,
        )
        assert fastmcp_toolset_client is not None, (
            "FastMCP mcp_client.toolset_client feature not found"
        )
        assert fastmcp_toolset_client.concept == Concept.CALL_EXPRESSION
        assert fastmcp_toolset_client.target_level == TargetLevel.FUNCTION
        assert fastmcp_toolset_client.startpoint is False
        assert fastmcp_toolset_client.feature_definition.get("base_confidence") == 0.95

        fastmcp_toolset_paths = [
            ap
            for ap in absolute_paths
            if ap.library == "fastmcp"
            and ap.feature_key == "mcp_client.toolset_client"
        ]
        assert len(fastmcp_toolset_paths) == 1, (
            f"Expected 1 absolute path for mcp_client.toolset_client, got {len(fastmcp_toolset_paths)}"
        )
        assert (
            fastmcp_toolset_paths[0].absolute_path
            == "pydantic_ai.toolsets.fastmcp.FastMCPToolset"
        )

=======
>>>>>>> origin/main
        # Validate all features have required fields
        for feature in features:
            assert feature.language is not None
            assert feature.library is not None
            assert feature.feature_key is not None
            assert feature.description is not None
            assert feature.target_level in [
                TargetLevel.FUNCTION,
                TargetLevel.CLASS,
            ]
            assert feature.concept in [
                Concept.ANNOTATION_LIKE,
                Concept.CALL_EXPRESSION,
                Concept.INHERITANCE,
<<<<<<< HEAD
                Concept.FUNCTION_DEFINITION,
            ]
            if feature.concept == Concept.CALL_EXPRESSION:
                base_confidence = feature.feature_definition.get("base_confidence")
                assert base_confidence is not None
                assert 0.0 <= base_confidence <= 1.0
            else:
                assert feature.feature_definition.get("base_confidence") is None
            # locator_strategy defaults to "VariableBound"
=======
            ]
            if feature.concept == Concept.CALL_EXPRESSION:
                base_confidence = resolve_base_confidence(feature)
                assert base_confidence is not None
                assert 0.0 <= base_confidence <= 1.0
            else:
                assert resolve_base_confidence(feature) is None
            # locator_strategy defaults to "VariableBound" (schema v3 removed this field)
>>>>>>> origin/main
            assert feature.locator_strategy == LocatorStrategy.VARIABLE_BOUND
            assert isinstance(feature.startpoint, bool)

        # Validate all absolute paths have required fields
        for ap in absolute_paths:
            assert ap.language is not None
            assert ap.library is not None
            assert ap.feature_key is not None
            assert ap.absolute_path is not None
            assert "." in ap.absolute_path  # Should be fully qualified

<<<<<<< HEAD
    def test_unknown_keys_are_rejected_in_feature_definition(
        self, test_client: TestClient, service_ports
    ):
        """Test unknown feature keys are rejected due to extra='forbid'."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
                    "capabilities": {
                        "data_model": {
                            "description": "Validation capability.",
                            "operations": {
                                "custom_feature": {
                                    "description": "Custom feature",
                                    "absolute_paths": ["customlib.Feature"],
                                    "target_level": "function",
                                    "concept": "AnnotationLike",
                                    "synthetic_extra_field": {"enabled": True},
                                }
                            },
                        }
                    },
                }
            }
        }
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            with pytest.raises((ValidationError, ValueError)):
                _seed(session, framework_data)
=======
    def test_unknown_keys_are_preserved_in_feature_definition(
        self, test_client: TestClient, service_ports
    ):
        """Test unknown feature keys are preserved through JSONB ingestion."""
        framework_data = load_framework_definitions()
        framework_data["python"]["fastapi"]["features"]["http_endpoint"][
            "synthetic_extra_field"
        ] = {"enabled": True, "note": "preserve"}

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            seed_framework_definitions(framework_data, session)

            feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.library == "fastapi",
                    FrameworkFeature.feature_key == "http_endpoint",
                )
            ).scalar_one()

            assert "synthetic_extra_field" in feature.feature_definition
            assert feature.feature_definition["synthetic_extra_field"] == {
                "enabled": True,
                "note": "preserve",
            }
>>>>>>> origin/main

    def test_payload_defaults_are_applied_during_ingestion(
        self, test_client: TestClient, service_ports
    ):
        """Test non-call features keep existing non-confidence defaults during ingestion."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
<<<<<<< HEAD
                    "capabilities": {
                        "data_model": {
                            "description": "Validation capability.",
                            "operations": {
                                "custom_feature": {
                                    "description": "Custom feature",
                                    "absolute_paths": ["customlib.feature"],
                                    "target_level": "function",
                                    "concept": "AnnotationLike",
                                }
                            },
=======
                    "features": {
                        "custom_feature": {
                            "description": "Custom feature",
                            "absolute_paths": ["customlib.feature"],
                            "target_level": "function",
                            "concept": "AnnotationLike",
>>>>>>> origin/main
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            _seed(session, framework_data)

            feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.capability_key == "data_model",
                    FrameworkFeature.operation_key == "custom_feature",
                )
            ).scalar_one()

            assert feature.locator_strategy == LocatorStrategy.VARIABLE_BOUND
            assert feature.feature_definition.get("base_confidence") is None
=======
            seed_framework_definitions(framework_data, session)

            feature = session.execute(select(FrameworkFeature)).scalar_one()

            assert feature.locator_strategy == LocatorStrategy.VARIABLE_BOUND
            assert resolve_base_confidence(feature) is None
>>>>>>> origin/main
            assert feature.startpoint is False
            assert feature.feature_definition["locator_strategy"] == "VariableBound"
            assert "base_confidence" not in feature.feature_definition
            assert feature.feature_definition["startpoint"] is False

    def test_base_confidence_is_normalized_during_ingestion(
        self, test_client: TestClient, service_ports
    ):
        """Test CallExpression base_confidence must be explicit and valid during ingestion."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
<<<<<<< HEAD
                    "capabilities": {
                        "http_client": {
                            "description": "Client capability.",
                            "operations": {
                                "valid_confidence": {
                                    "description": "Valid confidence",
                                    "absolute_paths": ["customlib.valid"],
                                    "target_level": "function",
                                    "concept": "CallExpression",
                                    "base_confidence": 0.62,
                                }
                            },
                        }
=======
                    "features": {
                        "valid_confidence": {
                            "description": "Valid confidence",
                            "absolute_paths": ["customlib.valid"],
                            "target_level": "function",
                            "concept": "CallExpression",
                            "base_confidence": 0.62,
                        },
>>>>>>> origin/main
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
<<<<<<< HEAD
            _seed(session, framework_data)

            valid_feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.capability_key == "http_client",
                    FrameworkFeature.operation_key == "valid_confidence",
                )
            ).scalar_one()
            assert valid_feature.feature_definition.get("base_confidence") == 0.62
=======
            seed_framework_definitions(framework_data, session)

            valid_feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.feature_key == "valid_confidence"
                )
            ).scalar_one()
            assert resolve_base_confidence(valid_feature) == 0.62
>>>>>>> origin/main

    def test_call_expression_invalid_base_confidence_is_rejected(
        self, test_client: TestClient, service_ports
    ):
        """Test invalid CallExpression base_confidence values are rejected."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
<<<<<<< HEAD
                    "capabilities": {
                        "http_client": {
                            "description": "Client capability.",
                            "operations": {
                                "invalid_confidence": {
                                    "description": "Invalid confidence",
                                    "absolute_paths": ["customlib.invalid"],
                                    "target_level": "function",
                                    "concept": "CallExpression",
                                    "base_confidence": 1.4,
                                }
                            },
=======
                    "features": {
                        "invalid_confidence": {
                            "description": "Invalid confidence",
                            "absolute_paths": ["customlib.invalid"],
                            "target_level": "function",
                            "concept": "CallExpression",
                            "base_confidence": 1.4,
>>>>>>> origin/main
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            try:
<<<<<<< HEAD
                _seed(session, framework_data)
            except (ValueError, ValidationError) as exc:
                assert "base_confidence" in str(exc).lower() or "CallExpression" in str(
                    exc
                )
=======
                seed_framework_definitions(framework_data, session)
            except ValueError as exc:
                assert "CallExpression base_confidence" in str(exc)
>>>>>>> origin/main
            else:
                raise AssertionError(
                    "Expected invalid CallExpression confidence to raise"
                )

    def test_non_call_expression_base_confidence_is_rejected(
        self, test_client: TestClient, service_ports
    ):
        """Test non-CallExpression features cannot define base_confidence."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
<<<<<<< HEAD
                    "capabilities": {
                        "rest_api": {
                            "description": "Endpoint capability.",
                            "operations": {
                                "get": {
                                    "description": "HTTP endpoint",
                                    "absolute_paths": ["customlib.Endpoint"],
                                    "target_level": "function",
                                    "concept": "AnnotationLike",
                                    "base_confidence": 0.91,
                                }
                            },
=======
                    "features": {
                        "http_endpoint": {
                            "description": "HTTP endpoint",
                            "absolute_paths": ["customlib.Endpoint"],
                            "target_level": "function",
                            "concept": "AnnotationLike",
                            "base_confidence": 0.91,
>>>>>>> origin/main
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            try:
<<<<<<< HEAD
                _seed(session, framework_data)
            except (ValueError, ValidationError) as exc:
=======
                seed_framework_definitions(framework_data, session)
            except ValueError as exc:
>>>>>>> origin/main
                assert "only for CallExpression" in str(exc)
            else:
                raise AssertionError("Expected non-CallExpression confidence to raise")

    @pytest.mark.asyncio(loop_scope="session")
    async def test_query_parity_for_import_lookup(
        self, test_client: TestClient, service_ports
    ):
        """Test import lookup returns expected FeatureSpec set after JSONB cutover."""
<<<<<<< HEAD
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)
=======
        framework_data = load_framework_definitions()

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            seed_framework_definitions(framework_data, session)
>>>>>>> origin/main

            imports = [
                "fastapi.FastAPI",
                "sqlmodel.SQLModel",
                "pydantic.BaseModel",
            ]
            expected_rows = session.execute(
<<<<<<< HEAD
                select(
                    FrameworkFeature.capability_key,
                    FrameworkFeature.operation_key,
                    FrameworkFeature.library,
                )
=======
                select(FrameworkFeature.feature_key, FrameworkFeature.library)
>>>>>>> origin/main
                .join(FeatureAbsolutePath)
                .where(
                    FrameworkFeature.language == "python",
                    FeatureAbsolutePath.absolute_path.in_(imports),
                )
                .distinct()
            ).all()

<<<<<<< HEAD
        expected_set = {
            (f"{row[0]}.{row[1]}", row[2]) for row in expected_rows
        }
=======
        expected_set = {(row[0], row[1]) for row in expected_rows}
>>>>>>> origin/main

        async with get_session_cm() as async_session:
            feature_specs = await get_framework_features_for_imports(
                async_session,
                "python",
                imports,
            )

        actual_set = {
            (feature.feature_key, feature.library) for feature in feature_specs
        }
        assert actual_set == expected_set
