from datetime import datetime

from pydantic import BaseModel, Field


class DocumentPublic(BaseModel):
    id: str = Field(examples=["843f4b97-f68e-4b2d-a4ec-55691aaef4a6"])
    owner_id: str = Field(examples=["f0d4ef3d-5a7b-4a86-858f-d9f9d3027d7b"])
    original_filename: str = Field(examples=["company-policy.pdf"])
    content_type: str = Field(examples=["application/pdf"])
    size_bytes: int = Field(examples=[20480])
    processing_status: str = Field(examples=["ready"])
    summary_text: str | None = Field(
        default=None,
        examples=["This document defines the internal policy for secure document handling."],
    )
    tags: list[str] = Field(default_factory=list, examples=[["fakulteta", "poročilo"]])
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentTagsRequest(BaseModel):
    tags: list[str] = Field(max_length=20, examples=[["fakulteta", "poročilo"]])


class DocumentListResponse(BaseModel):
    items: list[DocumentPublic]
    total: int = Field(description="Total number of documents for the current user")
    skip: int = 0
    limit: int = 20


class DocumentQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, examples=["Kaj je glavni namen dokumenta?"])


class QuestionAnswerPublic(BaseModel):
    id: str = Field(examples=["2cbe6cb2-d85f-4bd8-bb18-7af860595032"])
    document_id: str = Field(examples=["843f4b97-f68e-4b2d-a4ec-55691aaef4a6"])
    question_text: str = Field(examples=["Kaj je glavni namen dokumenta?"])
    answer_text: str = Field(
        examples=["Glavni namen dokumenta je definirati varno ravnanje z internimi PDF dokumenti."],
    )
    source_mode: str = Field(examples=["fallback"])
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentInsightEntry(BaseModel):
    id: str
    original_filename: str
    processing_status: str
    size_bytes: int
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
    has_summary: bool
    answer_count: int = 0
    insight_score: int = Field(ge=0, le=100)
    badge: str
    reason_key: str


class InsightBreakdownItem(BaseModel):
    label: str
    count: int = Field(ge=0)


class InsightActionItem(BaseModel):
    key: str
    count: int = Field(ge=0, default=0)
    severity: str = Field(pattern="^(high|medium|low)$")


class DocumentInsightsOverview(BaseModel):
    total_documents: int = Field(ge=0)
    ready_documents: int = Field(ge=0)
    summary_documents: int = Field(ge=0)
    tagged_documents: int = Field(ge=0)
    documents_with_questions: int = Field(ge=0)
    total_questions: int = Field(ge=0)
    total_size_bytes: int = Field(ge=0)
    workspace_score: int = Field(ge=0, le=100)
    summary_coverage_pct: int = Field(ge=0, le=100)
    tag_coverage_pct: int = Field(ge=0, le=100)
    question_coverage_pct: int = Field(ge=0, le=100)


class DocumentInsightsActivity(BaseModel):
    uploads_last_7_days: int = Field(ge=0)
    questions_last_7_days: int = Field(ge=0)
    last_upload_at: datetime | None = None
    last_question_at: datetime | None = None


class DocumentInsightsResponse(BaseModel):
    overview: DocumentInsightsOverview
    activity: DocumentInsightsActivity
    status_breakdown: list[InsightBreakdownItem] = Field(default_factory=list)
    tag_breakdown: list[InsightBreakdownItem] = Field(default_factory=list)
    action_items: list[InsightActionItem] = Field(default_factory=list)
    most_active_documents: list[DocumentInsightEntry] = Field(default_factory=list)
    ready_for_review: list[DocumentInsightEntry] = Field(default_factory=list)
    needs_attention: list[DocumentInsightEntry] = Field(default_factory=list)
    recently_uploaded: list[DocumentInsightEntry] = Field(default_factory=list)
