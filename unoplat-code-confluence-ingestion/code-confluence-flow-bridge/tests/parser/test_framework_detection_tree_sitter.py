"""Tests for tree-sitter based framework detection using schema definitions."""

from functools import lru_cache
import json
from pathlib import Path
from typing import List

from unoplat_code_confluence_commons.base_models import (
    Concept,
    FeatureSpec,
    LocatorStrategy,
    TargetLevel,
)

from src.code_confluence_flow_bridge.engine.programming_language.python.python_source_context import (
    PythonSourceContext,
)
from src.code_confluence_flow_bridge.engine.programming_language.python.python_tree_sitter_framework_detector import (
    PythonTreeSitterFrameworkDetector,
)


@lru_cache(maxsize=1)
def _load_python_feature_specs() -> List[FeatureSpec]:
    repo_root = Path(__file__).resolve().parents[2]
    definitions_dir = repo_root / "framework-definitions" / "python"
    feature_specs: List[FeatureSpec] = []

    for json_path in sorted(definitions_dir.glob("*.json")):
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        language_data = payload.get("python", {})
        for library_name, library_data in language_data.items():
            features = library_data.get("features", {})
            for feature_key, feature_data in features.items():
                feature_specs.append(
                    FeatureSpec(
                        feature_key=feature_key,
                        library=library_name,
                        absolute_paths=feature_data.get("absolute_paths", []),
                        target_level=TargetLevel(feature_data.get("target_level")),
                        concept=Concept(feature_data.get("concept")),
                        locator_strategy=LocatorStrategy.VARIABLE_BOUND,
                        construct_query=feature_data.get("construct_query"),
                        description=feature_data.get("description"),
                        startpoint=feature_data.get("startpoint", False),
                    )
                )

    return feature_specs


def test_fastapi_tree_sitter_detection_main_py() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    main_py_path = repo_root / "src" / "code_confluence_flow_bridge" / "main.py"
    source_code = main_py_path.read_text(encoding="utf-8")

    feature_specs = _load_python_feature_specs()
    context = PythonSourceContext.from_source(source_code)
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)
    assert any(det.feature_key == "http_endpoint" for det in detections)


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
    context = PythonSourceContext.from_source(source_code)
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)
    assert any(
        det.feature_key == "data_model" and det.library == "pydantic"
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
    context = PythonSourceContext.from_source(source_code)
    detector = PythonTreeSitterFrameworkDetector()

    detections = detector.detect(context, feature_specs)

    assert any(
        det.feature_key == "column" and det.library == "sqlalchemy"
        for det in detections
    )
    assert any(
        det.feature_key == "mapped_column" and det.library == "sqlalchemy"
        for det in detections
    )
    assert any(
        det.feature_key == "relationship" and det.library == "sqlalchemy"
        for det in detections
    )
    # field_definition removed from sqlmodel in schema v3
    assert any(
        det.feature_key == "relationship" and det.library == "sqlmodel"
        for det in detections
    )
    assert any(
        det.feature_key == "db_data_model" and det.library == "sqlmodel"
        for det in detections
    )
