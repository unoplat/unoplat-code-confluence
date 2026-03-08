from enum import Enum
from typing import Mapping

from ghapi.core import GhApi
from loguru import logger


class AppFeedbackCategory(str, Enum):
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"


class SentimentRating(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    UNHAPPY = "unhappy"


_CATEGORY_LABELS: dict[AppFeedbackCategory, str] = {
    AppFeedbackCategory.BUG_REPORT: "Bug Report",
    AppFeedbackCategory.FEATURE_REQUEST: "Feature Request",
    AppFeedbackCategory.GENERAL: "General",
}

_CATEGORY_GITHUB_LABELS: dict[AppFeedbackCategory, str] = {
    AppFeedbackCategory.BUG_REPORT: "bug",
    AppFeedbackCategory.FEATURE_REQUEST: "enhancement",
    AppFeedbackCategory.GENERAL: "feedback",
}

_SENTIMENT_EMOJIS: dict[SentimentRating, str] = {
    SentimentRating.HAPPY: "😊",
    SentimentRating.NEUTRAL: "😐",
    SentimentRating.UNHAPPY: "😞",
}

_TARGET_OWNER = "unoplat"
_TARGET_REPO = "unoplat-code-confluence"
_GITHUB_HOST = "https://api.github.com"


class AppFeedbackService:
    """Static service for creating GitHub issues from app feedback."""

    @staticmethod
    def build_issue_title(category: AppFeedbackCategory, subject: str) -> str:
        label = _CATEGORY_LABELS[category]
        return f"[{label}] {subject}"

    @staticmethod
    def build_issue_body(
        category: AppFeedbackCategory,
        sentiment: SentimentRating,
        description: str,
        current_route: str | None,
        app_version: str | None,
    ) -> str:
        emoji = _SENTIMENT_EMOJIS[sentiment]
        category_label = _CATEGORY_LABELS[category]

        sections: list[str] = [
            f"**Category:** {category_label}",
            f"**Sentiment:** {emoji} {sentiment.value.capitalize()}",
            "",
            "## Description",
            description,
        ]

        if current_route or app_version:
            sections.append("")
            sections.append("## Context")
            if current_route:
                sections.append(f"- **Page:** `{current_route}`")
            if app_version:
                sections.append(f"- **Version:** `{app_version}`")

        sections.append("")
        sections.append("---")
        sections.append("*Submitted via in-app feedback*")

        return "\n".join(sections)

    @staticmethod
    def create_github_issue(
        token: str,
        title: str,
        body: str,
        labels: list[str],
    ) -> Mapping[str, object]:
        api = GhApi(
            owner=_TARGET_OWNER,
            repo=_TARGET_REPO,
            token=token,
            gh_host=_GITHUB_HOST,
        )
        logger.info("Creating GitHub issue: {}", title)
        # ghapi dynamically generates API methods at runtime; basedpyright
        # cannot resolve them statically.  Suppress the resulting false-positive
        # type errors (upstream library limitation).
        result: Mapping[str, object] = api.issues.create(  # pyright: ignore[reportUnknownVariableType,reportUnknownMemberType,reportAttributeAccessIssue]
            title=title,
            body=body,
            labels=labels,
        )
        return result  # pyright: ignore[reportUnknownVariableType]

    @staticmethod
    def get_labels_for_category(category: AppFeedbackCategory) -> list[str]:
        return ["app-feedback", _CATEGORY_GITHUB_LABELS[category]]
