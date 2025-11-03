# Standard Library
from pathlib import Path
from typing import Callable, List, Optional

# Third Party
from pydantic import BaseModel, ConfigDict
from unoplat_code_confluence_commons.base_models import ProgrammingLanguageMetadata

# First Party
from src.code_confluence_flow_bridge.engine.framework_detection_service import (
    FrameworkDetectionService,
)
from src.code_confluence_flow_bridge.models.configuration.settings import (
    EnvironmentSettings,
)


class LanguageProcessorContext(BaseModel):
    """Runtime context shared with language-specific processors."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    codebase_name: str
    codebase_path: Path
    root_packages: List[str]
    programming_language_metadata: ProgrammingLanguageMetadata
    env_config: EnvironmentSettings
    framework_detection_service: Optional[FrameworkDetectionService] = None
    concurrency_limit: int
    increment_files_processed: Callable[[int], None]
