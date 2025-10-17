from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from sqlalchemy.orm import relationship

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    payment_id = Column(String, unique=True, index=True, nullable=False)
    authority = Column(String, index=True, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")