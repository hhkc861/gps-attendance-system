from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


UserRole = Literal["ADMIN", "teacher", "STUDENT"]


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=50)
    fullName: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=1)
    role: UserRole = "STUDENT"

    @field_validator("username", "fullName", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password must not be blank")
        return value


class UserResponse(BaseModel):
    id: str
    username: str
    fullName: str
    role: UserRole
    createdAt: datetime


class UserCreateResponse(BaseModel):
    success: Literal[True] = True
    message: str = "Account created successfully"
    data: UserResponse
