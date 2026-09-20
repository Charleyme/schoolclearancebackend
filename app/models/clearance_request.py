from sqlalchemy import Boolean, Column, DateTime, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import  datetime, timezone
class ClearanceRequest(Base):
    __tablename__ = "clearance_requests"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(String(20), nullable=False,default="pending")
    submitted_at = Column(
        DateTime, 
        nullable=True
    )
    student = relationship("Student")
    records = relationship("ClearanceRecord", back_populates="clearance_request", cascade="all, delete-orphan")
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
