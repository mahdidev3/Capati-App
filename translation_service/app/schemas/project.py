# app/schemas/project.py
import re

from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

from app.models.project import ProjectType, ProjectStatus


class ProjectBase(BaseModel):
    project_id : int
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

class TranslationPricesRequest(BaseModel):
    duration: float
    resolution: str

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, value: str) -> str:
        # Regular expression for resolution format: {width}x{height}
        pattern = r"^\d+x\d+$"
        if not re.match(pattern, value):
            raise ValueError("Resolution must be in the format 'WIDTHxHEIGHT' (e.g., '1920x1080')")

        # Split the resolution into width and height
        width, height = map(int, value.split("x"))

        # Ensure width and height are positive
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")

        return value

class TranslationPricesResponse(BaseModel):
    success: bool
    data: dict

class StartTranslationRequest(BaseModel):
    duration: int
    resolution: str
    projectType: str
    videoSize : int
    useWalletBalance: bool = True

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, value: str) -> str:
        # Regular expression for resolution format: {width}x{height}
        pattern = r"^\d+x\d+$"
        if not re.match(pattern, value):
            raise ValueError("Resolution must be in the format 'WIDTHxHEIGHT' (e.g., '1920x1080')")

        # Split the resolution into width and height
        width, height = map(int, value.split("x"))
        # Ensure width and height are positive
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")

        return value


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
