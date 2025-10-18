from fastapi import APIRouter, Depends, status, Request, Response
from src.api.schemas import RegisterRequest, RegisterResponse
from src.api.services import AuthService
# from src.db import get_session
# from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

# def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
#   return AuthService(session)

@router.post(
  "/register",
  response_model=RegisterResponse, 
  status_code=status.HTTP_201_CREATED)
async def register(
  request: RegisterRequest,
  fastapi_request: Request,
  response: Response,
  auth_service: AuthService = Depends()
):
  client_host = fastapi_request.client.host if fastapi_request.client else None
  user_agent = fastapi_request.headers.get("User-Agent")

  tokens = await auth_service.register_user({
    "name": request.name, 
    "email":request.email, 
    "password":request.password, 
    "user_agent":user_agent, 
    "client_host":client_host
  })
  
  auth_service.set_cookie_token(response, tokens['refreshToken'])

  return {
    "success": True,
    "accessToken": tokens['accessToken']
  }
