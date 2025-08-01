import os
import json
import logging
import pathlib
import time
from typing import Any, Dict, List, Tuple

from code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)
from code_confluence_flow_bridge.processor.db.postgres.custom_grammar_metadata import (
    FeatureAbsolutePath,
    Framework,
    FrameworkFeature,
)
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class FrameworkDefinitionLoader:
    """Handles bulk loading of framework definitions at application startup."""
    
    def __init__(self, env_settings: EnvironmentSettings):
        """Initialize loader with path from environment settings."""
        self.definitions_path = pathlib.Path(env_settings.framework_definitions_path)
        self._loaded = False
        
        # Debug environment variable loading
        logger.info(f"Environment variable FRAMEWORK_DEFINITIONS_PATH: {os.getenv('FRAMEWORK_DEFINITIONS_PATH', 'NOT SET')}")
        logger.info(f"Settings framework_definitions_path: {env_settings.framework_definitions_path}")
        logger.info(f"FrameworkDefinitionLoader initialized with path: {self.definitions_path}")
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Absolute definitions path: {self.definitions_path.resolve()}")
        logger.debug(f"Path exists: {self.definitions_path.exists()}")
        
    def load_framework_definitions(self) -> Dict[str, Any]:
        """Load and combine all framework definition JSON files."""
        python_dir = self.definitions_path / "python"
        
        logger.info(f"Loading framework definitions from: {self.definitions_path}")
        logger.debug(f"Python directory path: {python_dir.resolve()}")
        
        if not python_dir.exists():
            raise FileNotFoundError(f"Framework definitions python directory not found: {python_dir.resolve()}")
        
        combined_data: Dict[str, Dict[str, Any]] = {}
        json_files = list(python_dir.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {python_dir}")
            return combined_data
        
        logger.info(f"Loading framework definitions from {len(json_files)} files in {python_dir}")
        
        for json_file in json_files:
            try:
                logger.debug(f"Loading framework definition from {json_file}")
                file_data = json.loads(json_file.read_text())
                
                # Merge data from each file (language -> library -> features structure)
                for language, language_data in file_data.items():
                    if language not in combined_data:
                        combined_data[language] = {}
                    combined_data[language].update(language_data)
                    
            except Exception as e:
                logger.error(f"Failed to load framework definition from {json_file}: {e}")
                raise
        
        logger.info(f"Successfully loaded framework definitions from {len(json_files)} files")
        return combined_data
    
    def parse_json_data(self, data: Dict[str, Any]) -> Tuple[List[Framework], List[FrameworkFeature], List[FeatureAbsolutePath]]:
        """Parse JSON data into normalized database records."""
        frameworks = []
        features = []
        absolute_paths = []
        
        # Track unique frameworks to avoid duplicates
        seen_frameworks = set()
        
        logger.debug("Parsing framework definitions into SQLModel objects")
        
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
                        construct_query=feature_data.get("construct_query"),
                        startpoint=feature_data.get("startpoint", False)
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
        
        logger.info(f"Parsed {len(frameworks)} frameworks, {len(features)} features, {len(absolute_paths)} absolute paths")
        return frameworks, features, absolute_paths
    
    async def load_framework_definitions_at_startup(self, session: AsyncSession) -> Dict[str, Any]:
        """
        Load framework definitions at startup with optimized bulk insertion.
        Uses atomic clear + repopulate strategy for consistency.
        """
        logger.info("Starting framework definitions loading...")
        start_time = time.time()
        
        # Check if already loaded (idempotency)
        existing_count: int = await session.scalar(select(func.count(Framework.language))) or 0 #type: ignore
        if existing_count > 0 and self._loaded:
            logger.info(f"Framework definitions already loaded ({existing_count} frameworks). Skipping.")
            return {"skipped": True, "existing_count": existing_count}
        
        # Load and parse definitions
        framework_data = self.load_framework_definitions()
        frameworks, features, absolute_paths = self.parse_json_data(framework_data)
        parsing_time = time.time() - start_time
        
        logger.info(f"Parsed {len(frameworks)} frameworks, {len(features)} features, {len(absolute_paths)} paths in {parsing_time:.3f}s")
        
        # Atomic operation: clear existing + repopulate
        db_start_time = time.time()
        
        # Clear in correct order (foreign key dependencies)
        logger.debug("Clearing existing framework definitions...")
        
        
        await session.execute(delete(FeatureAbsolutePath)) #type: ignore
        await session.execute(delete(FrameworkFeature)) #type: ignore
        await session.execute(delete(Framework)) #type: ignore
        
        
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
    