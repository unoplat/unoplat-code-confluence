from typing import Optional

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field
from unoplat_code_confluence_commons.credential_enums import ProviderKey

from unoplat_code_confluence_query_engine.db.postgres.db import get_startup_session
from unoplat_code_confluence_query_engine.services.config.credentials_service import (
    CredentialsService,
)
from unoplat_code_confluence_query_engine.services.feedback.app_feedback_service import (
    AppFeedbackCategory,
    AppFeedbackService,
    SentimentRating,
)

router = APIRouter(prefix="/v1/app-feedback", tags=["app-feedback"])


class AppFeedbackRequest(BaseModel):
    category: AppFeedbackCategory
    sentiment: SentimentRating
    subject: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=10, max_length=2000)
    current_route: Optional[str] = None
    app_version: Optional[str] = None


class AppFeedbackResponse(BaseModel):
    issue_url: Optional[str] = None
    issue_number: Optional[int] = None


@router.post("", response_model=AppFeedbackResponse)
async def submit_app_feedback(
    request: AppFeedbackRequest,
) -> AppFeedbackResponse:
    """Submit general app feedback as a GitHub issue."""
    async with get_startup_session() as session:
        pat = await CredentialsService.get_repository_pat(
            session, ProviderKey.GITHUB_OPEN
        )

    if not pat:
        raise HTTPException(
            status_code=422,
            detail="GitHub PAT not configured. Please configure GitHub credentials first.",
        )

    title = AppFeedbackService.build_issue_title(request.category, request.subject)
    body = AppFeedbackService.build_issue_body(
        category=request.category,
        sentiment=request.sentiment,
        description=request.description,
        current_route=request.current_route,
        app_version=request.app_version,
    )
    labels = AppFeedbackService.get_labels_for_category(request.category)

    try:
        result = AppFeedbackService.create_github_issue(
            token=pat,
            title=title,
            body=body,
            labels=labels,
        )
    except Exception:
        logger.exception("Failed to create GitHub issue for app feedback")
        raise HTTPException(
            status_code=500,
            detail="Failed to create GitHub issue. Please try again later.",
        )

    issue_url: str | None = None
    issue_number: int | None = None

    if isinstance(result, dict):
        raw_url = result.get("html_url")
        if isinstance(raw_url, str):
            issue_url = raw_url
        raw_number = result.get("number")
        if isinstance(raw_number, int):
            issue_number = raw_number

    return AppFeedbackResponse(issue_url=issue_url, issue_number=issue_number)
