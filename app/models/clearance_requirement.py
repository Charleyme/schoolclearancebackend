from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String

from app.database import Base


class ClearanceRequirement(Base):
    __tablename__ = "clearance_requirements"

    id = Column(Integer, primary_key=True, index=True)

    clearance_unit_id = Column(
        Integer,
        ForeignKey("clearance_units.id"),
        nullable=False
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        String(500),
        nullable=True
    )
    requirement_type = Column(
        String(20),
        nullable= False,
        default="document"
    )
    expected_amount= Column(
        Numeric(12, 2),
        nullable= True
    )
    is_required = Column(
        Boolean,
        default=True,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )