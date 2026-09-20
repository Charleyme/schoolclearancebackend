from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

class ClearanceRecordUpdate(BaseModel):
    student_response: Optional[str] = None
    amount_owed: Optional[Decimal] = None
    reason: Optional[str] = None

class ClearanceRecordResponse(BaseModel):
    id: int
    clearance_unit_id: int
    status: str
    student_response: Optional[str] = None
    amount_owed: Optional[Decimal] = None
    reason:Optional[str]= None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ClearanceResponse(BaseModel):
    id: int
    student_id: int
    status: str
    submitted_at: Optional[datetime] = None
    records: list[ClearanceRecordResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ClearanceUnitStatus(BaseModel):
    record_id: int
    unit_id: int
    unit_name: str
    unit_code: str
    status: str
    student_response: Optional[str] = None
    amount_owed: Optional[Decimal] = None
    reason: Optional[str] = None
    remark: Optional[str] = None
    approved_at: Optional[datetime] = None


class ClearanceProgressResponse(BaseModel):
    clearance_id: int
    overall_status: str

    student_name: str
    matric_number: str

    total_units: int
    approved: int
    pending: int
    rejected: int

    units: list[ClearanceUnitStatus]
    model_config = ConfigDict(from_attributes=True)


class ClearanceDocumentResponse(BaseModel):
    id: int
    requirement_id: int
    requirement_name: str
    file_name: str
    verification_status: str
    verification_remark: Optional[str] = None
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)