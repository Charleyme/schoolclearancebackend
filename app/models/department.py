from sqlalchemy import Boolean, Column, DateTime, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import  datetime, timezone
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique= True, nullable=False)
    code = Column(String(20), unique= True, nullable= False)
    school_id = Column(
        Integer,
        ForeignKey('schools.id'),
        nullable= True
    )
    school = relationship('School')
    created_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
