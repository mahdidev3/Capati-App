from fastapi import Depends, Cookie, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_mobile_token
from app.models.user import User
from app.services.error_handlers import app_error

async def get_current_user(
    db: Session = Depends(get_db),
    auth_token: str = Cookie(None),
    authorization: str = Header(None)
):
    token = auth_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[len("Bearer "):]
    if not token:
        app_error(
            code="UNAUTHORIZED",
            message="Could not validate credentials.",
            details={"error": "No token provided"},
            status_code=401
        )
    mobile = verify_mobile_token(token)
    if mobile is None:
        app_error(
            code="UNAUTHORIZED",
            message="Could not validate credentials.",
            details={"error": "Invalid token"},
            status_code=401
        )
    user = db.query(User).filter(User.mobile == mobile).first()
    if user is None:
        app_error(
            code="UNAUTHORIZED",
            message="Could not validate credentials.",
            details={"error": "User not found"},
            status_code=401
        )
    return user
