from app.db.base import Base
from sqlalchemy import ForeignKey, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from decimal import Decimal
from typing import Optional

class Transfer(Base):
    __tablename__ = "transfers"
    __table_args__ = (
        CheckConstraint("amount > 0", name="positive_amount"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_wallet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wallets.id"))
    receiver_wallet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("wallets.id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2))
    created_at : Mapped[datetime] = mapped_column(server_default=func.now())
    sender_wallet: Mapped[Optional["Wallet"]] = relationship("Wallet", foreign_keys=[sender_wallet_id])
    receiver_wallet: Mapped[Optional["Wallet"]] = relationship("Wallet", foreign_keys=[receiver_wallet_id])
