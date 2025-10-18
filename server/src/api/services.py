from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, status, HTTPException, Response
from src.db import get_session
from src.config import Config
from sqlalchemy.future import select
from src.api.models import User, UserAuth, Session
from jwt import encode, decode
import bcrypt
import uuid
from datetime import datetime, timezone, timedelta
from src.api.schemas import RegisterData

class AuthService:
  def __init__(self, session: AsyncSession = Depends(get_session)):
    self.session = session
    self.jwt_secret = Config.JWT_SECRET
    self.jwt_refresh_secret = Config.JWT_REFRESH_SECRET
    self.access_expire_minutes = Config.ACCESS_EXPIRE_MINUTES
    self.refresh_expire_days = Config.REFRESH_EXPIRE_DAYS
    self.cookie_name = Config.COOKIE_TOKEN

  async def register_user(self, data: RegisterData) -> dict[str, str]:
    print(data)
    q = select(UserAuth).filter_by(email=data["email"])
    res = await self.session.execute(q)
    user = res.scalars().one_or_none()

    if user:
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already exists")
    
    data["password"] = self.secure_hash(data["password"])

    # create User 
    user = User(name=data["name"])
    self.session.add(user)
    await self.session.flush()

    # create UserAuth
    user_auth = UserAuth(
      email= data["email"],
      password= data["password"],
      user_id = user.id
    )    
    self.session.add(user_auth)

    # create Session
    sessionUser = Session(
      user_id=user.id,
      user_agent=data["user_agent"],
      ip_address=data["client_host"]  
    )
    self.session.add(sessionUser)
    await self.session.flush()

    accessToken: str = self.generate_access_token(user.id, sessionUser.id)
    refreshToken: str = self.generate_refresh_token(user.id, sessionUser.id)

    sessionUser.refresh_token = refreshToken
    await self.session.commit()
    return {"refreshToken": refreshToken, "accessToken": accessToken}

  def secure_hash(self, password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

  def verify_password(self, password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

  def generate_access_token(self, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_expire_minutes)
    payload = {"user_id": str(user_id), "session_id": str(session_id), "expire": expire.isoformat()}
    return encode(payload, self.jwt_secret, algorithm="HS256")

  def generate_refresh_token(self, user_id: uuid.UUID, session_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_expire_days)
    payload = {"user_id": str(user_id), "session_id": str(session_id), "expire": expire.isoformat()}
    return encode(payload, self.jwt_refresh_secret, algorithm="HS256")
  
  def set_cookie_token(self, response: Response, token: str, httponly: bool = True) -> None:
    response.set_cookie(
      key=self.cookie_name, 
      value=token, 
      httponly=httponly, 
      samesite="lax", 
      secure=False, 
      path="/auth",
      max_age=7 * 24 * 60 * 60
    )