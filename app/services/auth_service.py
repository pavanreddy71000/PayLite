from app.services.user_service import pwd_context, get_user_by_email
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from jose import jwt, JWTError
from app.exceptions import AuthenticationError
from fastapi.concurrency import run_in_threadpool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def verify_password(plain_password, hashed_password):
    return await run_in_threadpool(pwd_context.verify, plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return token

async def authenticate_user(db, email, password):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if await verify_password(password, user.hashed_password):
        return user
    return None

async def get_current_user(token:str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
    except JWTError:
        raise AuthenticationError("Invalid Token")
    if payload["sub"] is None:
        raise AuthenticationError("Invalid Token")
    user = await get_user_by_email(db, payload["sub"])
    if not user:
        raise AuthenticationError("User not found")
    return user