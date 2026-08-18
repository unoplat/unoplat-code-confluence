from xml.etree import ElementTree

from pydantic_ai import ModelRetry
import pytest

from unoplat_code_confluence_query_engine.tools.architecture_validation_tools import (
    _extract_icon_references,
    _validate_svg_image_references,
)


def test_extract_icon_references_includes_dotted_d2_paths() -> None:
    d2_text = """
icon: https://icons.d2lang.com/resources/aws/cloud.svg
api.icon: https://example.com/api.svg
service.backend.icon: "https://example.com/backend.svg"
"quoted.node".icon: 'https://example.com/quoted.svg'
"""

    assert _extract_icon_references(d2_text) == [
        "https://icons.d2lang.com/resources/aws/cloud.svg",
        "https://example.com/api.svg",
        "https://example.com/backend.svg",
        "https://example.com/quoted.svg",
    ]


@pytest.mark.parametrize(
    "reference",
    [
        "https://example.com/icon.svg",
        "//example.com/icon.svg",
        "file:///etc/passwd",
        "relative/icon.svg",
    ],
)
def test_validate_svg_image_references_rejects_unembedded_images(
    reference: str,
) -> None:
    svg_root = ElementTree.fromstring(
        f'<svg xmlns="http://www.w3.org/2000/svg"><image href="{reference}" /></svg>'
    )

    with pytest.raises(ModelRetry, match="unembedded image reference"):
        _validate_svg_image_references(svg_root)


def test_validate_svg_image_references_allows_embedded_images() -> None:
    svg_root = ElementTree.fromstring(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<image href="data:image/svg+xml;base64,PHN2Zy8+" />'
        "</svg>"
    )

    _validate_svg_image_references(svg_root)


def test_validate_svg_image_references_checks_xlink_and_feimage() -> None:
    svg_root = ElementTree.fromstring(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink">'
        '<filter><feImage xlink:href="https://example.com/filter.svg" /></filter>'
        "</svg>"
    )

    with pytest.raises(ModelRetry, match="https://example.com/filter.svg"):
        _validate_svg_image_references(svg_root)
