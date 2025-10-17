# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from .config import settings
import hashlib
import secrets
import uuid


def generate_otp(length: int = settings.OTP_LENGTH):
    """
    Generate a 6-digit numeric OTP and return its hash (SHA3-512).
    """
    otp = str(secrets.randbelow(10 ** length)).zfill(length)  # 6-digit random OTP
    hashed = hashlib.sha3_512(otp.encode()).hexdigest()
    return otp, hashed


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    """
    Verify if the provided OTP matches the stored hash.
    """
    return hashlib.sha3_512(plain_otp.encode()).hexdigest() == hashed_otp


def get_password_hash(password: str) -> str:
    """
    Hash the given password using SHA3-512.
    """
    # Encode the password to bytes and compute the SHA3-512 hash
    return hashlib.sha3_512(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verify if the provided plain password matches the stored SHA3-512 hash.
    """
    # Hash the plain password and compare with the stored hash
    return get_password_hash(plain_password) == stored_hash


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(seconds=31536000)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        mobile: str = payload.get("sub")
        if mobile is None:
            return None
        return mobile
    except JWTError:
        return None


def generate_upload_token(user_id: int, project_id: int, expires_delta: Optional[timedelta] = None):
    """
    Generate a token for upload session that includes user_id, project_id, and expiration.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)  # Default 1 hour

    upload_id = str(uuid.uuid4())

    to_encode = {
        "upload_id": upload_id,
        "user_id": user_id,
        "project_id": project_id,
        "exp": expire,
        "type": "upload"
    }

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return upload_id, encoded_jwt


def verify_upload_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify the upload token and return the payload if valid.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        upload_id = payload.get("upload_id")
        user_id = payload.get("user_id")
        project_id = payload.get("project_id")
        token_type = payload.get("type")

        if upload_id is None or user_id is None or project_id is None or token_type != "upload":
            return None

        return {
            "upload_id": upload_id,
            "user_id": user_id,
            "project_id": project_id
        }
    except JWTError:
        return None