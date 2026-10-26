from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

UserRole = Literal["ADMIN", "TEACHER", "STUDENT"]


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        min_length=1,
        max_length=50,
        title="Username",
        description="The unique username for the account.",
        examples=["24021400"],
    )
    fullName: str = Field(
        min_length=1,
        max_length=200,
        title="Full name",
        description="The user's full name.",
        examples=["Nguyen Trong Dai"],
    )
    password: str = Field(
        min_length=1,
        title="Password",
        description="The account password, which is stored as a secure hash.",
        examples=["IloveSoftwareArchitecture!"],
    )
    role: UserRole = Field(
        default="STUDENT",
        title="User role",
        description="The account role, which can be 'STUDENT', 'TEACHER', or 'ADMIN'.",
        examples=["STUDENT", "TEACHER", "ADMIN"],
    )

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
    id: int = Field(
        title="User ID",
        description="The unique ID of the account.",
        examples=[1],
    )
    username: str = Field(
        title="Username",
        description="The account username.",
        examples=["24021400"],
    )
    fullName: str = Field(
        title="Full name",
        description="The user's full name.",
        examples=["Nguyen Trong Dai"],
    )
    role: UserRole = Field(
        title="User role",
        description="The account role, which can be 'STUDENT', 'TEACHER', or 'ADMIN'.",
        examples=["STUDENT", "TEACHER", "ADMIN"],
    )
    createdAt: datetime = Field(
        title="Creation time",
        description="The time when the account was created.",
        examples=["2026-10-26T10:30:00Z"],
    )


class UserListResponse(BaseModel):
    users: list[UserResponse] = Field(
        title="Users",
        description="The accounts matching the supplied filters and pagination.",
        examples=[
            [
                {
                    "id": 1,
                    "username": "24021400",
                    "fullName": "Nguyen Trong Dai",
                    "role": "STUDENT",
                    "createdAt": "2026-10-26T10:30:00Z",
                }
            ]
        ],
    )


class UserDeleteResponse(BaseModel):
    success: Literal[True] = Field(
        title="Success",
        description="Indicates that the account was deleted successfully.",
        examples=[True],
    )
    message: str = Field(
        title="Message",
        description="A message describing the result of the operation.",
        examples=["Account deleted successfully"],
    )
