"""Tests for tree-sitter based framework detection using schema definitions."""

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import List, cast

from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_tree_sitter_framework_detector import (
    PythonTreeSitterFrameworkDetector,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
from src.code_confluence_flow_bridge.processor.db.postgres.framework_query_service import (
    _build_feature_spec,
    _resolve_base_confidence,
)
from unoplat_code_confluence_commons.base_models import (
    CallExpressionInfo,
    Concept,
    FeatureSpec,
    InheritanceInfo,
    LocatorStrategy,
    TargetLevel,
)


@lru_cache(maxsize=1)
def _load_python_feature_specs() -> List[FeatureSpec]:
    """Load Python feature specs through the production normalization pipeline."""
    repo_root = Path(__file__).resolve().parents[2]
    definitions_dir = repo_root / "framework-definitions"

    # Use production loader for JSON loading + normalization
    settings = EnvironmentSettings(FRAMEWORK_DEFINITIONS_PATH=str(definitions_dir))
    loader = FrameworkDefinitionLoader(settings)
    framework_data = loader.load_framework_definitions()
    _frameworks, features, absolute_paths = loader.parse_json_data(framework_data)

    # Group absolute paths by feature identity (mirrors DB join)
    paths_by_feature: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for ap in absolute_paths:
        paths_by_feature[(ap.language, ap.library, ap.feature_key)].append(
            ap.absolute_path
        )

    # Convert to FeatureSpec using production query-service logic
    feature_specs: List[FeatureSpec] = []
    for feature in features:
        if feature.language != "python":
            continue
        feature_paths = paths_by_feature[
            (feature.language, feature.library, feature.feature_key)
        ]
        base_confidence = _resolve_base_confidence(feature)
        feature_specs.append(
            _build_feature_spec(feature, feature_paths, base_confidence)
        )

    return feature_specs


def _build_pydantic_inheritance_spec() -> FeatureSpec:
    return FeatureSpec(
        capability_key="data_model",
        operation_key="data_model",
        library="pydantic",
        absolute_paths=["pydantic.BaseModel", "pydantic.main.BaseModel"],
        target_level=TargetLevel.CLASS,
        concept=Concept.INHERITANCE,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        description="Pydantic BaseModel inheritance",
    )


def _build_litellm_completion_spec() -> FeatureSpec:
    return FeatureSpec(
        capability_key="llm_inference",
        operation_key="llm_completion",
        library="litellm",
        absolute_paths=["litellm.completion", "litellm.main.completion"],
        target_level=TargetLevel.FUNCTION,
        concept=Concept.CALL_EXPRESSION,
        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
        description="LiteLLM completion call",
        base_confidence=0.69,
    )


def test_fastapi_tree_sitter_detection_main_py() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    main_py_path = repo_root / "src" / "code_confluence_flow_bridge" / "main.py"
    source_code = main_py_path.read_text(encoding="utf-8")

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)
    assert any(det.feature_key.startswith("rest_api.") for det in detections)


def test_fastapi_tree_sitter_detection_router_decorators() -> None:
    source_code = """
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
"""

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)

    assert any(
        det.feature_key == "rest_api.get"
        and det.library == "fastapi"
        and "health" in det.match_text
        for det in detections
    )


def test_fastapi_tree_sitter_detection_fastapi_routing_apirouter() -> None:
    source_code = """
from fastapi.routing import APIRouter

router = APIRouter()


@router.post("/users")
async def create_user() -> dict[str, bool]:
    return {"created": True}
"""

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)

    assert any(
        det.feature_key == "rest_api.post"
        and det.library == "fastapi"
        and "users" in det.match_text
        for det in detections
    )


def test_pydantic_tree_sitter_detection_model_file() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    model_path = (
        repo_root
        / "src"
        / "code_confluence_flow_bridge"
        / "models"
        / "github"
        / "github_repo.py"
    )
    source_code = model_path.read_text(encoding="utf-8")

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)
    assert any(
        det.feature_key == "data_model.data_model" and det.library == "pydantic"
        for det in detections
    )


def test_sqlalchemy_and_sqlmodel_call_expression_detection() -> None:
    source_code = """
from sqlalchemy import Column
from sqlalchemy.orm import mapped_column, relationship
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel):
    id: int = Field(primary_key=True)


def build():
    Column("id")
    mapped_column("name")
    relationship("Other")
    Relationship(back_populates="users")
"""

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)

    # field_definition removed from sqlmodel in schema v3
    assert any(
        det.feature_key == "relational_database.relationship" and det.library == "sqlmodel"
        for det in detections
    )
    assert any(
        det.feature_key == "relational_database.db_data_model" and det.library == "sqlmodel"
        for det in detections
    )


def test_python_call_expression_accepts_import_bound_module_alias_call() -> None:
    source_code = """
import litellm as llm


def run() -> None:
    llm.completion(model="gpt-4o-mini", messages=[])
"""

    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()
    spec = _build_litellm_completion_spec()

    detections = detector.detect(context, [spec])

    assert len(detections) == 1
    call_detection = cast(CallExpressionInfo, detections[0])
    assert call_detection.library == "litellm"
    assert call_detection.feature_key == "llm_inference.llm_completion"
    assert call_detection.callee == "llm.completion"
    assert call_detection.metadata["match_confidence"] == spec.base_confidence
    assert call_detection.metadata["call_match_kind"] == "module_member_exact"
    assert call_detection.metadata["matched_absolute_path"] == "litellm.completion"
    assert call_detection.metadata["matched_alias"] == "llm"
    assert call_detection.metadata["call_match_policy_version"] == "v1_import_bound"


def test_python_call_expression_rejects_unbound_member_collision() -> None:
    source_code = """
from litellm import completion


class ApiClient:
    def completion(self, payload: str) -> str:
        return payload


api = ApiClient()


def run() -> str:
    return api.completion("hello")
"""

    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_litellm_completion_spec()])

    assert detections == []


def test_pydantic_inheritance_rejects_unbound_member_superclass() -> None:
    source_code = """
from pydantic import BaseModel


class User(foo.BaseModel):
    pass
"""

    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_pydantic_inheritance_spec()])

    assert detections == []


def test_pydantic_inheritance_accepts_symbol_alias_superclass() -> None:
    source_code = """
from pydantic import BaseModel as BM


class User(BM):
    pass
"""

    context = PythonSourceContext.from_bytes(source_code.encode("utf-8", errors="ignore"))
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, [_build_pydantic_inheritance_spec()])

    assert len(detections) == 1
    inheritance_detection = cast(InheritanceInfo, detections[0])
    assert inheritance_detection.library == "pydantic"
    assert inheritance_detection.feature_key == "data_model.data_model"
    assert inheritance_detection.subclass == "User"
    assert inheritance_detection.superclass == "BM"
