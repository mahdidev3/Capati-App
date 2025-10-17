# app/core/file_handler.py
import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile
import aiofiles
import logging

logger = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
TRANSLATED_DIR = "translations"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TRANSLATED_DIR, exist_ok=True)


async def save_upload_file(upload_file: UploadFile, destination: str) -> Tuple[bool, str]:
    """
    Save an uploaded file to the specified destination.

    Args:
        upload_file: The UploadFile object from FastAPI
        destination: The path where the file should be saved

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        async with aiofiles.open(destination, 'wb') as f:
            while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
                await f.write(chunk)
        return True, "File saved successfully"
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return False, f"Error saving file: {str(e)}"


def generate_file_path(project_id: int, upload_id: str, extension: str, directory: str = UPLOAD_DIR) -> str:
    """
    Generate a unique file path for a project upload.

    Args:
        project_id: The ID of the project
        upload_id: The unique upload ID
        extension: The file extension
        directory: The directory to save the file in

    Returns:
        The generated file path
    """
    filename = f"{project_id}_{upload_id}.{extension}"
    return os.path.join(directory, filename)


def create_placeholder_file(project_id: int) -> str:
    """
    Create a placeholder file for a translated video.

    Args:
        project_id: The ID of the project

    Returns:
        The path to the created file
    """
    file_path = os.path.join(TRANSLATED_DIR, f"{project_id}_translated.mp4")
    open(file_path, "a").close()
    return file_path


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: The path to the file

    Returns:
        True if the file exists, False otherwise
    """
    return os.path.exists(file_path)


def get_file_size(file_path: str) -> Optional[int]:
    """
    Get the size of a file in bytes.

    Args:
        file_path: The path to the file

    Returns:
        The file size in bytes, or None if the file doesn't exist
    """
    if not file_exists(file_path):
        return None
    return os.path.getsize(file_path)