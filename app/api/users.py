from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app.services.user_service import create_user, get_user_by_id, get_user_by_email, update_user
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.db.session import get_db

router = APIRouter(prefix="/users")

@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, user_in)
    return user

@router.get("/{user_id}", response_model=UserRead)
def read_user_by_id_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserRead)
def update_user_endpoint(user_id: int, user_in: UserUpdate,db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user = update_user(db, user_id, user_in)
    return user

