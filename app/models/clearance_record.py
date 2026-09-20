from sqlalchemy import Boolean, Column,Numeric, Text, DateTime, Integer, String, DateTime, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import  datetime, timezone
class ClearanceRecord(Base):
    __tablename__ = "clearance_records"
    id = Column(Integer, primary_key=True, index=True)
    clearance_request_id = Column(Integer, ForeignKey("clearance_requests.id"), nullable=False)
    clearance_unit_id= Column(Integer, ForeignKey("clearance_units.id"), nullable=False)
    status= Column(
        String(20),
        nullable=False,
        default="pending"
    )
    student_response = Column(
        String(255),
        nullable=True
    )
    amount_owed = Column(
        Numeric(12, 2),
        nullable= True
    )
    reason = Column(
        Text,
        nullable= True
    )
    remark = Column(
        Text, 
        nullable= True
    )
    approved_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )
    approved_at = Column(
        DateTime, 
        nullable= True
    )
    created_at = Column(
            DateTime, 
            default= lambda: datetime.now(timezone.utc),
            nullable= False
    )
    clearance_request = relationship("ClearanceRequest", back_populates="records")
    clearance_unit= relationship("ClearanceUnit")
    officer = relationship('User')
    payments = relationship('ClearancePayment', back_populates="clearance_record", cascade="all, delete-orphan")