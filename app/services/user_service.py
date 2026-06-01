from app.models.user import User
from passlib.context import CryptContext
from app.models.wallet import Wallet

pwd_context = CryptContext(schemes=["bcrypt"])

def create_user(db, user_in):
    user = User(
        email=user_in.email.lower(),
        hashed_password=pwd_context.hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(user)
    db.flush()
    wallet = Wallet(
        user_id=user.id,
    )
    db.add(wallet)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(db, user_id):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db, email):
    return db.query(User).filter(User.email == email.lower()).first()

def update_user(db, user_id, user_in):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    update_data = user_in.model_dump(exclude_unset=True)
    if "email" in update_data:
        update_data["email"] = update_data["email"].lower()
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user