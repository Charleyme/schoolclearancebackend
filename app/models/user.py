from sqlalchemy import Boolean, Column, DateTime, Integer, String, DateTime
from app.database import Base
from datetime import  datetime, timezone
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique= True, nullable=False, index=True)
    email = Column(String(100), unique= True, nullable= False, index=True)
    password_hash= Column(String(256), nullable= False)
    role = Column(String(20), nullable=False, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, 
        default= lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        onupdate= lambda: datetime.now(timezone.utc)
    )
