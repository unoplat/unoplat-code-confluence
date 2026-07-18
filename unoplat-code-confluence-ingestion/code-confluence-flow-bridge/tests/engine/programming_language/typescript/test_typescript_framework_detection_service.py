"""Regression tests for the TypeScript framework detection service."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from json import loads
from pathlib import Path
from typing import cast

import pytest
from unoplat_code_confluence_commons.base_models import (
    CallExpressionInfo,
    FeatureSpec,
    LocatorStrategy,
)

from code_confluence_flow_bridge.engine.programming_language.typescript import (
    typescript_framework_detection_service as service_module,
)
from code_confluence_flow_bridge.engine.programming_language.typescript.typescript_source_context import (
    TypeScriptSourceContext,
)


@pytest.mark.parametrize("local_binding", ["axios", "http_client"])
async def test_default_axios_import_loads_definition_and_detects_request(
    monkeypatch: pytest.MonkeyPatch,
    local_binding: str,
) -> None:
    definition_path = (
        Path(__file__).parents[4]
        / "framework-definitions"
        / "typescript"
        / "axios.json"
    )
    definition = loads(definition_path.read_text(encoding="utf-8"))
    operation = definition["typescript"]["axios"]["capabilities"]["http_client"][
        "operations"
    ]["request"]
    spec = FeatureSpec(
        capability_key="http_client",
        operation_key="request",
        library="axios",
        description=operation["description"],
        absolute_paths=operation["absolute_paths"],
        target_level=operation["target_level"],
        concept=operation["concept"],
        locator_strategy=LocatorStrategy.DIRECT,
        construct_query=operation["construct_query"],
        base_confidence=operation["base_confidence"],
    )
    queried_imports: list[str] = []

    @asynccontextmanager
    async def fake_session_cm() -> AsyncIterator[object]:
        yield object()

    async def fake_exact_import_query(
        _session: object,
        language: str,
        imports: list[str],
    ) -> list[FeatureSpec]:
        assert language == "typescript"
        queried_imports.extend(imports)
        if set(imports).intersection(spec.absolute_paths):
            return [spec]
        return []

    monkeypatch.setattr(service_module, "get_session_cm", fake_session_cm)
    monkeypatch.setattr(
        service_module,
        "get_framework_features_for_imports",
        fake_exact_import_query,
    )

    source = f'import {local_binding} from "axios"\n{local_binding}.get("/users")\n'
    context = TypeScriptSourceContext.from_bytes(source.encode("utf-8"))
    detections = await service_module.TypeScriptFrameworkDetectionService().detect_features(
        context,
        "typescript",
    )

    assert queried_imports == ["axios"]
    assert len(detections) == 1
    assert cast(CallExpressionInfo, detections[0]).callee == f"{local_binding}.get"
