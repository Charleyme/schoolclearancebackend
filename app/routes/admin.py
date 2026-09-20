from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User

from app.auth.dependencies import require_roles, get_current_user
from app.schemas.payment_summary import PaymentSummaryResponse
from app.schemas.officer_assigment import OfficerAssignmentResponse, OfficerAssignmentCreate
from app.services.adminoperation import assign_officer

router = APIRouter(
    prefix="/admin",
    tags=['Admin']
)


@router.post('/officer-assignments', response_model=OfficerAssignmentResponse)
def assign_officer_unit(data:OfficerAssignmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin"))):
    return assign_officer(data, db, current_user)