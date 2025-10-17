from pydantic import BaseModel, Field , field_validator
from typing import Optional

from app.core.config import settings


class MobileRequest(BaseModel):
    mobile: str

    @field_validator("mobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v

class OtpLoginRequest(BaseModel):
    mobile: str
    otp: str
    otpId: str

    @field_validator("mobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v

class PasswordLoginRequest(BaseModel):
    mobile: str
    password: str

    @field_validator("mobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v


class SignupCompleteRequest(BaseModel):
    mobile: str
    otp: str
    otpId: str
    password: str = Field(..., min_length=8, description="At least 8 chars, one number")

    @field_validator("password")
    def validate_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


    @field_validator("mobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"  # Fixed: token_type should be a string literal, not a type annotation

class UserResponse(BaseModel):
    id: int
    mobile: str

    class Config:
        from_attributes = True


    @field_validator("mobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v

class LoginResponse(BaseModel):
    success: bool
    message: str
    token: str
    user: UserResponse

class OtpResponse(BaseModel):
    success: bool
    message: str
    otpId: str