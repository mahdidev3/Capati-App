import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from .sms import send_sms
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logger import logger
from app.models.user import User



def app_error(code: str, message: str, details: dict | None = None, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": code,
            "message": message,
            "details": details or {}
        }
    )

def format_error_response(code: str, message: str, details: dict | None = None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {}
            }
        }
    )

def log_success(path: str, message: str, details: dict | None = None):
    logger.info(f"Success: Path={path}, Message={message}, Details={details or {}}")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    details = {"field": errors[0].get("loc")[-1], "issue": errors[0].get("msg")} if errors else {}
    logger.error(f"Validation error: Path={request.url.path}, Details={details}")
    admin_message = f"خطای اعتبارسنجی در {request.url.path}: {details.get('issue', 'Unknown issue')}"
    send_sms(settings.ADMIN_PHONE, admin_message)
    return format_error_response(
        code="VALIDATION_ERROR",
        message="داده ورودی نامعتبر است",
        details=details,
        status_code=422
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "NOT_FOUND",
                "message": "The requested resource was not found on the server.",
                "details": str(exc.detail) if exc.detail else "Resource not found."
            }
        )

    details = {"path": request.url.path}
    logger.error(f"HTTP error: Code={exc.detail.get('code', 'UNKNOWN')}, Message={exc.detail.get('message', str(exc))}, Details={exc.detail.get('details' , {})} , Path={request.url.path}")
    admin_message = f"خطای HTTP در {request.url.path}: {exc.detail.get('message', str(exc))}"

    if(not send_sms(settings.ADMIN_PHONE, admin_message)):
        logger.warning("admin sms id off")

    if exc.detail.get("code") in [
        "INVALID_PROJECT_TYPE", "INSUFFICIENT_BALANCE", "PROJECT_NOT_FOUND",
        "PROJECT_NOT_COMPLETED","INVALID_AMOUNT", "INVALID_PAYMENT", "PAYMENT_ALREADY_PROCESSED"
    ]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.user.id).first() if hasattr(request, "user") else None
            if user and user.mobile:
                send_sms(user.mobile, f"خطا در {request.url.path}: {exc.detail.get('message', str(exc))}")
        finally:
            db.close()

    return format_error_response(
        code=exc.detail.get("code", "HTTP_ERROR"),
        message=exc.detail.get("message", str(exc)),
        details=details,
        status_code=exc.status_code
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    error_details = {
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }
    if hasattr(exc, 'statement') and exc.statement:
        error_details["statement"] = exc.statement
    if hasattr(exc, 'params') and exc.params:
        error_details["params"] = exc.params
    error_details["traceback"] = traceback.format_exc()
    logger.error(f"Database error: Type={exc.__class__.__name__}, Message={str(exc)}, Path={request.url.path}")
    admin_message = f"خطای پایگاه داده در {request.url.path}: {str(exc)}"
    send_sms(settings.ADMIN_PHONE, admin_message)
    return format_error_response(
        code="DATABASE_ERROR",
        message="عملیات پایگاه داده با خطا مواجه شد",
        details=error_details,
        status_code=500
    )

async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: Message={str(exc)}, Path={request.url.path}")
    admin_message = f"خطای غیرمنتظره در {request.url.path}: {str(exc)}"
    send_sms(settings.ADMIN_PHONE, admin_message)
    return format_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="خطای غیرمنتظره رخ داد",
        details={"error": str(exc)},
        status_code=500
    )
