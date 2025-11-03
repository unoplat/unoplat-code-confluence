"""Mock workflow service that replays pre-recorded repository events."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger


class MockSSEService:
    """Load repository workflow events from JSON fixtures for mock runs."""

    def __init__(
        self,
        events_file_path: str | Path,
        result_file_path: str | Path | None = None,
    ) -> None:
        self.events_file_path = Path(events_file_path)
        self.result_file_path = (
            Path(result_file_path)
            if result_file_path
            else self.events_file_path.parent / "agent-md-result.json"
        )
        self.repository_name: str | None = None
        self.repository_workflow_run_id: str | None = None
        self._codebases: List[Dict[str, Any]] = []
        self._final_payload: Dict[str, Any] = {}
        self._load_fixture()

    def _load_fixture(self) -> None:
        try:
            raw = json.loads(self.events_file_path.read_text())
        except FileNotFoundError:
            logger.error("Mock events file not found at {}", self.events_file_path)
            return
        except json.JSONDecodeError as error:
            logger.error(
                "Mock events file {} could not be parsed: {}",
                self.events_file_path,
                error,
            )
            return

        self.repository_name = raw.get("repository_name")
        self.repository_workflow_run_id = raw.get("repository_workflow_run_id")
        self._codebases = raw.get("codebases", [])

        try:
            self._final_payload = json.loads(self.result_file_path.read_text())
        except FileNotFoundError:
            logger.warning(
                "Mock agent MD result file not found at {}", self.result_file_path
            )
            self._final_payload = {
                "repository": self.repository_name or "mock/repository",
                "codebases": {},
            }
        except json.JSONDecodeError as error:
            logger.warning(
                "Mock agent MD result file {} could not be parsed: {}",
                self.result_file_path,
                error,
            )
            self._final_payload = {
                "repository": self.repository_name or "mock/repository",
                "codebases": {},
            }

        logger.info(
            "Loaded mock workflow fixture with {} codebases from {}",
            len(self._codebases),
            self.events_file_path,
        )

    def has_events(self) -> bool:
        return bool(self._codebases)

    def iter_codebase_events(self) -> List[Dict[str, Any]]:
        return self._codebases

    def get_final_payload(self) -> Dict[str, Any]:
        return self._final_payload
