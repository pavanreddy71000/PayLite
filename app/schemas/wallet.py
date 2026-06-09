from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal

class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    balance: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime

