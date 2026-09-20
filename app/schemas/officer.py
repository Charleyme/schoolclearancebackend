from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ClearanceDecision(BaseModel):
    status: str
    amount_owed: Optional[Decimal]= None
    remark: Optional[str] = None