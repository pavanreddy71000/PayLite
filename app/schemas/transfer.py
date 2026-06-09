from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional

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
