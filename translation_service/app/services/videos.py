import asyncio
import os
from datetime import datetime
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
import logging
from app.models.project import Project, ProjectStatus
from app.core.database import get_db
from app.services.translation import translate_video
from app.core.config import settings
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

async def process_video_translation(project_id: int, db: Session = Depends(get_db)):
    try:
        with db.begin():
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                logging.error(f"Project {project_id} not found")
                return
            project.status = ProjectStatus.processing
            project.progress = 10.0
        video_path = os.path.join(settings.UPLOAD_DIR, project.video_id)
        project_type = project.type
        result_path = translate_video(
            project_id=project_id,
            video_path=video_path,
            operation_type=project_type,
        )
        with db.begin():
            project.status = ProjectStatus.completed
            project.progress = 100.0
            project.completed_at = datetime.utcnow()
            project.download_token = str(uuid.uuid4())
            # Create translated file
            translated_path = os.path.join(settings.TRANSLATED_DIR, f"{project.id}_translated.{video_path.split('.')[-1]}")
            open(translated_path, "a").close()  # Placeholder, replace with actual translation output
    except Exception as e:
        logging.error(f"Error processing video translation for project {project_id}: {str(e)}")
        with db.begin():
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = ProjectStatus.failed
                project.progress = 0.0
        raise

def add_to_executor(project_id: int):
    future = executor.submit(asyncio.run, process_video_translation(project_id))
    if future.running():
        return {"status": "Task is being processed"}
    elif future._state == 'PENDING':
        return {"status": "Task is in the queue"}
    else:
        return {"status": "Task status unknown"}