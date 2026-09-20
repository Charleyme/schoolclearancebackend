from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ClearancePayment(Base):
    __tablename__ = "clearance_payments"

    id = Column(Integer, primary_key=True, index=True)

    clearance_record_id = Column(
        Integer,
        ForeignKey("clearance_records.id"),
        nullable=False
    )

    requirement_id = Column(
        Integer,
        ForeignKey("clearance_requirements.id"),
        nullable=False
    )

    amount = Column(
        Numeric(12, 2),
        nullable=False
    )

    receipt_file_name = Column(
        String(255),
        nullable=False
    )

    receipt_file_path = Column(
        String(500),
        nullable=False
    )

    payment_date = Column(
        DateTime,
        nullable=True
    )

    verification_status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    verification_remark = Column(
        String(500),
        nullable=True
    )

    verified_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    verified_at = Column(
        DateTime,
        nullable=True
    )
    
    created_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        nullable=False
    )
    clearance_record = relationship("ClearanceRecord", back_populates="payments")