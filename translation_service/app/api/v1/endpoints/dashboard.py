from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.translate import get_download_url
from app.core.database import get_db
from app.models.user import User
from typing import Dict
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectBase, DashboardData
from app.api.deps import get_current_user
from app.services.download import get_download_url_with_token
from app.services.error_handlers import app_error
from app.core.config import settings

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Fetch recent projects (same logic as original /dashboard)
        times_ago = datetime.utcnow() - timedelta(hours=settings.RECENT_PROJECTS_HOURS)
        recent_projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            (Project.status != ProjectStatus.completed) | (
                (Project.status == ProjectStatus.completed) & (Project.completed_at >= times_ago)
            )
        ).all()
        in_progress_projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.status == ProjectStatus.processing
        ).all()
        completed_projects = db.query(Project).filter(
            Project.user_id == current_user.id,
            Project.status == ProjectStatus.completed
        ).all()
        def project_to_dict(project: Project) -> Dict:
            (download_url , expire_at) = get_download_url_with_token(project.id) if project.status == ProjectStatus.completed else (None , datetime.utcnow())
            return {
                "name": project.name,
                "type": project.type,
                "status": project.status,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "progress": project.progress,
                "completed_at": project.completed_at.isoformat() if project.completed_at else None,
                "price" : project.price,
                "project_id" : project.id
            }

        recent_projects = [project_to_dict(p) for p in recent_projects]
        in_progress_projects = [project_to_dict(p) for p in in_progress_projects]
        completed_projects = [project_to_dict(p) for p in completed_projects]

        # Combine dashboard and account data
        return {
            "success": True,
            "data": {
                # Original dashboard data
                "balance": current_user.balance,
                "recentProjects": [ProjectBase.model_validate(p) for p in recent_projects],
                "inProgressProjects": [ProjectBase.model_validate(p) for p in in_progress_projects],
                "completedProjects": [ProjectBase.model_validate(p) for p in completed_projects],
                # Account data (from /account endpoint)
                "statistics": {
                    "currentBalance": current_user.balance,
                    "joinDate": current_user.created_at
                },
                "profile": {
                    "firstName": current_user.first_name,
                    "lastName": current_user.last_name,
                    "username": current_user.mobile,
                    "credits": current_user.balance,
                    "phone_number": current_user.mobile,
                    "phone_verified": True,
                    "is_admin": False,
                    "created_at": current_user.created_at
                },
                "advancedSettings": {
                    "mobile": current_user.mobile,
                    "verified": True
                }
            }
        }
    except HTTPException as http:
        raise http
    except Exception as e:
        app_error(
            code="INTERNAL_SERVER_ERROR",
            message="خطای غیرمنتظره رخ داد",
            details={"error": str(e)},
            status_code=500
        )
