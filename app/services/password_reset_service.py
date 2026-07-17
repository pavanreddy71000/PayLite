from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.exceptions import InvalidResetTokenError
from app.services.user_service import get_user_by_email, pwd_context
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from fastapi.concurrency import run_in_threadpool
import secrets

async def request_password_reset(db, email):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    reset_token = PasswordResetToken(
        token = secrets.token_urlsafe(),
        user_id = user.id,
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    )
    db.add(reset_token)
    await db.commit()
    await db.refresh(reset_token)
    return reset_token

async def confirm_password_reset(db, token, new_password):
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
    reset_token = result.scalar_one_or_none()
    if not reset_token:
        raise InvalidResetTokenError("Reset token not found")
    if reset_token.used:
        raise InvalidResetTokenError("Reset token is already used")
    expires_at = reset_token.expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise InvalidResetTokenError("Reset token is expired")
    result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = result.scalar_one_or_none()
    user.hashed_password = await run_in_threadpool(pwd_context.hash, new_password)
    reset_token.used = True
    await db.commit()
    return True