
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User

from app.schemas.student import StudentCreate, StudentResponse
from app.services.student import create_student_profile, get_student_profile
from app.auth.dependencies import require_roles, get_current_user


router = APIRouter(
    tags=["Students"]
)
@router.post("/studentprofile", response_model=StudentResponse)
def createprofile(student_data: StudentCreate,db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return create_student_profile(student_data, db, current_user)


@router.get("/studentsprofile", response_model=StudentResponse)
def getprofile(db: Session = Depends(get_db), current_user: User = Depends(require_roles("student"))):
    return get_student_profile(db, current_user)