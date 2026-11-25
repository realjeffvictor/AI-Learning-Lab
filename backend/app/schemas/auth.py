from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.security import MAX_PASSWORD_LENGTH, check_password_policy
from app.schemas.user import UserRead


class RegisterRequest(BaseModel):
    # extra="forbid" blocks mass assignment: a client can never send "role": "admin".
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str
    display_name: str = Field(min_length=1, max_length=80)

    @field_validator("email")
    @classmethod
    def _lower_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("display_name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be empty.")
        return value

    @model_validator(mode="after")
    def _password_policy(self) -> "RegisterRequest":
        problem = check_password_policy(self.password, self.email)
        if problem:
            raise ValueError(problem)
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)

    @field_validator("email")
    @classmethod
    def _lower_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserRead
