from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from src.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    Tokens,
    LoginRequest,
    LoginResponse,
)
from src.api.services import AuthService
from src.config import Config

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    fastapi_request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
) -> RegisterResponse:
    try:
        client_host: str | None = (
            fastapi_request.client.host if fastapi_request.client else None
        )
        user_agent: str | None = fastapi_request.headers.get("User-Agent")

        tokens: Tokens = await auth_service.register_user(
            {
                "name": request.name,
                "email": request.email,
                "password": request.password,
                "user_agent": user_agent,
                "client_host": client_host,
            }
        )

        auth_service.set_cookie_token(response, tokens["refreshToken"])
        return RegisterResponse(success=True, accessToken=tokens["accessToken"])

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    fastapi_request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
) -> LoginResponse:
    try:
        client_host: str | None = (
            fastapi_request.client.host if fastapi_request.client else None
        )
        user_agent: str | None = fastapi_request.headers.get("User-Agent")

        tokens: Tokens = await auth_service.login_user(
            {
                "email": request.email,
                "password": request.password,
                "user_agent": user_agent,
                "client_host": client_host,
            }
        )

        auth_service.set_cookie_token(response, tokens["refreshToken"])
        return LoginResponse(success=True, accessToken=tokens["accessToken"])

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
):
    try:
        refresh_token = request.cookies.get(Config.COOKIE_TOKEN)
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token found in cookies",
            )

        await auth_service.logout_user(refresh_token, response)
        return

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        )


@router.post("/refresh", response_model=Tokens, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
):
    try:
        refresh_token = request.cookies.get(Config.COOKIE_TOKEN)
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token found in cookies",
            )

        return await auth_service.refresh_token(refresh_token, response)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh token failed: {str(e)}",
        )
