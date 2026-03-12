from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(examples=["demo.user@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["VerySecure123"])
    full_name: str = Field(min_length=2, max_length=120, examples=["Demo User"])


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(examples=["demo.user@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["VerySecure123"])


class TokenResponse(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo"])
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: str = Field(examples=["f0d4ef3d-5a7b-4a86-858f-d9f9d3027d7b"])
    email: EmailStr = Field(examples=["demo.user@example.com"])
    full_name: str = Field(examples=["Demo User"])
    role: str = Field(examples=["user"])
    created_at: datetime
    last_login_at: datetime | None = None

    model_config = {"from_attributes": True}
