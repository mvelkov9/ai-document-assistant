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
