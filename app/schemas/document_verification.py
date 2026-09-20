from pydantic import BaseModel

class DocumentVerificationRequest(BaseModel):
    action: str
    remark: str | None = None