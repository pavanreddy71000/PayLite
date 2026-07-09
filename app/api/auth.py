from fastapi import Depends, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import authenticate_user, create_access_token
from app.services.password_reset_service import request_password_reset, confirm_password_reset
from app.schemas.password_reset import ForgotPasswordRequest, ResetPasswordRequest
from app.db.session import get_db
from app.exceptions import AuthenticationError

router = APIRouter(prefix="/auth")

@router.post("/token", status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(user_in: ForgotPasswordRequest, db: Session = Depends(get_db)):
    result = request_password_reset(db, user_in.email)
    if result:
        return {"message": "Reset link sent", "token": result.token}
    else:
        return {"message": "Reset link sent"}

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(user_in: ResetPasswordRequest, db: Session = Depends(get_db)):
    confirm_password_reset(db, user_in.token, user_in.new_password)
    return {"message": "Password reset successful"}