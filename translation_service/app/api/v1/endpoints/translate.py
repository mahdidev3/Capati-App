import os
import uuid
import math
import asyncio
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, UploadFile, File, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import FileResponse
from requests import session
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.database import get_db, SessionLocal
from app.models.user import User
from app.models.project import Project as DBProject, ProjectStatus, get_project_type
from app.schemas.project import (
    VideoUploadResponse, TranslationPricesResponse,
    StartTranslationRequest, StartTranslationResponse,
    TranslationStatusResponse, DownloadUrlResponse, TranslationPricesRequest
)
from app.api.deps import get_current_user
from app.services.download import verify_download_token, get_download_url_with_token
from app.services.pricing import PRICING, calculate_price, calculate_prices
from app.core.security import generate_upload_token, verify_upload_token, create_access_token
from app.core.websocket_manager import manager
from app.services.videos import add_to_executor
from app.services.error_handlers import app_error

router = APIRouter()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TRANSLATED_DIR, exist_ok=True)


@router.post("/translate/prices", response_model=TranslationPricesResponse)
def get_translation_options(request: TranslationPricesRequest, current_user: User = Depends(get_current_user)):
    try:
        duration = request.duration  # مدت زمان ویدیو (به ثانیه)

        width, height = map(int, request.resolution .split("x"))

        prices = calculate_prices(width , height , duration)

        return {
            "success": True,
            "data": {
                "options": prices
            }
        }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.post("/translate/start", response_model=StartTranslationResponse)
def start_translation(
    request: StartTranslationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        option_price_per_mb = PRICING.get(request.projectType)
        if option_price_per_mb is None:
            app_error(
                code="INVALID_PROJECT_TYPE",
                message="گزینه ترجمه یافت نشد",
                status_code=404
            )

        width, height = map(int, request.resolution.split("x"))

        total_price, multiplier, video_type = calculate_price(request.projectType,width , height , request.duration)
        if request.useWalletBalance and current_user.balance < total_price:
            app_error(
                code="INSUFFICIENT_BALANCE",
                message="موجودی کافی نیست",
                status_code=400
            )
        project_type = get_project_type(request.projectType)
        new_project = DBProject(
            name=f"ترجمه ویدیو (pending upload) {str(uuid.uuid4())[:8]}",
            type=project_type,
            user_id=current_user.id,
            video_id=None,
            status=ProjectStatus.awaiting_upload,
            price=total_price,
        )
        db.add(new_project)
        db.flush()
        db.refresh(new_project)
        upload_id, upload_token = generate_upload_token(
            user_id=current_user.id,
            project_id=new_project.id,
            expires_delta=timedelta(hours=settings.UPLOAD_TOKEN_EXPIRE_HOURS)
        )
        manager.create_upload_session(
            upload_id=upload_id,
            project_id=new_project.id,
            user_id=current_user.id,
            file_size=request.videoSize
        )
        websocket_url = f"{settings.BASE_URL}/v1/translate/ws/upload/{upload_id}?token={upload_token}"
        logs_url = f"{settings.BASE_URL}/v1/translate/ws/logs/{upload_id}?token={upload_token}"
        return {
            "success": True,
            "message": "ترجمه ثبت شد. اکنون می‌توانید فایل را آپلود کنید",
            "projectId": new_project.id,
            "estimatedTime": settings.ESTIMATED_TRANSLATION_TIME,
            "uploadToken": upload_token,
            "uploadUrl": websocket_url,
            "logsUrl": logs_url,
            "chunkSize": settings.CHUNK_SIZE,
            "price": total_price,
        }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.websocket("/translate/ws/upload/{upload_id}")
async def websocket_upload(websocket: WebSocket, upload_id: str, token: str = Query(...)):
    token_data = verify_upload_token(token)
    if not token_data or token_data["upload_id"] != upload_id:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    session = manager.get_upload_session(upload_id)
    if not session:
        await websocket.close(code=4002, reason="Upload session not found")
        return
    if session["status"] == "completed":
        await websocket.close(code=4003, reason="Upload session already completed")
        return
    if not manager.is_logs_socket_connected(upload_id):
        await websocket.close(code=4003, reason="Logs socket not connected. Please connect to logs socket first.")
        return
    await manager.connect(websocket, upload_id, "upload")
    db = SessionLocal()
    try:
        data = await websocket.receive_text()
        try:
            metadata = json.loads(data)
            file_extension = metadata.get("file_extension", "mp4")
        except json.JSONDecodeError:
            await manager.send_json_to_type(
                {"type": "error", "message": "Invalid metadata format"},
                upload_id,
                "logs"
            )
            raise ValueError("Invalid metadata format")
        session["file_extension"] = file_extension
        file_path = os.path.join(settings.UPLOAD_DIR, f"{session['project_id']}_{upload_id}.{file_extension}")
        session["file_path"] = file_path
        await manager.send_json_to_type(
            {"status": "ready", "message": "Ready to receive file"},
            upload_id,
            "logs"
        )
        bytes_received = 0
        with open(file_path, "wb") as f:
            while bytes_received < session["file_size"]:
                try:
                    chunk = await websocket.receive_bytes()
                    f.write(chunk)
                    bytes_received += len(chunk)
                    updated_session = manager.update_upload_progress(upload_id, bytes_received)
                    if updated_session:
                        await manager.send_json_to_type(
                            {
                                "type": "progress",
                                "progress": updated_session["progress"],
                                "bytes_received": bytes_received
                            },
                            upload_id,
                            "logs"
                        )
                except WebSocketDisconnect:
                    await manager.send_json_to_type(
                        {"type": "error", "message": "Upload disconnected unexpectedly"},
                        upload_id,
                        "logs"
                    )
                    raise
        with db.begin():
            project = db.query(DBProject).filter(DBProject.id == session["project_id"]).first()
            if not project:
                app_error(
                    code="PROJECT_NOT_FOUND",
                    message="پروژه یافت نشد",
                    status_code=404
                )
            if project.owner.balance < project.price:
                app_error(
                    code="INSUFFICIENT_BALANCE",
                    message="موجودی کافی نیست",
                    status_code=400
                )
            project.video_id = f"{session['project_id']}_{upload_id}.{file_extension}"
            project.status = ProjectStatus.awaiting_queue
            project.progress = 0
            project.owner.balance -= project.price
            result = add_to_executor(project.id)
            await manager.send_json_to_type(
                {
                    "type": "complete",
                    "message": f"File upload completed successfully, {result.get('status', 'Task status unknown')}",
                    "project_id": project.id
                },
                upload_id,
                "logs"
            )
        manager.complete_upload_session(upload_id, file_path)
    except Exception as e:
        await manager.send_json_to_type(
            {"type": "error", "message": f"Error during upload: {str(e)}"},
            upload_id,
            "logs"
        )
        raise
    finally:
        manager.disconnect(websocket, upload_id, "upload")
        db.close()

@router.websocket("/translate/ws/logs/{upload_id}")
async def websocket_logs(websocket: WebSocket, upload_id: str, token: str = Query(...)):
    token_data = verify_upload_token(token)
    if not token_data or token_data["upload_id"] != upload_id:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    session = manager.get_upload_session(upload_id)
    if not session:
        await websocket.close(code=4002, reason="Upload session not found")
        return
    await manager.connect(websocket, upload_id, "logs")
    try:
        await manager.send_personal_message(
            json.dumps({
                "type": "status",
                "status": session["status"],
                "progress": session["progress"],
                "bytes_received": session["bytes_received"]
            }),
            websocket
        )
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, upload_id, "logs")

@router.get("/translate/status/{project_id}", response_model=TranslationStatusResponse)
def get_translation_status(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(DBProject).filter(DBProject.id == project_id, DBProject.user_id == current_user.id).first()
        if not project:
            app_error(
                code="PROJECT_NOT_FOUND",
                message="پروژه یافت نشد",
                status_code=404
            )
        if project.status == ProjectStatus.processing:
            progress = min(100, (project.progress or 0) + 10)
            project.progress = progress
            if progress >= 100:
                project.status = ProjectStatus.completed
                project.completed_at = datetime.utcnow()
        return {
            "success": True,
            "data": {
                "projectId": project.id,
                "status": project.status.value,
                "progress": project.progress,
                "estimatedTimeRemaining": settings.ESTIMATED_TIME_REMAINING if project.status == ProjectStatus.processing else None
            }
        }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.get("/translate/download/{project_id}", response_model=DownloadUrlResponse)
def get_download_url(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(DBProject).filter(DBProject.id == project_id, DBProject.user_id == current_user.id).first()
        if not project or project.status != ProjectStatus.completed:
            app_error(
                code="PROJECT_NOT_COMPLETED",
                message="پروژه تکمیل شده یافت نشد",
                status_code=404
            )

        download_url,expires_at  = get_download_url_with_token(project_id)

        return {
            "success": True,
            "data": {
                "downloadUrl": download_url,
                "expiresAt": expires_at.isoformat()
            }
        }
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )

@router.get("/translate/download/{project_id}/file")
def download_file(
    project_id: int,
    token: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        token_project_id, is_download = verify_download_token(token)  # Reusing verify_upload_token for simplicity
        if token_project_id != project_id or not is_download:
            app_error(
                code="INVALID_TOKEN",
                message="لینک دانلود نامعتبر یا منقضی شده است",
                status_code=401
            )
        project = db.query(DBProject).filter(DBProject.id == project_id, DBProject.user_id == current_user.id).first()
        if not project or project.status != ProjectStatus.completed:
            app_error(
                code="PROJECT_NOT_COMPLETED",
                message="فایل برای دانلود یافت نشد",
                status_code=404
            )
        file_path = os.path.join(settings.TRANSLATED_DIR,
                                 f"{project.id}_translated.{project.video_id.split('.')[-1]}")
        if not os.path.exists(file_path):
            app_error(
                code="FILE_NOT_FOUND",
                message="فایل ترجمه شده هنوز آماده نشده است",
                status_code=404
            )
        return FileResponse(path=file_path, filename=f"translated_{project.video_id}")
    except HTTPException as http:
        raise http
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )