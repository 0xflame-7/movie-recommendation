from pydantic import BaseModel, EmailStr
from typing_extensions import TypedDict
from uuid import UUID


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    success: bool
    accessToken: str


class RegisterData(TypedDict):
    name: str
    email: EmailStr
    password: str
    user_agent: str | None
    client_host: str | None


class AuthResponse(TypedDict):
    success: bool
    accessToken: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginData(TypedDict):
    email: EmailStr
    password: str
    user_agent: str | None
    client_host: str | None


class RefreshResponse(BaseModel):
    success: bool
    accessToken: str


class LogoutResponse(BaseModel):
    success: bool


class AuthGuard(TypedDict):
    user_id: UUID
    session_id: UUID


class UserMe(TypedDict):
    name: str
    profilePic: str | None
