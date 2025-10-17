from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, generate_otp, verify_otp
from app.models.user import User
from app.models.otp import Otp
from app.schemas.user import ProfileUpdate, PasswordChange, AccountInfo, MobileChangeOtp, MobileChangeVerify
from app.api.deps import get_current_user
from app.schemas.auth import OtpResponse
from app.services.sms import send_change_mobile_otp_sms
from app.services.error_handlers import app_error
from pydantic import BaseModel, Field

router = APIRouter()

@router.get("/account", response_model=AccountInfo)
def get_account(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": {
            "statistics": {
                "currentBalance": current_user.balance,
                "joinDate": current_user.created_at
            },
            "profile": {
                "firstName": current_user.first_name,
                "lastName": current_user.last_name,
                "username": current_user.mobile,
                "credits": current_user.balance,
                "phone_number": current_user.mobile,
                "phone_verified": current_user.phone_verified,
                "is_admin": False,
                "created_at": current_user.created_at
            },
            "advancedSettings": {
                "mobile": current_user.mobile,
                "verified": current_user.phone_verified
            }
        }
    }

@router.put("/account/profile")
def update_profile(
    profile: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        current_user.first_name = profile.firstName
        current_user.last_name = profile.lastName
        return {"success": True, "message": "پروفایل با موفقیت به‌روزرسانی شد"}
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.put("/account/password")
def change_password(
    passwords: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.hashed_password or not verify_password(passwords.currentPassword,
                                                                   current_user.hashed_password):
            app_error(
                code="INVALID_PASSWORD",
                message="رمز عبور فعلی اشتباه است",
                status_code=400
            )
        current_user.hashed_password = get_password_hash(passwords.newPassword)
        return {"success": True, "message": "رمز عبور با موفقیت تغییر کرد"}
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/account/mobile-change-otp", response_model=OtpResponse)
def mobile_change_otp(
    request: MobileChangeOtp,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        with db.begin():
            existing_user = db.query(User).filter(User.mobile == request.newMobile).first()
            if existing_user:
                app_error(
                    code="MOBILE_ALREADY_REGISTERED",
                    message="شماره موبایل جدید قبلا ثبت شده است",
                    status_code=400
                )
            # Check for existing OTP to prevent race conditions
            existing_otp = db.execute(
                select(Otp).filter_by(mobile=request.newMobile).with_for_update()
            ).scalar_one_or_none()
            if existing_otp and existing_otp.expires_at > datetime.utcnow():
                app_error(
                    code="OTP_ALREADY_SENT",
                    message="کد تایید قبلا ارسال شده و هنوز معتبر است",
                    status_code=429
                )
            db.execute(delete(Otp).filter_by(mobile=request.newMobile))
            otp_code, hashed_otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=settings.CHANGE_MOBILE_OPT_TIME)
            db_otp = Otp(mobile=request.newMobile, hashed_otp=hashed_otp, expires_at=expires_at)
            db.add(db_otp)
            db.refresh(db_otp)
            if not send_change_mobile_otp_sms(request.newMobile, otp_code):
                app_error(
                    code="SMS_SEND_FAILED",
                    message="ارسال پیامک با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.",
                    status_code=502
                )
            return OtpResponse(
                success=True,
                message="کد تایید با موفقیت ارسال شد",
                otpId=db_otp.otp_id
            )
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.put("/account/mobile", response_model=dict)
def mobile_change_verify(
    request: MobileChangeVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        with db.begin():
            db_otp = db.query(Otp).filter(Otp.otp_id == request.otpId, Otp.mobile == request.newMobile).first()
            if not db_otp:
                app_error(
                    code="INVALID_OTP_ID",
                    message="شناسه کد تایید نامعتبر است",
                    status_code=400
                )
            if not verify_otp(request.otp, db_otp.hashed_otp) or db_otp.expires_at < datetime.utcnow():
                app_error(
                    code="INVALID_OTP",
                    message="کد تایید نامعتبر یا منقضی شده است",
                    status_code=400
                )
            existing_user = db.query(User).filter(User.mobile == request.newMobile).first()
            if existing_user and existing_user.id != current_user.id:
                app_error(
                    code="MOBILE_ALREADY_REGISTERED",
                    message="شماره موبایل جدید قبلا ثبت شده است",
                    status_code=400
                )
            current_user.mobile = request.newMobile
            db.delete(db_otp)
            return {
                "success": True,
                "message": "شماره موبایل با موفقیت تغییر کرد"
            }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )
