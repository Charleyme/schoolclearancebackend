
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User

from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.clearance import ClearanceResponse, ClearanceProgressResponse
from app.services.clearance import clearance_application, get_clearance_info, get_my_documents, get_clearance_record
from app.auth.dependencies import require_roles, get_current_user
from app.schemas.payment_summary import PaymentSummaryResponse
from app.services.payment_summary_service import get_school_fee_summary
from app.services.officerchecking import apply_again_for_clearance


router = APIRouter(
    tags=["Clearance"]
)
@router.post("/apply", response_model=ClearanceResponse, status_code=201)
def apply_for_clearance(db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return clearance_application(db, current_user)
@router.get("/clearance_info", response_model=ClearanceProgressResponse)
def clearance_info(db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return get_clearance_info(db, current_user)
@router.get("/record/{record_id}")
def get_record(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return get_clearance_record(db, record_id, current_user)

@router.get("/my_documents")
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return get_my_documents(db, current_user)

@router.get("/payment-summary/{clearance_record_id}", response_model=list[PaymentSummaryResponse])
def payment_summary(clearance_record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return get_school_fee_summary(db, current_user, clearance_record_id)

@router.post("/record/{record_id}/apply-again")
def apply_again(record_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return apply_again_for_clearance(db, record_id, current_user)