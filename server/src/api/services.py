from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, HTTPException, Response
from sqlalchemy.future import select
from src.db import get_session
from src.config import Config
from src.api.models import User, UserAuth, Session, AuthProvider
from src.api.schemas import RegisterData, Tokens, LoginData
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
import bcrypt
import uuid
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger("auth")
logging.basicConfig(level=logging.INFO if Config.is_production else logging.DEBUG)


class PasswordService:
    """Handles password hashing and verification."""

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())


class JWTService:
    """Encapsulates all JWT logic: encoding, decoding, and expiration."""

    def __init__(self):
        self.jwt_secret = Config.JWT_SECRET
        self.jwt_refresh_secret = Config.JWT_REFRESH_SECRET
        self.access_expire_minutes = Config.ACCESS_EXPIRE_MINUTES
        self.refresh_expire_days = Config.REFRESH_EXPIRE_DAYS

    def generate_access_token(self, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self.access_expire_minutes
        )
        payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "exp": int(expire.timestamp()),
        }
        return encode(payload, self.jwt_secret, algorithm="HS256")

    def generate_refresh_token(self, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days)
        payload = {
            "user_id": str(user_id),
            "session_id": str(session_id),
            "exp": int(expire.timestamp()),
        }
        return encode(payload, self.jwt_refresh_secret, algorithm="HS256")

    def decode_token(self, token: str, refresh: bool = False) -> dict:
        try:
            secret = self.jwt_refresh_secret if refresh else self.jwt_secret
            return decode(token, secret, algorithms=["HS256"])
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


class AuthService:
    """Manages user registration, login, and session lifecycle."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_session),
        jwt_service: JWTService = Depends(JWTService),
        password_service: PasswordService = Depends(PasswordService),
    ):
        self.session = session
        self.jwt_service = jwt_service
        self.password_service = password_service
        self.cookie_name = Config.COOKIE_TOKEN

    # REGISTER
    async def register_user(self, data: RegisterData) -> Tokens:
        try:
            q = select(UserAuth).filter_by(email=data["email"])
            res = await self.session.execute(q)
            if res.scalars().one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already exists",
                )

            hashed_password = self.password_service.hash_password(data["password"])

            user = User(name=data["name"])
            self.session.add(user)
            await self.session.flush()

            user_auth = UserAuth(
                email=data["email"],
                password=hashed_password,
                user_id=user.id,
            )
            self.session.add(user_auth)

            session_user = Session(
                user_id=user.id,
                user_agent=data.get("user_agent"),
                ip_address=data.get("client_host"),
            )
            self.session.add(session_user)
            await self.session.flush()

            access_token = self.jwt_service.generate_access_token(
                user.id, session_user.id
            )
            refresh_token = self.jwt_service.generate_refresh_token(
                user.id, session_user.id
            )
            session_user.refresh_token = refresh_token

            await self.session.commit()
            logger.info(f"User registered successfully: {user.name}")

            return {"accessToken": access_token, "refreshToken": refresh_token}

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.exception("Registration failed: %s", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    # LOGIN
    async def login_user(self, data: LoginData) -> Tokens:
        try:
            q = select(UserAuth).filter_by(email=data["email"])
            res = await self.session.execute(q)
            user_auth = res.scalars().one_or_none()

            if not user_auth:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            q = select(User).filter_by(id=user_auth.user_id)
            res = await self.session.execute(q)
            user = res.scalars().one_or_none()

            if not user or not user.is_active:
                raise HTTPException(
                    status_code=401, detail="User inactive or not found"
                )

            if user_auth.provider != AuthProvider.EMAIL or not user_auth.password:
                raise HTTPException(status_code=401, detail="Not an email-auth user")

            if not self.password_service.verify_password(
                data["password"], user_auth.password
            ):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            session_user = Session(
                user_id=user.id,
                user_agent=data.get("user_agent"),
                ip_address=data.get("client_host"),
            )
            self.session.add(session_user)
            await self.session.flush()

            access_token = self.jwt_service.generate_access_token(
                user.id, session_user.id
            )
            refresh_token = self.jwt_service.generate_refresh_token(
                user.id, session_user.id
            )
            session_user.refresh_token = refresh_token

            await self.session.commit()
            logger.info(f"User logged in successfully: {user.name}")

            return {"accessToken": access_token, "refreshToken": refresh_token}

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.exception("Login failed: %s", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    # COOKIES
    def set_cookie_token(self, response: Response, token: str) -> None:
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True,
            samesite="none" if Config.is_production else "lax",
            secure=Config.is_production,
            path="/auth",
            max_age=7 * 24 * 60 * 60,
        )

    def delete_cookie_token(self, response: Response) -> None:
        response.delete_cookie(key=self.cookie_name)

    async def logout_user(self, token: str, response: Response):
        """Invalidate the current session and clear cookie."""
        try:
            payload = self.jwt_service.decode_token(token, refresh=True)
            session_id = payload.get("session_id")

            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session",
                )

            q = select(Session).filter_by(id=session_id, valid=True)
            res = await self.session.execute(q)
            session_obj = res.scalars().one_or_none()

            if not session_obj:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid session",
                )

            session_obj.valid = False
            await self.session.commit()
            self.delete_cookie_token(response)
            logger.info("User logged out successfully")

        except HTTPException:
            raise
        except Exception as e:
            await self.session.rollback()
            logger.exception("Logout failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}",
            )

    async def refresh_token(self, refresh_token: str, response: Response):
        return
