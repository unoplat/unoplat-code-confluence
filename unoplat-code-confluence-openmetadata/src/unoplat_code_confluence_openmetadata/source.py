"""OpenMetadata Source implementation for Code Confluence snapshots."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from metadata.ingestion.api.models import Either
from metadata.ingestion.api.steps import Source
from metadata.ingestion.models.custom_pydantic import BaseModel
from metadata.ingestion.ometa.ometa_api import OpenMetadata

from unoplat_code_confluence_openmetadata.client import CodeConfluenceClient
from unoplat_code_confluence_openmetadata.config import (
    CodeConfluenceSourceConfig,
    parse_source_config,
)
from unoplat_code_confluence_openmetadata.glossary import publish_glossary
from unoplat_code_confluence_openmetadata.governance import publish_governance
from unoplat_code_confluence_openmetadata.mapper import OpenMetadataCreateRequest, iter_create_requests
from unoplat_code_confluence_openmetadata.models import RepositoryAgentSnapshotResponse


class CodeConfluenceSource(Source):
    """Custom ingestion source that emits API service/collection/endpoint requests."""

    def __init__(self, config: CodeConfluenceSourceConfig, metadata: OpenMetadata) -> None:
        super().__init__()
        self.metadata = metadata
        self.config = config
        self.client: CodeConfluenceClient | None = None
        self._snapshot: RepositoryAgentSnapshotResponse | None = None

    @classmethod
    def create(
        cls,
        config_dict: dict[str, Any],
        metadata: OpenMetadata,
        pipeline_name: str | None = None,
    ) -> "CodeConfluenceSource":
        """Create the source from an OpenMetadata workflow source config dict."""

        del pipeline_name
        source = cls(parse_source_config(config_dict), metadata)
        source.prepare()
        return source

    @property
    def name(self) -> str:
        return "CodeConfluenceSource"

    def prepare(self) -> None:
        """Initialize the query-engine client."""

        if self.client is None:
            self.client = CodeConfluenceClient(self.config)

    def test_connection(self) -> None:
        """Fetch and validate the configured snapshot once."""

        self._snapshot = self._fetch_snapshot()

    def _iter(self) -> Iterable[Either[OpenMetadataCreateRequest]]:
        """Yield OpenMetadata create requests for the configured repository run."""

        snapshot = self._snapshot or self._fetch_snapshot()
        metadata = cast(OpenMetadata[BaseModel, BaseModel], self.metadata)
        publish_glossary(metadata)
        publish_governance(metadata)
        yield from iter_create_requests(snapshot, self.config)

    def close(self) -> None:
        """Close the query-engine client."""

        if self.client is not None:
            self.client.close()
            self.client = None

    def _fetch_snapshot(self) -> RepositoryAgentSnapshotResponse:
        self.prepare()
        if self.client is None:  # pragma: no cover - defensive guard
            raise RuntimeError("Code Confluence client was not initialized")
        return self.client.fetch_repository_agent_snapshot()
