from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Otp(Base):
    __tablename__ = "otps"

    otp_id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    mobile = Column(String, nullable=False, index=True)
    hashed_otp = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
