from sqlalchemy import Boolean, Column, DateTime, Integer, String, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

from datetime import  datetime, timezone
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey('users.id'),
        unique=True,
        nullable = False
    )
    matric_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    full_name = Column(String(150), nullable=False)
   
    department_id = Column(
        Integer, 
        ForeignKey('departments.id'),
        nullable = False
    )
    level = Column(String(20), nullable=False)
    graduation_session = Column(String(20), nullable=False)
    user= relationship("User")
    department = relationship("Department")
    created_at = Column(
        DateTime, 
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
