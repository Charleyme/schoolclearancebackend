from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class ClearanceDocument(Base):
    __tablename__ = "clearance_documents"

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

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    verification_status = Column(
        String(20),
        default="pending",
        nullable=False
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
    clearance_record = relationship('ClearanceRecord')
    requirement = relationship("ClearanceRequirement")