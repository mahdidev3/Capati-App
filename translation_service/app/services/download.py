import os
import json
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.core.config import settings
from app.core.security import create_access_token, verify_upload_token, verify_access_token
from app.services.error_handlers import app_error


def get_download_url_with_token(project_id: int):
    # Define file path for storing URLs
    url_dir = settings.URL_STORAGE_DIR  # Directory from settings
    try:
        os.makedirs(url_dir, exist_ok=True)  # Create directory if it doesn't exist
    except OSError as e:
        app_error(
            code="URL_STORAGE_DIR_CREATION_FAILED",
            message="Failed to create URL storage directory",
            details={"error": str(e)},
            status_code=500
        )

    url_file = os.path.join(url_dir, f"project_{project_id}_url.json")

    # Check for existing URL
    try:
        if os.path.exists(url_file):
            with open(url_file, 'r') as f:
                data = json.load(f)
                try:
                    stored_expires_at = datetime.fromisoformat(data['expires_at'])
                    # Check if URL is still valid
                    if stored_expires_at > datetime.utcnow():
                        return data['download_url'], stored_expires_at
                except (KeyError, ValueError) as e:
                    app_error(
                        code="INVALID_URL_FILE",
                        message="Invalid or corrupted URL file",
                        details={"error": str(e), "file": url_file},
                        status_code=500
                    )
    except json.JSONDecodeError as e:
        app_error(
            code="JSON_DECODE_ERROR",
            message="Failed to parse URL file",
            details={"error": str(e), "file": url_file},
            status_code=500
        )
    except OSError as e:
        app_error(
            code="URL_FILE_READ_ERROR",
            message="Failed to read URL file",
            details={"error": str(e), "file": url_file},
            status_code=500
        )

    # Generate new URL and token if none exists or expired
    expires_at = datetime.utcnow() + timedelta(minutes=settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES)
    download_token = create_access_token(
        data={"project_id": project_id, "type": "download"},
        expires_delta=timedelta(minutes=settings.DOWNLOAD_TOKEN_EXPIRE_MINUTES)
    )
    download_url = f"{settings.BASE_URL}/v1/translate/download/{project_id}/file?token={download_token}"

    # Save new URL to file
    try:
        with open(url_file, 'w') as f:
            json.dump({
                'download_url': download_url,
                'expires_at': expires_at.isoformat()
            }, f)
    except OSError as e:
        app_error(
            code="URL_FILE_WRITE_ERROR",
            message="Failed to write URL to file",
            details={"error": str(e), "file": url_file},
            status_code=500
        )

    return download_url, expires_at

def verify_download_token(token):
    payload = verify_access_token(token)
    if payload is None:
        return None, False
    return payload.get("project_id"), payload.get("type") == "download"