from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User
from app.models.payment import Payment, PaymentStatus
from app.schemas.user import AccountInfo
from app.api.deps import get_current_user
from app.services.pricing import PRICING
from app.services.error_handlers import app_error
from app.core.config import settings
from app.core.security import create_access_token, verify_upload_token

router = APIRouter()

class PaymentRequest(BaseModel):
    amount: int

class PaymentVerifyRequest(BaseModel):
    paymentId: str
    authority: str

@router.get("/wallet", response_model=AccountInfo)
def get_wallet(current_user: User = Depends(get_current_user)):
    try:
        return {
            "success": True,
            "data": {
                "balance": current_user.balance,
                "pricing": PRICING
            }
        }
    except HTTPException as http:
        raise http
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/wallet/payment")
def initiate_payment(
    request: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        with db.begin():
            if request.amount < settings.MINIMUM_PAYMENT_AMOUNT:
                app_error(
                    code="INVALID_AMOUNT",
                    message="مبلغ نامعتبر است",
                    status_code=400
                )
            payment_id = str(uuid.uuid4())
            authority = str(uuid.uuid4())  # Simulated authority
            payment = Payment(
                user_id=current_user.id,
                amount=request.amount,
                payment_id=payment_id,
                authority=authority,
                status=PaymentStatus.pending,
                created_at=datetime.utcnow()
            )
            db.add(payment)
            redirect_url = f"https://shaparak.ir/payment/{payment_id}?authority={authority}"
            return {
                "success": True,
                "message": "پرداخت با موفقیت آغاز شد",
                "paymentId": payment_id,
                "redirectUrl": redirect_url
            }
    except HTTPException as http:
        raise http
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/wallet/payment/verify")
def verify_payment(
    request: PaymentVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        with db.begin():
            payment = db.query(Payment).filter(
                Payment.payment_id == request.paymentId,
                Payment.authority == request.authority,
                Payment.user_id == current_user.id
            ).first()
            if not payment:
                app_error(
                    code="INVALID_PAYMENT",
                    message="پرداخت نامعتبر است",
                    status_code=400
                )
            if payment.status != PaymentStatus.pending:
                app_error(
                    code="PAYMENT_ALREADY_PROCESSED",
                    message="پرداخت قبلاً پردازش شده است",
                    status_code=400
                )
            # Simulate payment gateway verification
            payment.status = PaymentStatus.completed
            payment.completed_at = datetime.utcnow()
            current_user.balance += payment.amount
            return {
                "success": True,
                "message": "پرداخت با موفقیت تایید شد",
                "newBalance": current_user.balance
            }
    except HTTPException as http:
        raise http
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )