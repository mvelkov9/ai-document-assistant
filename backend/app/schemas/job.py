from datetime import datetime

from pydantic import BaseModel, Field


class ProcessingJobPublic(BaseModel):
    id: str = Field(examples=["16f1e8d4-d1fd-43b9-b17b-0a60a8479d49"])
    owner_id: str = Field(examples=["f0d4ef3d-5a7b-4a86-858f-d9f9d3027d7b"])
    document_id: str = Field(examples=["843f4b97-f68e-4b2d-a4ec-55691aaef4a6"])
    job_type: str = Field(examples=["summary"])
    status: str = Field(examples=["queued"])
    job_input: str | None = Field(default=None, examples=["Kaj je glavni namen dokumenta?"])
    result_text: str | None = Field(
        default=None,
        examples=["Glavni namen dokumenta je definirati varno ravnanje z internimi PDF dokumenti."],
    )
    error_message: str | None = Field(default=None, examples=[None])
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
