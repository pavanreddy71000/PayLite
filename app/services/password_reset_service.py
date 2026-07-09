from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.exceptions import InvalidResetTokenError
from app.services.user_service import get_user_by_email, pwd_context
from datetime import datetime, timedelta
import secrets

def request_password_reset(db, email):
    user = get_user_by_email(db, email)
    if not user:
        return None
    reset_token = PasswordResetToken(
        token = secrets.token_urlsafe(),
        user_id = user.id,
        expires_at = datetime.utcnow() + timedelta(minutes=30)
    )
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    return reset_token

def confirm_password_reset(db, token, new_password):
    reset_token = db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    if not reset_token:
        raise InvalidResetTokenError("Reset token not found")
    if reset_token.used:
        raise InvalidResetTokenError("Reset token is already used")
    if reset_token.expires_at < datetime.utcnow():
        raise InvalidResetTokenError("Reset token is expired")
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.hashed_password = pwd_context.hash(new_password)
    reset_token.used = True
    db.commit()
    return True