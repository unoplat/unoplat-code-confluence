"""
Integration tests for framework definitions ingestion using testcontainers.

This module tests the complete ingestion pipeline for our framework definitions
with a real PostgreSQL database running in a testcontainer. It includes both:
1. Tests using real framework definition files from framework-definitions/
2. Comprehensive data validation and schema compliance tests
3. Performance benchmarks and idempotency verification
"""

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
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    get_framework_features_for_imports,
)
from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
    LocatorStrategy,
    TargetLevel,
)

from tests.utils.sync_db_utils import get_sync_postgres_session

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

    session.execute(delete(FeatureAbsolutePath))
    session.execute(delete(FrameworkFeature))
    session.execute(delete(Framework))

    session.add_all(frameworks)
    session.add_all(features)
    session.add_all(absolute_paths)
    session.commit()

    return {
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
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
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
                SELECT constraint_name, table_name
                FROM information_schema.table_constraints
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
        loader = _build_loader()
        framework_data = loader.load_framework_definitions()

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

        # Validate each framework has required v4 structure
        for framework_name, framework_def in python_frameworks.items():
            assert "docs_url" in framework_def, (
                f"Framework {framework_name} missing docs_url"
            )
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

    def test_bulk_insert_performance(self, test_client: TestClient, service_ports):
        """Test that bulk insert operation meets performance requirements."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
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
            )

            # Verify data exists in database
            framework_count = session.scalar(select(func.count(Framework.language)))  # type: ignore
            feature_count = session.scalar(
                select(func.count(FrameworkFeature.language))
            )  # type: ignore
            path_count = session.scalar(
                select(func.count(FeatureAbsolutePath.language))
            )  # type: ignore

            assert framework_count == 12
            assert feature_count == 59
            assert path_count == 129

    def test_foreign_key_relationships(self, test_client: TestClient, service_ports):
        """Test that foreign key relationships work correctly."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)

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
            )

            related_paths = session.execute(
                select(FeatureAbsolutePath).where(
                    FeatureAbsolutePath.language == rest_api_get_feature.language,
                    FeatureAbsolutePath.library == rest_api_get_feature.library,
                    FeatureAbsolutePath.capability_key
                    == rest_api_get_feature.capability_key,
                    FeatureAbsolutePath.operation_key
                    == rest_api_get_feature.operation_key,
                )
            )
            paths_list = related_paths.scalars().all()

            assert len(paths_list) == 4, (
                f"Expected 4 absolute paths for rest_api.get, got {len(paths_list)}"
            )
            path_values = [p.absolute_path for p in paths_list]
            assert "fastapi.FastAPI" in path_values
            assert "fastapi.applications.FastAPI" in path_values
            assert "fastapi.APIRouter" in path_values
            assert "fastapi.routing.APIRouter" in path_values

    def test_concept_validation(self, test_client: TestClient, service_ports):
        """Test that concept fields are correctly stored."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)

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

            # Should have all four concept types
            assert "AnnotationLike" in concepts
            assert "CallExpression" in concepts
            assert "Inheritance" in concepts
            assert "FunctionDefinition" in concepts

    def test_construct_query_jsonb_storage(
        self, test_client: TestClient, service_ports
    ):
        """Test that feature_definition JSONB stores construct_query correctly."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)

            # Find FastAPI rest_api.get feature which has construct_query
            feature_result = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.library == "fastapi",
                    FrameworkFeature.capability_key == "rest_api",
                    FrameworkFeature.operation_key == "get",
                )
            )
            feature = feature_result.scalar_one()

            assert "construct_query" in feature.feature_definition
            assert feature.construct_query is not None
            assert "method_regex" in feature.construct_query
            assert feature.construct_query["method_regex"] == "^get$"

    def test_clear_and_repopulate_idempotency(
        self, test_client: TestClient, service_ports
    ):
        """Test that multiple runs produce the same result."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            # Run seed function multiple times with the same session
            results = []
            for _i in range(3):
                _seed(session)

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

            # All results should be identical for all framework definitions
            expected_state = {"frameworks": 12, "features": 59, "paths": 129}
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
        loader = _build_loader()
        framework_data = loader.load_framework_definitions()

        # Parse data using production logic
        frameworks, features, absolute_paths = loader.parse_json_data(framework_data)

        # Validate parsing results match expected production data for all definitions
        assert len(frameworks) == 12, f"Expected 12 frameworks, got {len(frameworks)}"
        assert len(features) == 59, f"Expected 59 features, got {len(features)}"
        assert len(absolute_paths) == 129, (
            f"Expected 129 absolute paths, got {len(absolute_paths)}"
        )

        # Test specific framework: FastAPI
        fastapi_framework = next(
            (f for f in frameworks if f.library == "fastapi"), None
        )
        assert fastapi_framework is not None, "FastAPI framework not found"
        assert fastapi_framework.language == "python"
        assert fastapi_framework.docs_url == "https://fastapi.tiangolo.com"

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
        assert "fastapi.FastAPI" in path_values
        assert "fastapi.applications.FastAPI" in path_values
        assert "fastapi.APIRouter" in path_values
        assert "fastapi.routing.APIRouter" in path_values

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
                Concept.FUNCTION_DEFINITION,
            ]
            if feature.concept == Concept.CALL_EXPRESSION:
                base_confidence = feature.feature_definition.get("base_confidence")
                assert base_confidence is not None
                assert 0.0 <= base_confidence <= 1.0
            else:
                assert feature.feature_definition.get("base_confidence") is None
            # locator_strategy defaults to "VariableBound"
            assert feature.locator_strategy == LocatorStrategy.VARIABLE_BOUND
            assert isinstance(feature.startpoint, bool)

        # Validate all absolute paths have required fields
        for ap in absolute_paths:
            assert ap.language is not None
            assert ap.library is not None
            assert ap.feature_key is not None
            assert ap.absolute_path is not None
            assert "." in ap.absolute_path  # Should be fully qualified

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

    def test_payload_defaults_are_applied_during_ingestion(
        self, test_client: TestClient, service_ports
    ):
        """Test non-call features keep existing non-confidence defaults during ingestion."""
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
                                    "absolute_paths": ["customlib.feature"],
                                    "target_level": "function",
                                    "concept": "AnnotationLike",
                                }
                            },
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session, framework_data)

            feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.capability_key == "data_model",
                    FrameworkFeature.operation_key == "custom_feature",
                )
            ).scalar_one()

            assert feature.locator_strategy == LocatorStrategy.VARIABLE_BOUND
            assert feature.feature_definition.get("base_confidence") is None
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
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session, framework_data)

            valid_feature = session.execute(
                select(FrameworkFeature).where(
                    FrameworkFeature.capability_key == "http_client",
                    FrameworkFeature.operation_key == "valid_confidence",
                )
            ).scalar_one()
            assert valid_feature.feature_definition.get("base_confidence") == 0.62

    def test_call_expression_invalid_base_confidence_is_rejected(
        self, test_client: TestClient, service_ports
    ):
        """Test invalid CallExpression base_confidence values are rejected."""
        framework_data = {
            "python": {
                "customlib": {
                    "docs_url": "https://example.com/docs",
                    "description": "Custom framework",
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
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            try:
                _seed(session, framework_data)
            except (ValueError, ValidationError) as exc:
                assert "base_confidence" in str(exc).lower() or "CallExpression" in str(
                    exc
                )
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
                        }
                    },
                }
            }
        }

        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            try:
                _seed(session, framework_data)
            except (ValueError, ValidationError) as exc:
                assert "only for CallExpression" in str(exc)
            else:
                raise AssertionError("Expected non-CallExpression confidence to raise")

    @pytest.mark.asyncio(loop_scope="session")
    async def test_query_parity_for_import_lookup(
        self, test_client: TestClient, service_ports
    ):
        """Test import lookup returns expected FeatureSpec set after JSONB cutover."""
        with get_sync_postgres_session(service_ports["postgresql"]) as session:
            _seed(session)

            imports = [
                "fastapi.FastAPI",
                "sqlmodel.SQLModel",
                "pydantic.BaseModel",
            ]
            expected_rows = session.execute(
                select(
                    FrameworkFeature.capability_key,
                    FrameworkFeature.operation_key,
                    FrameworkFeature.library,
                )
                .join(FeatureAbsolutePath)
                .where(
                    FrameworkFeature.language == "python",
                    FeatureAbsolutePath.absolute_path.in_(imports),
                )
                .distinct()
            ).all()

        expected_set = {
            (f"{row[0]}.{row[1]}", row[2]) for row in expected_rows
        }

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
