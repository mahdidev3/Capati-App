from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # nullable برای کاربرانی فقط با OTP
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
