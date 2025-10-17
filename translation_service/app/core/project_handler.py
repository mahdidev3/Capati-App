# app/core/project_handler.py
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.project import Project as DBProject, ProjectStatus
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


def create_project(
        db: Session,
        name: str,
        project_type: str,
        user_id: int,
        video_id: Optional[str] = None,
        status: ProjectStatus = ProjectStatus.awaiting_upload
) -> DBProject:
    """
    Create a new project in the database.

    Args:
        db: The database session
        name: The name of the project
        project_type: The type of the project
        user_id: The ID of the user who owns the project
        video_id: The ID of the video (optional)
        status: The initial status of the project

    Returns:
        The created project
    """
    project = DBProject(
        name=name,
        type=project_type,
        user_id=user_id,
        video_id=video_id,
        status=status
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_project_by_id(db: Session, project_id: int, user_id: Optional[int] = None) -> Optional[DBProject]:
    """
    Get a project by its ID.

    Args:
        db: The database session
        project_id: The ID of the project
        user_id: The ID of the user (optional, for authorization)

    Returns:
        The project if found, None otherwise
    """
    query = db.query(DBProject).filter(DBProject.id == project_id)
    if user_id is not None:
        query = query.filter(DBProject.user_id == user_id)
    return query.first()


def update_project_status(
        db: Session,
        project_id: int,
        status: ProjectStatus,
        progress: Optional[int] = None,
        video_id: Optional[str] = None
) -> Optional[DBProject]:
    """
    Update the status of a project.

    Args:
        db: The database session
        project_id: The ID of the project
        status: The new status
        progress: The new progress (optional)
        video_id: The new video ID (optional)

    Returns:
        The updated project if found, None otherwise
    """
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if not project:
        return None

    project.status = status
    if progress is not None:
        project.progress = progress
    if video_id is not None:
        project.video_id = video_id

    if status == ProjectStatus.completed:
        project.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)
    return project


def get_user_projects(db: Session, user_id: int, status: Optional[ProjectStatus] = None) -> List[DBProject]:
    """
    Get all projects for a user.

    Args:
        db: The database session
        user_id: The ID of the user
        status: Filter by status (optional)

    Returns:
        List of projects
    """
    query = db.query(DBProject).filter(DBProject.user_id == user_id)
    if status is not None:
        query = query.filter(DBProject.status == status)
    return query.all()


def simulate_progress(db: Session, project_id: int) -> Optional[DBProject]:
    """
    Simulate progress for a project (for testing purposes).

    Args:
        db: The database session
        project_id: The ID of the project

    Returns:
        The updated project if found, None otherwise
    """
    project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if not project or project.status != ProjectStatus.processing:
        return None

    progress = min(100, (project.progress or 0) + 10)
    project.progress = progress

    if progress >= 100:
        project.status = ProjectStatus.completed
        project.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(project)
    return project