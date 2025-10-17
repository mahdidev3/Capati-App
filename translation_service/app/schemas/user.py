from pydantic import BaseModel , Field , field_validator

from app.core.config import settings


class ProfileUpdate(BaseModel):
    firstName: str
    lastName: str

class PasswordChange(BaseModel):
    currentPassword: str
    newPassword: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long and contain at least one number"
    )

    @field_validator("newPassword")
    def validate_new_password(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v

class MobileChangeOtp(BaseModel):
    newMobile: str

    @field_validator("newMobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v

class MobileChangeVerify(BaseModel):
    newMobile: str
    otp: str
    otpId: str

    @field_validator("newMobile")
    def validate_mobile(cls, v):
        import re
        if not re.match(settings.MOBILE_PATTERN, v):
            raise ValueError("شماره موبایل نامعتبر است")
        return v

class AccountInfo(BaseModel):
    success: bool
    data: dict
