from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_password_hash, create_access_token, verify_password, generate_otp, verify_otp
from app.models.user import User
from app.models.otp import Otp
from app.services.sms import send_login_otp_sms, send_signup_otp_sms
from app.schemas.auth import (
    MobileRequest, OtpLoginRequest, PasswordLoginRequest,
    SignupCompleteRequest, OtpResponse, LoginResponse
)
from app.core.config import settings
from app.api.deps import get_current_user
from app.services.error_handlers import app_error

router = APIRouter()

@router.post("/auth/login-otp", response_model=OtpResponse)
def login_otp(request: MobileRequest, db: Session = Depends(get_db)):
    try:
        with db.begin():
            # Check for existing OTP to prevent race conditions
            existing_otp = db.execute(
                select(Otp).filter_by(mobile=request.mobile).with_for_update()
            ).scalar_one_or_none()
            if existing_otp and existing_otp.expires_at > datetime.utcnow():
                app_error(
                    code="OTP_ALREADY_SENT",
                    message="کد تایید قبلا ارسال شده و هنوز معتبر است",
                    status_code=429
                )
            db.execute(delete(Otp).filter_by(mobile=request.mobile))
            otp_code, hashed_otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=settings.LOGIN_OPT_TIME)
            db_otp = Otp(mobile=request.mobile, hashed_otp=hashed_otp, expires_at=expires_at)
            db.add(db_otp)
            db.flush()
            if not send_login_otp_sms(request.mobile, otp_code):
                app_error(
                    code="SMS_SEND_FAILED",
                    message="ارسال پیامک با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.",
                    status_code=502
                )
            return {
                "success": True,
                "message": "کد تایید با موفقیت ارسال شد",
                "otpId": db_otp.otp_id
            }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/auth/login-otp-verify", response_model=LoginResponse)
def login_otp_verify(
    request: OtpLoginRequest,
    db: Session = Depends(get_db),
    response: Response = None
):
    try:
        with db.begin():
            db_otp = db.query(Otp).filter(Otp.otp_id == request.otpId, Otp.mobile == request.mobile).first()
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
            user = db.query(User).filter(User.mobile == request.mobile).first()
            if not user:
                user = User(mobile=request.mobile)
                db.add(user)
            db.delete(db_otp)
            access_token = create_access_token(data={"sub": user.mobile})
            db.flush()
            response.set_cookie(
                key="auth_token",
                value=access_token,
                max_age=31536000,
                httponly=True,
                secure=settings.ENVIRONMENT == "production" if hasattr(settings, "ENVIRONMENT") else False,
                samesite="strict"
            )
            return LoginResponse(
                success=True,
                message="ورود با موفقیت انجام شد",
                token=access_token,
                user={"id": user.id, "mobile": user.mobile}
            )
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/auth/login-password", response_model=LoginResponse)
def login_password(
    request: PasswordLoginRequest,
    db: Session = Depends(get_db),
    response: Response = None
):
    try:
        user = db.query(User).filter(User.mobile == request.mobile).first()
        if not user:
            app_error(
                code="USER_NOT_FOUND",
                message="کاربر یافت نشد",
                status_code=400
            )
        if not verify_password(request.password, user.hashed_password):
            app_error(
                code="INVALID_PASSWORD",
                message="رمز عبور اشتباه است",
                status_code=400
            )
        access_token = create_access_token(data={"sub": user.mobile})
        response.set_cookie(
            key="auth_token",
            value=access_token,
            max_age=31536000,
            httponly=True,
            secure=settings.ENVIRONMENT == "production" if hasattr(settings, "ENVIRONMENT") else False,
            samesite="strict"
        )
        return LoginResponse(
            success=True,
            message="ورود با موفقیت انجام شد",
            token=access_token,
            user={"id": user.id, "mobile": user.mobile}
        )
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/auth/signup-otp", response_model=OtpResponse)
def signup_otp(request: MobileRequest, db: Session = Depends(get_db)):
    try:
        with db.begin():
            user = db.query(User).filter(User.mobile == request.mobile).first()
            if user:
                app_error(
                    code="MOBILE_ALREADY_REGISTERED",
                    message="شماره موبایل قبلا ثبت شده است",
                    status_code=400
                )
            existing_otp = db.execute(
                select(Otp).filter_by(mobile=request.mobile).with_for_update()
            ).scalar_one_or_none()
            if existing_otp and existing_otp.expires_at > datetime.utcnow():
                app_error(
                    code="OTP_ALREADY_SENT",
                    message="کد تایید قبلا ارسال شده و هنوز معتبر است",
                    status_code=429
                )
            db.execute(delete(Otp).filter_by(mobile=request.mobile))
            otp_code, hashed_otp = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=settings.SIGNUP_OPT_TIME)
            db_otp = Otp(mobile=request.mobile, hashed_otp=hashed_otp, expires_at=expires_at)
            db.add(db_otp)
            db.flush()
            if not send_signup_otp_sms(request.mobile, otp_code):
                app_error(
                    code="SMS_SEND_FAILED",
                    message="ارسال پیامک با خطا مواجه شد. لطفاً بعداً دوباره تلاش کنید.",
                    status_code=502
                )
            return {
                "success": True,
                "message": "کد تایید با موفقیت ارسال شد",
                "otpId": db_otp.otp_id
            }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/auth/signup-complete", response_model=LoginResponse)
def signup_complete(
    request: SignupCompleteRequest,
    db: Session = Depends(get_db),
    response: Response = None
):
    try:
        with db.begin():
            db_otp = db.query(Otp).filter(Otp.otp_id == request.otpId, Otp.mobile == request.mobile).first()
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
            user = db.query(User).filter(User.mobile == request.mobile).first()
            if user:
                app_error(
                    code="MOBILE_ALREADY_REGISTERED",
                    message="شماره موبایل قبلا ثبت شده است",
                    status_code=400
                )
            hashed_password = get_password_hash(request.password)
            new_user = User(mobile=request.mobile, hashed_password=hashed_password)
            db.add(new_user)
            db.delete(db_otp)
            db.flush()
            access_token = create_access_token(data={"sub": new_user.mobile})
            response.set_cookie(
                key="auth_token",
                value=access_token,
                max_age=31536000,
                httponly=True,
                secure=settings.ENVIRONMENT == "production" if hasattr(settings, "ENVIRONMENT") else False,
                samesite="strict"
            )
            return LoginResponse(
                success=True,
                message="حساب با موفقیت ایجاد شد",
                token=access_token,
                user={"id": new_user.id, "mobile": new_user.mobile}
            )
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/auth/logout")
def logout(response: Response = None):
    response.delete_cookie("auth_token")
    return {"success": True, "message": "با موفقیت خارج شدید"}
