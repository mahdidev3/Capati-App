import asyncio
import os
from datetime import datetime
import uuid
from fastapi import Depends
from sqlalchemy.orm import Session
import logging
from app.models.project import Project, ProjectStatus
from app.core.database import get_db, SessionLocal
from app.services.translation import translate_video
from app.core.config import settings
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)


def process_video_translation(project_id: int):
    db = SessionLocal()
    try:
        with db.begin():
            print(f"Starting video translation process for project_id: {project_id}")
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                logging.error(f"Project {project_id} not found")
                print(f"Error: Project {project_id} not found in database")
                return
            print(f"Found project: ID={project.id}, Type={project.type}, Video_ID={project.video_id}")

            project.status = ProjectStatus.processing
            project.progress = 10.0
            print(f"Updated project status to {project.status}, progress to {project.progress}%")

            print("Committed initial project status to database")

            video_path = os.path.join(settings.UPLOAD_DIR, project.video_id)
            print(f"Constructed video path: {video_path}")
            project_type = project.type
            print(f"Project type: {project_type}")

            result_path = translate_video(
                project=project,
                video_path=video_path,
                operation_type=project_type,
            )
            print(f"Video translation completed, result path: {result_path}")

            project.status = ProjectStatus.completed
            project.progress = 100.0
            project.completed_at = datetime.utcnow()
            project.download_token = str(uuid.uuid4())
            print(f"Updated project: status={project.status}, progress={project.progress}%, "
                  f"completed_at={project.completed_at}, download_token={project.download_token}")

            translated_path = os.path.join(settings.TRANSLATED_DIR, f"{project.id}_translated.{video_path.split('.')[-1]}")
            print(f"Creating translated file at: {translated_path}")
            open(translated_path, "a").close()  # Placeholder, replace with actual translation output
            print(f"Created placeholder file at: {translated_path}")

            print("Committed final project status to database")

    except Exception as e:
        print(f"Error occurred during video translation: {str(e)}")
        logging.error(f"Error in process_video_translation for project {project_id}: {str(e)}")
        raise

def add_to_executor(project_id: int):
    future = executor.submit(process_video_translation , project_id)
    if future.running():
        return {"status": "Task is being processed"}
    elif future._state == 'PENDING':
        return {"status": "Task is in the queue"}
    else:
        return {"status": "Task status unknown"}