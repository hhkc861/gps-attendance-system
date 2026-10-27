from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.user_schema import UserResponse


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(
        min_length=1,
        max_length=50,
        title="Username",
        description="The account username. Surrounding whitespace is removed.",
        examples=["admin", "24021400"],
    )
    password: str = Field(
        min_length=1,
        title="Password",
        description="The account password. Whitespace is preserved.",
        examples=["ExamplePassword123!"],
        json_schema_extra={"format": "password", "writeOnly": True},
    )

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Password must not be blank")
        return value


class LoginData(BaseModel):
    accessToken: str = Field(
        title="Access token",
        description="The JWT used to access protected endpoints.",
    )
    tokenType: Literal["Bearer"] = Field(
        default="Bearer",
        title="Token type",
        description="The token's authentication scheme.",
        examples=["Bearer"],
    )
    expiresIn: int = Field(
        title="Token lifetime in seconds",
        description="Token lifetime in seconds. Currently 1800 (30 minutes).",
        examples=[1800],
    )
    user: UserResponse = Field(
        title="Authenticated account",
        description="The logged-in account's public information.",
    )


class LoginResponse(BaseModel):
    success: Literal[True] = Field(
        default=True,
        title="Success",
        description="Whether login succeeded.",
        examples=[True],
    )
    message: str = Field(
        default="Login successful",
        title="Result message",
        description="The login result message.",
        examples=["Login successful"],
    )
    data: LoginData = Field(
        title="Login result",
        description="Token details and account information.",
    )
