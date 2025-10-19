# src/api/middleware/auth_guard.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.db import get_session
from src.api.models import User, Session
from src.api.services import JWTService
import uuid
from src.api.schemas import AuthGuard


async def auth_guard(
    request: Request,
    db: AsyncSession = Depends(get_session),
    jwt_service: JWTService = Depends(JWTService),
) -> AuthGuard:
    """
    Middleware-style dependency to protect routes by verifying access tokens.
    """

    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
        )

    token = auth_header.split(" ")[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed authorization header",
        )

    # Decode access token
    payload = jwt_service.decode_token(token, refresh=False)
    user_id = payload.get("user_id")
    session_id = payload.get("session_id")

    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_id = uuid.UUID(user_id)
    session_id = uuid.UUID(session_id)

    # Validate user
    q_user = select(User).filter_by(id=user_id, is_active=True)
    res_user = await db.execute(q_user)
    user = res_user.scalars().one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Validate session
    q_session = select(Session).filter_by(id=session_id, user_id=user_id, valid=True)
    res_session = await db.execute(q_session)
    session_obj = res_session.scalars().one_or_none()

    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    # Attach user info to request.state
    request.state.user_id = user_id
    request.state.session_id = session_id

    return {"user_id": user_id, "session_id": session_id}
