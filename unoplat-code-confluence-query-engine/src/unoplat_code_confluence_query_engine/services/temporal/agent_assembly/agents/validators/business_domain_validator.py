from __future__ import annotations

from pydantic_ai import ModelRetry


def validate_business_logic_domain_output(output: str) -> str:
    """Validate business logic domain output."""

    if not output or not output.strip():
        raise ModelRetry(
            "Output is empty. Return a plain text description (2-4 sentences) "
            "summarizing the business logic domain based on the data models analyzed."
        )

    stripped_output = output.strip()
    if stripped_output.startswith("{") or stripped_output.startswith("["):
        raise ModelRetry(
            "Return ONLY plain text (2-4 sentences), NOT JSON or structured data. "
            "Summarize the business logic domain in natural language."
        )
    return output
