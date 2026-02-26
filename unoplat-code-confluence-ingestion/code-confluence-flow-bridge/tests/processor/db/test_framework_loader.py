"""Unit tests for framework definition loader schema compatibility."""

from pathlib import Path

from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from src.code_confluence_flow_bridge.processor.db.postgres.framework_loader import (
    FrameworkDefinitionLoader,
)
from unoplat_code_confluence_commons.base_models import Concept


def _build_loader(definitions_path: Path) -> FrameworkDefinitionLoader:
    # EnvironmentSettings is a BaseSettings model with alias
    # FRAMEWORK_DEFINITIONS_PATH. In full-suite runs this env var is set by
    # integration fixtures, so use the alias key explicitly to override it.
    settings = EnvironmentSettings(FRAMEWORK_DEFINITIONS_PATH=str(definitions_path))
    return FrameworkDefinitionLoader(settings)


def test_loader_reads_all_language_directories(tmp_path: Path) -> None:
    definitions_path = tmp_path / "framework-definitions"
    python_dir = definitions_path / "python"
    typescript_dir = definitions_path / "typescript"
    python_dir.mkdir(parents=True)
    typescript_dir.mkdir(parents=True)

    # Root schema file should be ignored by loader (it only loads <lang>/*.json).
    (definitions_path / "schema.json").write_text("{}", encoding="utf-8")

    (python_dir / "fastapi.json").write_text(
        """
{
  "python": {
    "fastapi": {
      "docs_url": "https://fastapi.tiangolo.com",
      "features": {
        "http_endpoint": {
          "description": "HTTP endpoint",
          "absolute_paths": ["fastapi.FastAPI"],
          "target_level": "function",
          "concept": "AnnotationLike"
        }
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    (typescript_dir / "nextjs.json").write_text(
        """
{
  "typescript": {
    "nextjs": {
      "docs_url": "https://nextjs.org/docs",
      "features": {
        "route_handler_export": {
          "description": "Route handler",
          "absolute_paths": ["next/server.NextResponse"],
          "target_level": "function",
          "concept": "FunctionDefinition",
          "construct_query": {
            "function_name_regex": "^(GET|POST)$",
            "export_name_regex": "^(GET|POST)$"
          }
        }
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    loader = _build_loader(definitions_path)
    data = loader.load_framework_definitions()

    assert "python" in data
    assert "typescript" in data
    assert "fastapi" in data["python"]
    assert "nextjs" in data["typescript"]


def test_parse_json_data_preserves_function_export_regexes(tmp_path: Path) -> None:
    loader = _build_loader(tmp_path)

    framework_data = {
        "typescript": {
            "nextjs": {
                "docs_url": "https://nextjs.org/docs",
                "description": "Next.js",
                "features": {
                    "route_handler_export": {
                        "description": "Route handler",
                        "absolute_paths": ["next/server.NextResponse"],
                        "target_level": "function",
                        "concept": "AnnotationLike",
                        "construct_query": {
                            "function_name_regex": "^(GET|POST)$",
                            "export_name_regex": "^(GET|POST)$",
                        },
                    }
                },
            }
        }
    }

    _frameworks, features, _absolute_paths = loader.parse_json_data(framework_data)

    assert len(features) == 1
    feature = features[0]
    assert feature.concept == Concept.ANNOTATION_LIKE
    assert feature.target_level.value == "function"
    assert feature.construct_query is not None
    assert feature.construct_query["function_name_regex"] == "^(GET|POST)$"
    assert feature.construct_query["export_name_regex"] == "^(GET|POST)$"
    assert feature.feature_definition["base_confidence"] == 0.85


def test_parse_json_data_normalizes_base_confidence(tmp_path: Path) -> None:
    loader = _build_loader(tmp_path)

    framework_data = {
        "python": {
            "customlib": {
                "docs_url": "https://example.com/docs",
                "features": {
                    "valid_confidence": {
                        "description": "Valid confidence",
                        "absolute_paths": ["customlib.valid"],
                        "target_level": "function",
                        "concept": "CallExpression",
                        "base_confidence": 0.41,
                    },
                    "invalid_confidence": {
                        "description": "Invalid confidence",
                        "absolute_paths": ["customlib.invalid"],
                        "target_level": "function",
                        "concept": "CallExpression",
                        "base_confidence": 3.2,
                    },
                },
            }
        }
    }

    _frameworks, features, _absolute_paths = loader.parse_json_data(framework_data)

    feature_by_key = {feature.feature_key: feature for feature in features}
    assert (
        feature_by_key["valid_confidence"].feature_definition["base_confidence"] == 0.41
    )
    assert (
        feature_by_key["invalid_confidence"].feature_definition["base_confidence"]
        == 0.85
    )
