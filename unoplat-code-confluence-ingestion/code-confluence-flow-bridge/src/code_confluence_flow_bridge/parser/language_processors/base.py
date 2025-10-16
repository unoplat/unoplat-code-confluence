# Standard Library
from abc import ABC, abstractmethod
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Set

# Third Party
from loguru import logger

# First Party
from src.code_confluence_flow_bridge.models.code_confluence_parsing_models.unoplat_file import (
    UnoplatFile,
)
from src.code_confluence_flow_bridge.parser.language_processors.language_processor_context import (
    LanguageProcessorContext,
)


class LanguageCodebaseProcessor(ABC):
    """Base language-aware processor responsible for per-file parsing."""

    def __init__(self, context: LanguageProcessorContext) -> None:
        self.context = context

    @property
    @abstractmethod
    def supported_extensions(self) -> Set[str]:
        """Return file extensions supported by this language processor.

        Examples:
            - Python: {".py"}
            - TypeScript: {".ts", ".tsx"}
            - Java: {".java"}

        Returns:
            Set of file extensions including the leading dot.
        """
        pass

    @property
    @abstractmethod
    def ignored_file_names(self) -> Set[str]:
        """Return file names that should be ignored during parsing.

        This can include exact filenames or suffix patterns.

        Examples:
            - Python: {"__init__.py"}
            - TypeScript: {".d.ts"}
            - Java: {"package-info.java"}

        Returns:
            Set of filenames or patterns to ignore.
        """
        pass

    def should_ignore(self, file_path: Path) -> bool:
        """Determine if a file should be ignored based on language-specific rules.

        Default implementation checks:
        1. Exact filename match in ignored_file_names
        2. Suffix match for patterns starting with '.' (e.g., '.d.ts')

        Override this method for more complex ignore logic.

        Args:
            file_path: Path to the file to check

        Returns:
            True if file should be ignored, False otherwise
        """
        # Check exact filename match
        if file_path.name in self.ignored_file_names:
            return True

        # Check for suffix match (e.g., for .d.ts files)
        for ignored in self.ignored_file_names:
            if ignored.startswith(".") and file_path.name.endswith(ignored):
                return True

        return False

    async def iter_files(
        self, package_files: Dict[str, List[str]]
    ) -> AsyncGenerator[UnoplatFile, None]:
        """Yield processed files using configured concurrency."""
        for package_name, files in package_files.items():
            logger.info(
                "Processing files in package | package_name={} | file_count={}",
                package_name,
                len(files),
            )

        all_files = [f for files in package_files.values() for f in files]
        if not all_files:
            return

        file_iter = iter(all_files)
        concurrency_limit = self.context.concurrency_limit

        active_tasks = set()
        for _ in range(min(concurrency_limit, len(all_files))):
            try:
                file_path = next(file_iter)
            except StopIteration:
                break
            active_tasks.add(asyncio.create_task(self.extract_file_data(file_path)))

        while active_tasks:
            done, active_tasks = await asyncio.wait(
                active_tasks, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                try:
                    file_data = await task
                    if file_data:
                        self.context.increment_files_processed(1)
                        yield file_data
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    logger.error("Failed to process file task: {}", exc)

            while len(active_tasks) < concurrency_limit:
                try:
                    file_path = next(file_iter)
                except StopIteration:
                    break
                active_tasks.add(asyncio.create_task(self.extract_file_data(file_path)))

    @abstractmethod
    async def extract_file_data(self, file_path: str) -> Optional[UnoplatFile]:
        """Process a single file and return its parsed representation."""
