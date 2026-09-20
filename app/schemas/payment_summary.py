from decimal import Decimal
from pydantic import BaseModel


class PaymentSummaryResponse(BaseModel):
    requirement_id: int
    requirement_name: str
    expected_amount: Decimal | None
    approved_amount: Decimal 
    pending_amount: Decimal
    rejected_amount: Decimal
    balance: Decimal | None
    receipt_count: int
    status: str