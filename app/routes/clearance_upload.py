
from fastapi import APIRouter, Depends, File, UploadFile, Form
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User

from app.auth.dependencies import require_roles
from app.services.clearance_upload import upload_document
from app.services.clearance_payment import upload_school_fee_payment


router = APIRouter(
    tags=["Clearance Uploads"]
)
@router.post("/upload-document")
def upload_document_route(clearance_record_id: int, requirement_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return upload_document(db, current_user, clearance_record_id, requirement_id, file)
@router.post("/upload-payment")
def upload_payment(amount: float = Form(...), clearance_record_id: int = Form(...), requirement_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return upload_school_fee_payment(db, current_user, clearance_record_id, requirement_id, amount, file)