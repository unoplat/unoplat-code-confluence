"""Load framework definition JSON files and bulk-insert them into Postgres."""

import os
import json
import logging
import pathlib
import time
from typing import Any, Dict, cast

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from unoplat_code_confluence_commons.base_models import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
    FrameworkFeaturePayload,
)

from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)

logger = logging.getLogger(__name__)


def _normalize_concept_name(raw_concept: object) -> str:
    """Map a raw concept value to a known concept name, defaulting to AnnotationLike."""
    if raw_concept in {
        "AnnotationLike",
        "CallExpression",
        "Inheritance",
        "FunctionDefinition",
    }:
        return cast(str, raw_concept)
    return "AnnotationLike"


def _normalize_base_confidence(payload_data: Dict[str, Any]) -> None:
    """Validate and coerce base_confidence for CallExpression payloads.

    Args:
        payload_data: Mutable feature payload dict; modified in-place.

    Raises:
        ValueError: If base_confidence is present on a non-CallExpression
            concept, is not numeric, or falls outside ``[0.0, 1.0]``.
    """
    concept_name = cast(str, payload_data["concept"])
    if concept_name != "CallExpression":
        if "base_confidence" in payload_data:
            raise ValueError(
                "base_confidence is supported only for CallExpression features"
            )
        return

    base_confidence = payload_data.get("base_confidence")
    if not isinstance(base_confidence, (int, float)) or isinstance(
        base_confidence, bool
    ):
        raise ValueError(
            "CallExpression features must define explicit numeric base_confidence"
        )

    numeric_confidence = float(base_confidence)
    if not 0.0 <= numeric_confidence <= 1.0:
        raise ValueError("CallExpression base_confidence must be between 0.0 and 1.0")

    payload_data["base_confidence"] = numeric_confidence


class FrameworkDefinitionLoader:
    """Handles bulk loading of framework definitions at application startup."""

    def __init__(self, env_settings: EnvironmentSettings):
        """Initialize loader with path from environment settings."""
        self.definitions_path = pathlib.Path(env_settings.framework_definitions_path)
        self._loaded = False

        # Debug environment variable loading
        logger.info(
            f"Environment variable FRAMEWORK_DEFINITIONS_PATH: {os.getenv('FRAMEWORK_DEFINITIONS_PATH', 'NOT SET')}"
        )
        logger.info(
            f"Settings framework_definitions_path: {env_settings.framework_definitions_path}"
        )
        logger.info(
            f"FrameworkDefinitionLoader initialized with path: {self.definitions_path}"
        )
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Absolute definitions path: {self.definitions_path.resolve()}")
        logger.debug(f"Path exists: {self.definitions_path.exists()}")

    def load_framework_definitions(self) -> Dict[str, Any]:
        """Load and combine all framework definition JSON files."""
        logger.info(f"Loading framework definitions from: {self.definitions_path}")

        if not self.definitions_path.exists():
            raise FileNotFoundError(
                "Framework definitions directory not found: "
                f"{self.definitions_path.resolve()}"
            )

        combined_data: Dict[str, Dict[str, Any]] = {}
        json_files = sorted(
            file_path
            for file_path in self.definitions_path.glob("*/*.json")
            if file_path.is_file()
        )

        if not json_files:
            logger.warning("No framework definition JSON files found in language dirs")
            return combined_data

        language_dirs = sorted({json_file.parent.name for json_file in json_files})
        logger.info(
            f"Loading framework definitions from {len(json_files)} files across languages: "
            f"{', '.join(language_dirs)}"
        )

        for json_file in json_files:
            try:
                logger.debug(f"Loading framework definition from {json_file}")
                file_data = json.loads(json_file.read_text())

                # Merge data from each file (language -> library -> capabilities -> operations structure)
                for language, language_data in file_data.items():
                    if language not in combined_data:
                        combined_data[language] = {}
                    combined_data[language].update(language_data)

            except Exception as e:
                logger.error(
                    f"Failed to load framework definition from {json_file}: {e}"
                )
                raise

        logger.info(
            f"Successfully loaded framework definitions from {len(json_files)} files"
        )
        return combined_data

    def parse_json_data(
        self, data: Dict[str, Any]
    ) -> tuple[list[Framework], list[FrameworkFeature], list[FeatureAbsolutePath]]:
        """Parse JSON data into normalized database records."""
        frameworks: list[Framework] = []
        features: list[FrameworkFeature] = []
        absolute_paths: list[FeatureAbsolutePath] = []

        # Track unique frameworks to avoid duplicates
        seen_frameworks: set[tuple[str, str]] = set()

        logger.debug("Parsing framework definitions into SQLModel objects")

        # Parse new schema structure: language -> library -> capabilities -> operations
        for language, language_data_raw in data.items():
            language_data = cast(dict[str, dict[str, Any]], language_data_raw)
            for library_name, library_data in language_data.items():
                docs_url = library_data.get("docs_url")
                description = library_data.get("description")

                # Create Framework record (deduplicated)
                framework_key = (language, library_name)
                if framework_key not in seen_frameworks:
                    frameworks.append(
                        Framework(
                            language=language,
                            library=library_name,
                            docs_url=docs_url,
                            description=description,
                        )
                    )
                    seen_frameworks.add(framework_key)

                # Process capabilities -> operations
                capabilities_data = cast(
                    dict[str, dict[str, Any]],
                    library_data.get("capabilities", {}),
                )
                for cap_key, cap_data in capabilities_data.items():
                    operations_data = cast(
                        dict[str, dict[str, Any]],
                        cap_data.get("operations", {}),
                    )
                    for op_key, op_data in operations_data.items():
                        feature_key = f"{cap_key}.{op_key}"
                        feature_data = dict(op_data)
                        feature_data["capability_key"] = cap_key
                        feature_data["operation_key"] = op_key
                        normalized_payload = self._normalize_feature_payload(
                            feature_data
                        )
                        feature_definition: dict[str, object] = (
                            normalized_payload.model_dump(
                                mode="json", exclude_none=False
                            )
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

        logger.info(
            f"Parsed {len(frameworks)} frameworks, {len(features)} features, {len(absolute_paths)} absolute paths"
        )
        return frameworks, features, absolute_paths

    def _normalize_feature_payload(
        self, feature_data: Dict[str, Any]
    ) -> FrameworkFeaturePayload:
        """Sanitise and validate raw feature JSON into a FrameworkFeaturePayload."""
        payload_data = dict(feature_data)

        if not isinstance(payload_data.get("absolute_paths"), list):
            payload_data["absolute_paths"] = []
        else:
            payload_data["absolute_paths"] = [
                value
                for value in payload_data["absolute_paths"]
                if isinstance(value, str)
            ]

        if not isinstance(payload_data.get("construct_query"), dict):
            payload_data["construct_query"] = None

        payload_data["concept"] = _normalize_concept_name(payload_data.get("concept"))
        _normalize_base_confidence(payload_data)

        if payload_data.get("target_level") not in {"function", "class"}:
            payload_data["target_level"] = "function"

        if payload_data.get("locator_strategy") not in {
            "VariableBound",
            "Direct",
        }:
            payload_data["locator_strategy"] = "VariableBound"

        if not isinstance(payload_data.get("startpoint"), bool):
            payload_data["startpoint"] = False

        return FrameworkFeaturePayload.model_validate(payload_data)

    async def load_framework_definitions_at_startup(
        self, session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Load framework definitions at startup with optimized bulk insertion.
        Uses atomic clear + repopulate strategy for consistency.
        """
        logger.info("Starting framework definitions loading...")
        start_time = time.time()

        # Check if already loaded (idempotency)
        existing_count: int = (
            await session.scalar(select(func.count(Framework.language))) or 0
        )  # type: ignore
        if existing_count > 0 and self._loaded:
            logger.info(
                f"Framework definitions already loaded ({existing_count} frameworks). Skipping."
            )
            return {"skipped": True, "existing_count": existing_count}

        # Load and parse definitions
        framework_data = self.load_framework_definitions()
        frameworks, features, absolute_paths = self.parse_json_data(framework_data)
        parsing_time = time.time() - start_time

        logger.info(
            f"Parsed {len(frameworks)} frameworks, {len(features)} features, {len(absolute_paths)} paths in {parsing_time:.3f}s"
        )

        # Atomic operation: clear existing + repopulate
        db_start_time = time.time()

        # Clear in correct order (foreign key dependencies)
        logger.debug("Clearing existing framework definitions...")

        await session.execute(delete(FeatureAbsolutePath))  # type: ignore
        await session.execute(delete(FrameworkFeature))  # type: ignore
        await session.execute(delete(Framework))  # type: ignore

        # Bulk insert all records using add_all (optimal for our data size)
        logger.debug("Bulk inserting framework definitions...")
        session.add_all(frameworks)
        session.add_all(features)
        session.add_all(absolute_paths)

        db_time = time.time() - db_start_time
        total_time = time.time() - start_time

        self._loaded = True

        metrics = {
            "parsing_time": parsing_time,
            "db_time": db_time,
            "total_time": total_time,
            "frameworks_count": len(frameworks),
            "features_count": len(features),
            "absolute_paths_count": len(absolute_paths),
        }

        logger.info(f"Framework definitions loaded successfully: {metrics}")
        return metrics
