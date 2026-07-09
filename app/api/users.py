from fastapi import Depends, status, APIRouter
from sqlalchemy.orm import Session
from app.services.user_service import create_user, get_user_by_id, get_user_by_email, update_user
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.db.session import get_db
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/users")

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_in)
    return user

@router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = get_user_by_id(db, user_id)
    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    user = update_user(db, user_id, user_in)
    return user