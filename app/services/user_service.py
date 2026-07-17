from app.models.user import User
from passlib.context import CryptContext
from app.models.wallet import Wallet
from app.exceptions import DuplicateEmailError, UserNotFoundError
from sqlalchemy import select
from fastapi.concurrency import run_in_threadpool

pwd_context = CryptContext(schemes=["bcrypt"])

async def create_user(db, user_in):
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise DuplicateEmailError()
    hashed = await run_in_threadpool(pwd_context.hash, user_in.password)
    user = User(
        email=user_in.email.lower(),
        hashed_password=hashed,
        full_name=user_in.full_name
    )
    db.add(user)
    await db.flush()
    wallet = Wallet(
        user_id=user.id,
    )
    db.add(wallet)
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_id(db, user_id):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundError()
    return user

async def get_user_by_email(db, email):
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    return user

async def update_user(db, user_id, user_in):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UserNotFoundError()
    update_data = user_in.model_dump(exclude_unset=True)
    if "email" in update_data:
        update_data["email"] = update_data["email"].lower()
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user