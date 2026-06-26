from __future__ import annotations

from python_on_whales import DockerClient
from python_on_whales.client_config import ClientNotFoundError
from python_on_whales.exceptions import DockerException

from unoplat_code_confluence_cli.config import CliSettings
from unoplat_code_confluence_cli.errors import DockerRuntimeError


class WhalesDockerComposeManager:
    def __init__(self, settings: CliSettings) -> None:
        self._docker = DockerClient(
            compose_files=[settings.compose_file_path],
            compose_project_name=settings.compose_project_name,
        )

    def ensure_available(self) -> None:
        try:
            if not self._docker.compose.is_installed():
                raise DockerRuntimeError(
                    "Docker Compose is required to auto-start Unoplat Code Confluence. "
                    "Install/enable the Docker Compose plugin and ensure `docker compose version` works."
                )
        except ClientNotFoundError as exc:
            raise DockerRuntimeError(
                "Docker is required to auto-start Unoplat Code Confluence, but the "
                "docker executable was not found. Install Docker Desktop or Docker Engine "
                "with the Compose plugin, then retry."
            ) from exc
        except DockerException as exc:
            raise DockerRuntimeError(
                "Docker Compose is required to auto-start Unoplat Code Confluence. "
                "Install/enable the Docker Compose plugin and ensure `docker compose version` works."
            ) from exc

    def pull_images(self) -> None:
        try:
            self._docker.compose.pull()
        except (ClientNotFoundError, DockerException) as exc:
            self._raise_docker_runtime_error("Docker Compose pull failed", exc)

    def start_stack(self) -> None:
        try:
            self._docker.compose.up(detach=True)
        except (ClientNotFoundError, DockerException) as exc:
            self._raise_docker_runtime_error("Docker Compose up failed", exc)

    def stop_stack(self, *, volumes: bool) -> None:
        try:
            self._docker.compose.down(volumes=volumes)
        except (ClientNotFoundError, DockerException) as exc:
            self._raise_docker_runtime_error("Docker Compose down failed", exc)

    def _raise_docker_runtime_error(
        self, message: str, exc: ClientNotFoundError | DockerException
    ) -> None:
        if isinstance(exc, ClientNotFoundError):
            raise DockerRuntimeError(
                "Docker is required to auto-start Unoplat Code Confluence, but the "
                "docker executable was not found. Install Docker Desktop or Docker Engine "
                "with the Compose plugin, then retry."
            ) from exc

        details = exc.stderr or exc.stdout or str(exc)
        raise DockerRuntimeError(f"{message}: {details}") from exc
