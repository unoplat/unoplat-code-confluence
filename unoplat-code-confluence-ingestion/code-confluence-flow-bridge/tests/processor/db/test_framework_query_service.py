"""Focused database tests for framework query service reconstruction."""

from pathlib import Path

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import delete
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.processor.db.postgres import (
    framework_query_service,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
from unoplat_code_confluence_commons.base_models import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)

from tests.utils.sync_db_utils import get_sync_postgres_session


def _build_loader(definitions_path: Path) -> FrameworkDefinitionLoader:
    settings = EnvironmentSettings(FRAMEWORK_DEFINITIONS_PATH=str(definitions_path))
    return FrameworkDefinitionLoader(settings)


def _seed_framework_data(
    service_ports: dict[str, int], framework_data: dict[str, object]
) -> None:
    loader = _build_loader(Path("."))
    frameworks, features, absolute_paths = loader.parse_json_data(framework_data)

    with get_sync_postgres_session(service_ports["postgresql"]) as session:
        session.execute(delete(FeatureAbsolutePath))
        session.execute(delete(FrameworkFeature))
        session.execute(delete(Framework))
        session.add_all(frameworks)
        session.add_all(features)
        session.add_all(absolute_paths)
        session.commit()


@pytest.mark.asyncio(loop_scope="session")
async def test_query_service_rebuilds_operation_level_feature_specs(
    test_client: TestClient,
    service_ports: dict[str, int],
) -> None:
    del test_client

    framework_data = {
        "python": {
            "fastapi": {
                "docs_url": "https://fastapi.tiangolo.com",
                "description": "FastAPI",
                "capabilities": {
                    "rest_api": {
                        "operations": {
                            "get": {
                                "description": "HTTP GET endpoint",
                                "absolute_paths": [
                                    "fastapi.FastAPI",
                                    "fastapi.APIRouter",
                                ],
                                "target_level": "function",
                                "concept": "CallExpression",
                                "locator_strategy": "Direct",
                                "construct_query": {
                                    "function_name_regex": "^get$",
                                },
                                "base_confidence": 0.73,
                                "startpoint": True,
                            }
                        }
                    }
                },
            }
        }
    }

    _seed_framework_data(service_ports, framework_data)

    async with get_session_cm() as session:
        feature_specs = (
            await framework_query_service.get_framework_features_for_imports(
                session,
                "python",
                ["fastapi.FastAPI"],
            )
        )
        all_feature_specs = (
            await framework_query_service.get_all_framework_features_for_language(
                session,
                "python",
            )
        )

    assert len(feature_specs) == 1
    feature_spec = feature_specs[0]
    capability_key, operation_key = feature_spec.feature_key.split(".", 1)
    assert feature_spec.feature_key == "rest_api.get"
    assert capability_key == "rest_api"
    assert operation_key == "get"
    assert feature_spec.library == "fastapi"
    assert sorted(feature_spec.absolute_paths) == [
        "fastapi.APIRouter",
        "fastapi.FastAPI",
    ]
    assert feature_spec.construct_query == {"function_name_regex": "^get$"}
    assert feature_spec.base_confidence == 0.73

    assert len(all_feature_specs) == 1
    all_capability_key, all_operation_key = all_feature_specs[0].feature_key.split(
        ".", 1
    )
    assert all_capability_key == "rest_api"
    assert all_operation_key == "get"
    assert all_feature_specs[0].construct_query == {"function_name_regex": "^get$"}
    assert all_feature_specs[0].base_confidence == 0.73
