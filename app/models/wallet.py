from app.db.base import Base
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

class Wallet(Base):
    __tablename__ = "wallets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    balance: Mapped[float] = mapped_column(Numeric(precision=12, scale=2), default=0.00)
    currency: Mapped[str] = mapped_column(default="USD")
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())