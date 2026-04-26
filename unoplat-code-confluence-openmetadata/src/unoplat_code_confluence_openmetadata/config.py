"""Configuration parsing for the Code Confluence OpenMetadata source."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator


class CodeConfluenceSourceConfig(BaseModel):
    """Validated connector settings supplied from the ingestion workflow YAML.

    The custom source expects these fields in
    ``source.serviceConnection.config.connectionOptions``.
    """

    query_engine_base_url: AnyHttpUrl = Field(alias="codeConfluenceApiBaseUrl")
    owner_name: str = Field(alias="repositoryOwnerName", min_length=1)
    repo_name: str = Field(alias="repositoryName", min_length=1)
    service_name: str | None = Field(default=None, alias="serviceName")
    timeout_seconds: float = Field(default=30.0, alias="timeoutSeconds", gt=0)

    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    @field_validator("owner_name", "repo_name")
    @classmethod
    def _must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value

    @field_validator("service_name")
    @classmethod
    def _blank_optional_string_as_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @property
    def normalized_query_engine_base_url(self) -> str:
        """Return the base URL without a trailing slash."""

        return str(self.query_engine_base_url).rstrip("/")


def parse_source_config(config_dict: Mapping[str, Any]) -> CodeConfluenceSourceConfig:
    """Extract and validate Code Confluence settings from workflow source config.

    Supported input shape:

    ``source.serviceConnection.config.connectionOptions``.

    All connector settings must be present in ``connectionOptions``.
    """

    raw_config = _extract_raw_config(config_dict)
    if not isinstance(raw_config, Mapping):
        raise ValueError("Code Confluence source config must be a mapping")

    return CodeConfluenceSourceConfig.model_validate(
        dict(cast(Mapping[str, Any], raw_config))
    )


def _extract_raw_config(config_dict: Mapping[str, Any]) -> object:
    service_connection = config_dict.get("serviceConnection")
    if isinstance(service_connection, Mapping):
        service_connection_config = service_connection.get("config")
        if isinstance(service_connection_config, Mapping):
            connection_options = service_connection_config.get("connectionOptions")
            if isinstance(connection_options, Mapping):
                return connection_options

    raise ValueError(
        "Code Confluence source config must be provided under "
        "serviceConnection.config.connectionOptions"
    )
