from sqlalchemy import Boolean, Column, DateTime, Integer, String, DateTime
from app.database import Base
from datetime import  datetime, timezone
class ClearanceUnit(Base):
    __tablename__ = "clearance_units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique= True, nullable=False)
    code = Column(String(30), unique= True, nullable= False)
    is_active = Column(Boolean, default=True, nullable=False)
   
    created_at = Column(
        DateTime, 
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
