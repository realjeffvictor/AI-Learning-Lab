import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Role = Literal["student", "instructor", "admin"]
ExperienceLevel = Literal["beginner", "intermediate", "advanced"]


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_name: str
    bio: str | None
    experience_level: ExperienceLevel


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: Role
    is_active: bool
    created_at: datetime
    last_login_at: datetime | None
    profile: ProfileRead


class UserPage(BaseModel):
    items: list[UserRead]
    page: int
    page_size: int
    total: int


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    bio: str | None = Field(default=None, max_length=500)
    experience_level: ExperienceLevel | None = None

    @field_validator("display_name")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Display name cannot be empty.")
        return value

    @field_validator("bio")
    @classmethod
    def _blank_bio_is_none(cls, value: str | None) -> str | None:
        return (value.strip() or None) if value is not None else None

    @model_validator(mode="after")
    def _required_fields_not_null(self) -> "ProfileUpdate":
        for name in ("display_name", "experience_level"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null.")
        return self


class AdminUserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Role | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def _at_least_one(self) -> "AdminUserUpdate":
        provided = {name: getattr(self, name) for name in self.model_fields_set}
        if not provided or any(value is None for value in provided.values()):
            raise ValueError("Provide role and/or is_active with non-null values.")
        return self
