from datetime import datetime, timezone
import traceback

from fastapi import APIRouter, Depends, HTTPException
from github import Github
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from unoplat_code_confluence_commons.base_models import (
    CodebaseWorkflowRun,
    RepositoryWorkflowRun,
)
from unoplat_code_confluence_commons.credential_enums import (
    CredentialNamespace,
    ProviderKey,
)

from src.code_confluence_flow_bridge.models.github.github_repo import (
    GithubIssueSubmissionRequest,
    IssueStatus,
    IssueTracking,
    IssueType,
)
from src.code_confluence_flow_bridge.processor.db.postgres.db import get_session
from src.code_confluence_flow_bridge.routers.github_issues.models import (
    AgentFeedbackSubmissionRequest,
    FeedbackCategory,
    SentimentRating,
)
from src.code_confluence_flow_bridge.utility.token_utils import (
    fetch_repository_provider_token,
)

router = APIRouter(prefix="/code-confluence", tags=["GitHub Issues"])

SENTIMENT_EMOJI_MAP = {
    SentimentRating.HAPPY: "😊",
    SentimentRating.NEUTRAL: "😐",
    SentimentRating.UNHAPPY: "😞",
}

CATEGORY_LABEL_MAP = {
    FeedbackCategory.ACCURACY: "Accuracy issues",
    FeedbackCategory.MISSING: "Missing information",
    FeedbackCategory.OTHER: "Other",
}


@router.post("/issues", response_model=IssueTracking)
async def create_github_issue(
    request: GithubIssueSubmissionRequest,
    session: AsyncSession = Depends(get_session),
) -> IssueTracking:
    """
    Create a GitHub issue based on error information and track it in the database.

    This endpoint creates a GitHub issue using the provided error information and then updates
    either the codebase workflow run or repository workflow run record with the issue details.
    """
    try:
        token, _ = await fetch_repository_provider_token(
            session, CredentialNamespace.REPOSITORY, ProviderKey.GITHUB_OPEN
        )

        title = (
            f"Error: {request.error_message_body[:50]}..."
            if len(request.error_message_body) > 50
            else f"Error: {request.error_message_body}"
        )
        body = f"## Error Details\n\n{request.error_message_body}\n\n"

        body += "## Workflow Information\n\n"
        body += (
            f"- Repository: {request.repository_owner_name}/{request.repository_name}\n"
        )

        if request.codebase_folder:
            body += f"- Codebase Folder: {request.codebase_folder}\n"

        github_issue_data = {
            "title": title,
            "body": body,
            "labels": ["bug", "automated"],
        }

        try:
            g = Github(token)
            repo = g.get_repo("unoplat/unoplat-code-confluence")
            labels = github_issue_data["labels"]
            github_issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels,  # type: ignore
            )
        except Exception as e:
            logger.error("GitHub API error: {}", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to create GitHub issue: {str(e)}"
            )

        issue_tracking = IssueTracking(
            issue_id=str(github_issue.id),
            issue_url=github_issue.html_url,
            issue_status=IssueStatus.OPEN,
        )

        issue_tracking_full = IssueTracking(
            issue_id=issue_tracking.issue_id,
            issue_number=github_issue.number,
            issue_url=issue_tracking.issue_url,
            issue_status=issue_tracking.issue_status,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        issue_data = issue_tracking_full.model_dump()

        if (
            request.error_type == IssueType.CODEBASE
            and request.codebase_workflow_run_id
        ):
            condition = (
                (CodebaseWorkflowRun.repository_name == request.repository_name)
                & (
                    CodebaseWorkflowRun.repository_owner_name
                    == request.repository_owner_name
                )
                & (CodebaseWorkflowRun.codebase_folder == request.codebase_folder)
                & (
                    CodebaseWorkflowRun.codebase_workflow_run_id
                    == request.codebase_workflow_run_id
                )
            )  # type: ignore
            codebase_run_query = select(CodebaseWorkflowRun).where(condition)
            codebase_run_result = await session.execute(codebase_run_query)
            codebase_run = codebase_run_result.scalar_one_or_none()

            if not codebase_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Codebase workflow run {request.codebase_workflow_run_id} not found",
                )

            codebase_run.issue_tracking = issue_data

        else:
            condition = (
                (RepositoryWorkflowRun.repository_name == request.repository_name)
                & (
                    RepositoryWorkflowRun.repository_owner_name
                    == request.repository_owner_name
                )
                & (
                    RepositoryWorkflowRun.repository_workflow_run_id
                    == request.parent_workflow_run_id
                )
            )  # type: ignore
            repo_run_query = select(RepositoryWorkflowRun).where(condition)
            repo_run_result = await session.execute(repo_run_query)
            repo_run = repo_run_result.scalar_one_or_none()

            if not repo_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Repository workflow run {request.parent_workflow_run_id} not found",
                )

            repo_run.issue_tracking = issue_data

        return issue_tracking_full

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error creating GitHub issue: {}", str(e))
        workflow_context = {
            "workflow_id": request.parent_workflow_run_id,
            "repository": f"{request.repository_owner_name}/{request.repository_name}",
        }
        if (
            request.error_type == IssueType.CODEBASE
            and request.codebase_workflow_run_id
        ):
            workflow_context["codebase_workflow_run_id"] = (
                request.codebase_workflow_run_id
            )
            if request.codebase_folder:
                workflow_context["codebase_folder"] = request.codebase_folder

        error_context = {
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "workflow_context": workflow_context,
        }

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Faced an error while creating GitHub issue. Please try after some time.",
                "error_context": error_context,
            },
        )


@router.post("/feedback", response_model=IssueTracking)
async def submit_agent_feedback(
    request: AgentFeedbackSubmissionRequest,
    session: AsyncSession = Depends(get_session),
) -> IssueTracking:
    """
    Submit feedback for agent generation as a GitHub issue.

    This endpoint creates a GitHub issue with structured feedback including
    overall rating, per-agent ratings, categories, and comments.
    """
    try:
        token, _ = await fetch_repository_provider_token(
            session, CredentialNamespace.REPOSITORY, ProviderKey.GITHUB_OPEN
        )

        title = f"Feedback: Agent Generation for {request.repository_owner_name}/{request.repository_name}"

        overall_emoji = SENTIMENT_EMOJI_MAP.get(request.overall_rating, "")
        body = f"## Agent Generation Feedback\n\n"
        body += f"**Overall Rating:** {overall_emoji} {request.overall_rating.value.capitalize()}\n\n"

        body += "## Workflow Information\n\n"
        body += (
            f"- Repository: {request.repository_owner_name}/{request.repository_name}\n"
        )
        body += f"- Workflow Run ID: {request.parent_workflow_run_id}\n\n"

        if request.agent_ratings:
            body += "## Per-Agent Ratings\n\n"
            body += "| Codebase | Agent | Rating |\n"
            body += "|----------|-------|--------|\n"
            for agent_rating in request.agent_ratings:
                if agent_rating.rating:
                    emoji = SENTIMENT_EMOJI_MAP.get(agent_rating.rating, "")
                    body += f"| {agent_rating.codebase_name} | {agent_rating.agent_id} | {emoji} {agent_rating.rating.value.capitalize()} |\n"
            body += "\n"

        if request.categories:
            body += "## Feedback Categories\n\n"
            for category in request.categories:
                label = CATEGORY_LABEL_MAP.get(category, category.value)
                body += f"- {label}\n"
            body += "\n"

        if request.comments:
            body += "## Comments\n\n"
            body += f"{request.comments}\n"

        try:
            g = Github(token)
            repo = g.get_repo("unoplat/unoplat-code-confluence")
            github_issue = repo.create_issue(
                title=title,
                body=body,
                labels=["feedback", "agent-generation"],  # type: ignore
            )
        except Exception as e:
            logger.error("GitHub API error: {}", str(e))
            raise HTTPException(
                status_code=500, detail=f"Failed to create feedback issue: {str(e)}"
            )

        issue_tracking_full = IssueTracking(
            issue_id=str(github_issue.id),
            issue_number=github_issue.number,
            issue_url=github_issue.html_url,
            issue_status=IssueStatus.OPEN,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return issue_tracking_full

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error submitting agent feedback: {}", str(e))
        error_context = {
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "workflow_context": {
                "workflow_id": request.parent_workflow_run_id,
                "repository": f"{request.repository_owner_name}/{request.repository_name}",
            },
        }

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Faced an error while submitting feedback. Please try after some time.",
                "error_context": error_context,
            },
        )
