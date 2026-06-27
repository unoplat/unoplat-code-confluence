from __future__ import annotations

import os
from pathlib import Path

from pydantic import ValidationError

from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.domain.release import ReleaseState
from unoplat_code_confluence_cli.errors import ReleaseError


class FileReleaseStore:
    def __init__(self, settings: CliSettings) -> None:
        self._settings = settings

    @property
    def compose_file_path(self) -> Path:
        return self._settings.compose_file_path

    @property
    def release_state_path(self) -> Path:
        return self._settings.release_state_path

    def read_release_state(self) -> ReleaseState | None:
        path = self.release_state_path
        if not path.exists():
            return None
        try:
            return ReleaseState.model_validate_json(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ReleaseError(f"Unable to read local release state at {path}: {exc}") from exc
        except ValidationError as exc:
            raise ReleaseError(
                f"Local release state at {path} does not match schema_version 1."
            ) from exc

    def write_release_state(self, state: ReleaseState) -> None:
        atomic_write_text(
            self.release_state_path,
            state.model_dump_json(indent=2) + "\n",
        )

    def write_compose_file(self, content: str) -> None:
        atomic_write_text(self.compose_file_path, content)

    def compose_file_exists(self) -> bool:
        return self.compose_file_path.exists()


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    os.replace(temp_path, path)
