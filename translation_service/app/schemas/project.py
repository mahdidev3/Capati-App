# app/schemas/project.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.project import ProjectType, ProjectStatus


class ProjectBase(BaseModel):
    name: str
    type: ProjectType
    status: ProjectStatus
    created_at: datetime
    price : float
    progress: Optional[float] = None
    completed_at: Optional[datetime] = None
    class Config:
        use_enum_values = True


class Project(ProjectBase):
    id: int

    class Config:
        from_attributes = True


class DashboardData(BaseModel):
    success: bool
    data: dict


class VideoUploadResponse(BaseModel):
    success: bool
    message: str
    videoId: str
    originalName: str
    size: int
    duration: int  # شبیه‌سازی شده


class TranslationOptionsResponse(BaseModel):
    success: bool
    data: dict


class StartTranslationRequest(BaseModel):
    videoSize: int  # bytes - required now
    projectType: str
    useWalletBalance: bool = True


class StartTranslationResponse(BaseModel):
    success: bool
    message: str
    projectId: int
    estimatedTime: str
    uploadToken: str
    uploadUrl: str
    logsUrl: str
    price: float
    chunkSize: int


class TranslationStatusResponse(BaseModel):
    success: bool
    data: dict


class DownloadUrlResponse(BaseModel):
    success: bool
    data: dict
