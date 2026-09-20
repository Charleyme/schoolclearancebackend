from sqlalchemy import Boolean, Column, DateTime, Integer, UniqueConstraint, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import  datetime, timezone
class OfficerAssignment(Base):
    __tablename__ = "officer_assignments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    clearance_unit_id = Column(Integer, ForeignKey("clearance_units.id"), nullable=False)
    school_id = Column(
        Integer,
        ForeignKey('schools.id'),
        nullable= True
    )
    user = relationship("User")
    clearance_unit = relationship("ClearanceUnit")
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "clearance_unit_id",
            name="unique_officer_assignment"
        ),
    )
    created_at = Column(
        DateTime, 
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
