from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime, timezone
from enum import Enum


class User(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False)
    profilePic: str | None = Field(default=None)
    email_verified: bool | None = Field(default=False, nullable=False)
    is_active: bool | None = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthProvider(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"


class UserAuth(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    provider: AuthProvider | None = Field(default=AuthProvider.EMAIL, nullable=False)

    email: str = Field(nullable=False, index=True, unique=True)
    password: str | None = Field(default=None, nullable=True, repr=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Session(SQLModel, table=True):

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)

    user_agent: str | None = Field(default=None, nullable=True)
    ip_address: str | None = Field(default=None, nullable=True)
    refresh_token: str = Field(default=None, nullable=True, repr=False)
    valid: bool | None = Field(default=True, nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
