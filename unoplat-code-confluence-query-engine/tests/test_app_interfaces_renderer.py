"""Tests for canonical app-interface markdown rendering."""

from unoplat_code_confluence_query_engine.models.output.agent_md_output import (
    BidirectionalConstruct,
    BidirectionalKind,
    Interfaces,
    OutboundConstruct,
    OutboundKind,
)
from unoplat_code_confluence_query_engine.services.agents_md.rendering.app_interfaces.renderer import (
    render_app_interfaces,
)


def test_renderer_keeps_one_way_sections_and_renders_realtime_sync_evidence() -> None:
    interfaces = Interfaces(
        outbound_constructs=[
            OutboundConstruct(
                kind=OutboundKind.HTTP,
                library="axios",
                match_pattern={"src/api.ts": ["L8: apiClient.get('/users')"]},
            )
        ],
        bidirectional_constructs=[
            BidirectionalConstruct(
                kind=BidirectionalKind.REALTIME_SYNC,
                library="@tanstack/react-db",
                match_pattern={"src/hooks.ts": ["L20: useLiveQuery(query)"]},
            )
        ],
    )

    markdown = render_app_interfaces(interfaces)

    assert "## Inbound Constructs" in markdown
    assert "## Outbound Constructs" in markdown
    assert "### http_client (axios)" in markdown
    assert "`src/api.ts`: L8: apiClient.get('/users')" in markdown
    assert "## Bidirectional Constructs" in markdown
    assert "### realtime_sync (@tanstack/react-db)" in markdown
    assert "`src/hooks.ts`: L20: useLiveQuery(query)" in markdown
    assert "shape_subscription" not in markdown
    assert "live_changes" not in markdown
    assert "frontend →" not in markdown
    assert "## Internal Constructs" in markdown


def test_renderer_defaults_empty_bidirectional_section() -> None:
    markdown = render_app_interfaces(Interfaces())

    assert "## Bidirectional Constructs" in markdown
    assert "No bidirectional constructs detected." in markdown
