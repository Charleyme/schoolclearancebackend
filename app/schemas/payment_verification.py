from pydantic import BaseModel

class PaymentVerificationRequest(BaseModel):
    action: str
    remark: str | None = None