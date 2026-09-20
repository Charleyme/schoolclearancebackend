
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User


from app.schemas.officer import ClearanceDecision
from app.schemas.document_verification import DocumentVerificationRequest
from app.schemas.payment_verification import PaymentVerificationRequest
from app.auth.dependencies import require_roles
from app.services.officerchecking import get_pending_clearances, approve_clearance, get_clearance_record, get_document_for_review, verify_document, verify_payment, get_officer_payments


router = APIRouter(
    prefix="/officer",
    tags=["Officer"]
)
@router.get("/pending")
def get_pending_student_clearances(db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return get_pending_clearances(db, current_user)
@router.put("/approve/{record_id}")
def approve_student_clearance(record_id: int, decision: ClearanceDecision, db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return approve_clearance(db, record_id, decision, current_user)
@router.get("/record/{record_id}")
def get_student_clearance_record(record_id: int,db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return get_clearance_record(db, record_id, current_user)
@router.get("documents/{document_id}")
def get_specific_document_for_review(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return get_document_for_review(document_id, db, current_user)

@router.patch("/documents/{document_id}/verify")
def verify_student_document(document_id: int, data: DocumentVerificationRequest,db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return verify_document(document_id, data, db, current_user)

@router.patch("/payments/{payment_id}/verify")
def verify_student_payment(payment_id: int, data: PaymentVerificationRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return verify_payment(payment_id, data, db, current_user)

@router.get("/payments")
def get_student_payments(db: Session = Depends(get_db), current_user: User = Depends(require_roles("officer", "admin"))):
    return get_officer_payments(db, current_user)