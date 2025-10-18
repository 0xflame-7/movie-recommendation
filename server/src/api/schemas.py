from pydantic import BaseModel
from typing import TypedDict

class RegisterRequest(BaseModel):
  name: str
  email: str
  password: str

class RegisterResponse(BaseModel):
  success: bool
  accessToken: str

class LoginRequest(BaseModel):
  email: str
  password: str

class LoginResponse(BaseModel):
  success: bool
  accessToken: str

class RegisterData(TypedDict):
  name: str
  email: str
  password: str
  user_agent: str | None
  client_host: str | None