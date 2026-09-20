
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.user import User

from app.schemas.user import UserResponse, UserRegister, UserLogin
from app.services.user import register, login_user
from app.auth.dependencies import require_roles, get_current_user


router = APIRouter(
    tags=["User"]
)
@router.post("/register", response_model= UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    return register(db, user_data)

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user_data)

@router.get("/students")
def student_area(current_user: User = Depends(require_roles("student"))):
    return {
        "message": "Welocme to the student area",
       
    }
@router.get("/admin")
def admin_area(current_user: User = Depends(require_roles("admin"))):
    return {
        "message": "Welocme to the admin area",
        
    }
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "message": "you are authentciatred",
        
    }