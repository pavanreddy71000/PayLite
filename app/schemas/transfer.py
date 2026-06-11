from pydantic import BaseModel, Field, ConfigDict, model_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, Literal

class TransferCreate(BaseModel):
    receiver_wallet_id: int
    amount: Decimal = Field(gt=0)

class DepositCreate(BaseModel):
    amount: Decimal = Field(gt=0)

class WithdrawCreate(BaseModel):
    amount: Decimal = Field(gt=0)

class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sender_wallet_id: Optional[int]
    receiver_wallet_id: Optional[int]
    amount: Decimal
    created_at: datetime

class TransferHistoryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    type: Optional[Literal["deposit", "withdrawal", "transfer"]] = None
    min_amount: Optional[Decimal] = Field(default=None, gt=0)
    max_amount: Optional[Decimal] = Field(default=None, gt=0)
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    sort: Optional[str] = Field(default="-created_at")

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.min_amount is not None and self.max_amount is not None:
            if self.min_amount > self.max_amount:
                raise ValueError("min_amount must be less than or equal to max_amount")
        if self.from_date is not None and self.to_date is not None:
            if self.from_date > self.to_date:
                raise ValueError("from_date must be less than or equal to to_date")
        return self

class PaginatedTransferResponse(BaseModel):
    items: list[TransferResponse]
    total: int
    page: int
    size: int
    pages: int