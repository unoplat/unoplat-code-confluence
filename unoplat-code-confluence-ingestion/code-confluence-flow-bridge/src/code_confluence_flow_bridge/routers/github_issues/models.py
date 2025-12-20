from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SentimentRating(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    UNHAPPY = "unhappy"


class FeedbackCategory(str, Enum):
    ACCURACY = "accuracy"
    MISSING = "missing"
    OTHER = "other"


class AgentRating(BaseModel):
    codebase_name: str = Field(description="Name of the codebase")
    agent_id: str = Field(description="Identifier of the agent")
    rating: Optional[SentimentRating] = Field(
        default=None, description="Optional sentiment rating for this agent"
    )


class AgentFeedbackSubmissionRequest(BaseModel):
    repository_name: str = Field(description="The name of the repository")
    repository_owner_name: str = Field(description="The name of the repository owner")
    parent_workflow_run_id: str = Field(description="The run ID of the parent workflow")
    overall_rating: SentimentRating = Field(
        description="Overall sentiment rating for the agent generation"
    )
    agent_ratings: Optional[List[AgentRating]] = Field(
        default=None, description="Optional per-agent ratings for detailed feedback"
    )
    categories: List[FeedbackCategory] = Field(
        default_factory=list, description="Categories of feedback"
    )
    comments: Optional[str] = Field(
        default=None, description="Optional free-form comments"
    )
