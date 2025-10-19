from fastapi import APIRouter, Depends, status, Request, Response, HTTPException
from src.api.schemas import (
    RegisterRequest,
    AuthResponse,
    LoginRequest,
    AuthGuard,
    UserMe,
)
from src.api.services import AuthService, UserService
from src.config import Config
from src.api.middleware import auth_guard

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: RegisterRequest,
    fastapi_request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
) -> AuthResponse:
    try:
        client_host: str | None = (
            fastapi_request.client.host if fastapi_request.client else None
        )
        user_agent: str | None = fastapi_request.headers.get("User-Agent")

        return AuthResponse(
            await auth_service.register_user(
                {
                    "name": request.name,
                    "email": request.email,
                    "password": request.password,
                    "user_agent": user_agent,
                    "client_host": client_host,
                },
                response,
            )
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@auth_router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    fastapi_request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
) -> AuthResponse:
    try:
        client_host: str | None = (
            fastapi_request.client.host if fastapi_request.client else None
        )
        user_agent: str | None = fastapi_request.headers.get("User-Agent")

        return AuthResponse(
            await auth_service.login_user(
                {
                    "email": request.email,
                    "password": request.password,
                    "user_agent": user_agent,
                    "client_host": client_host,
                },
                response,
            )
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@auth_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    auth_data: AuthGuard = Depends(auth_guard),
    auth_service: AuthService = Depends(),
):
    """
    Protected logout endpoint:
    - Requires a valid access token (via Authorization header)
    - Invalidates session and clears refresh token cookie
    """
    return await auth_service.logout_user(auth_data, response)


@auth_router.post(
    "/refresh", response_model=AuthResponse, status_code=status.HTTP_200_OK
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(),
) -> AuthResponse:
    try:
        refresh_token = request.cookies.get(Config.COOKIE_TOKEN)
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token found in cookies",
            )

        return AuthResponse(await auth_service.refresh_token(refresh_token, response))

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh token failed: {str(e)}",
        )


user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.get("/me", response_model=UserMe, status_code=status.HTTP_200_OK)
async def getMe(
    auth_data: AuthGuard = Depends(auth_guard), user_service: UserService = Depends()
) -> UserMe:
    return await user_service.get_user(auth_data["user_id"])
