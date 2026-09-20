from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.student import StudentResponse, StudentCreate
from app.models.user import User
from app.models.student import Student
from app.auth.security import hash_password, verify_password, create_access_token


def create_student_profile(student_data: StudentCreate, db: Session, current_user: User):
    existing_profile = db.query(Student).filter(Student.user_id  == current_user.id).first()
    if existing_profile:
        raise HTTPException(
            status_code= 400,
            detail="Student profile already exists"
        )
    existing_matric= db.query(Student).filter(Student.matric_number == student_data.matric_number).first()
    if existing_matric:
        raise HTTPException(
            status_code=400,
            detail="Matric number already exists"
        )
    student = Student(
        user_id = current_user.id,
        matric_number= student_data.matric_number,
        full_name = student_data.full_name,
        department_id = student_data.department_id,
        level = student_data.level,
        graduation_session = student_data.graduation_session
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
def get_student_profile(db:Session, current_user: User):
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found"
        )
    return student