from pydantic import BaseModel, EmailStr
from typing import TypedDict


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


class Tokens(TypedDict):
    accessToken: str
    refreshToken: str


class AuthResponse(TypedDict):
    success: bool
    accessToken: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    success: bool
    accessToken: str


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
