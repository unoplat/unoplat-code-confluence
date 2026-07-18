"""Focused database tests for framework query service reconstruction."""

import json
from pathlib import Path

from code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from code_confluence_flow_bridge.processor.db.postgres import (
    framework_query_service,
)
from code_confluence_flow_bridge.processor.db.postgres.db import get_session_cm
from code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
import pytest
from sqlalchemy import delete
from unoplat_code_confluence_commons.base_models import (
    Concept,
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
        Framework.metadata.create_all(
            bind=session.get_bind(),
            tables=[
                Framework.__table__,
                FrameworkFeature.__table__,
                FeatureAbsolutePath.__table__,
            ],
            checkfirst=True,
        )
        session.execute(delete(FeatureAbsolutePath))
        session.execute(delete(FrameworkFeature))
        session.execute(delete(Framework))
        session.add_all(frameworks)
        session.add_all(features)
        session.add_all(absolute_paths)
        session.commit()


@pytest.mark.asyncio(loop_scope="session")
async def test_query_service_rebuilds_operation_level_feature_specs(
    service_ports: dict[str, int],
) -> None:
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
    assert feature_spec.capability_key == "rest_api"
    assert feature_spec.operation_key == "get"
    assert feature_spec.feature_key == "rest_api.get"
    assert feature_spec.library == "fastapi"
    assert sorted(feature_spec.absolute_paths) == [
        "fastapi.APIRouter",
        "fastapi.FastAPI",
    ]
    assert feature_spec.construct_query == {"function_name_regex": "^get$"}
    assert feature_spec.base_confidence == 0.73

    assert len(all_feature_specs) == 1
    assert all_feature_specs[0].capability_key == "rest_api"
    assert all_feature_specs[0].operation_key == "get"
    assert all_feature_specs[0].construct_query == {"function_name_regex": "^get$"}
    assert all_feature_specs[0].base_confidence == 0.73


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    ("definition_file", "source_import", "expected_library", "expected_feature_key"),
    [
        ("click.json", "click", "click", "cli_command.command"),
        (
            "temporalio.json",
            "temporalio.activity",
            "temporalio",
            "background_worker.task_definition",
        ),
        (
            "temporalio.json",
            "temporalio.workflow",
            "temporalio",
            "scheduler.task_definition",
        ),
    ],
)
async def test_query_service_loads_descendant_annotation_feature_specs(
    service_ports: dict[str, int],
    definition_file: str,
    source_import: str,
    expected_library: str,
    expected_feature_key: str,
) -> None:
    definitions_path = Path(__file__).resolve().parents[3] / "framework-definitions"
    framework_data = json.loads(
        (definitions_path / "python" / definition_file).read_text(encoding="utf-8")
    )
    _seed_framework_data(service_ports, framework_data)

    async with get_session_cm() as session:
        feature_specs = (
            await framework_query_service.get_framework_features_for_imports(
                session,
                "python",
                [source_import],
            )
        )

    matching_specs = [
        spec
        for spec in feature_specs
        if spec.library == expected_library
        and spec.feature_key == expected_feature_key
    ]
    assert len(matching_specs) == 1
    assert matching_specs[0].concept == Concept.ANNOTATION_LIKE


@pytest.mark.asyncio(loop_scope="session")
async def test_query_service_does_not_cross_package_boundaries(
    service_ports: dict[str, int],
) -> None:
    definitions_path = Path(__file__).resolve().parents[3] / "framework-definitions"
    click_data = json.loads(
        (definitions_path / "python" / "click.json").read_text(encoding="utf-8")
    )
    _seed_framework_data(service_ports, click_data)

    async with get_session_cm() as session:
        feature_specs = (
            await framework_query_service.get_framework_features_for_imports(
                session,
                "python",
                ["clickhouse"],
            )
        )

    assert feature_specs == []


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize(
    "source_import",
    [
        "sqlalchemy.ext.asyncio.AsyncSession",
        "sqlalchemy.orm.Session",
        "sqlalchemy.insert",
        "sqlalchemy.sql.expression.insert",
        "sqlalchemy.dialects.postgresql.insert",
    ],
)
async def test_query_service_loads_sqlalchemy_db_sql_for_supported_imports(
    service_ports: dict[str, int],
    source_import: str,
) -> None:
    definitions_path = Path(__file__).resolve().parents[3] / "framework-definitions"
    sqlalchemy_data = json.loads(
        (definitions_path / "python" / "sqlalchemy.json").read_text(encoding="utf-8")
    )
    _seed_framework_data(service_ports, sqlalchemy_data)

    async with get_session_cm() as session:
        feature_specs = (
            await framework_query_service.get_framework_features_for_imports(
                session,
                "python",
                [source_import],
            )
        )

    db_sql_specs = [
        spec
        for spec in feature_specs
        if spec.library == "sqlalchemy"
        and spec.feature_key == "relational_database.db_sql"
    ]
    assert len(db_sql_specs) == 1
    spec = db_sql_specs[0]
    assert spec.construct_query_typed is not None
    assert spec.construct_query_typed.match_policy.value == "import_guarded_regex"
    assert spec.base_confidence is not None and spec.base_confidence < 0.70
