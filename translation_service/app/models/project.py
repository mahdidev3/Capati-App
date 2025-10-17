from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base
import enum

class ProjectStatus(str, enum.Enum):
    awaiting_upload = "awaiting upload"
    awaiting_queue = "awaiting queue"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class ProjectType(str, enum.Enum):
    english_subtitle = "english_subtitle"
    persian_subtitle = "persian_subtitle"
    persian_dubbing = "persian_dubbing"
    persian_dubbing_english_subtitle = "persian_dubbing_english_subtitle"
    persian_dubbing_persian_subtitle = "persian_dubbing_persian_subtitle"

def get_project_type(project_type : str):
    # Convert the string from request to ProjectType enum
    project_type_str = project_type  # e.g., "video_translation"
    try:
        project_type = ProjectType(project_type_str)
    except ValueError:
        raise ValueError(f"Invalid project type: {project_type_str}")
    return project_type

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.processing)
    progress = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    video_id = Column(String, nullable=True) # Reference to video file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    price = Column(Float)
    owner = relationship("User", back_populates="projects")

# Add relationship to User model
from .user import User
User.projects = relationship("Project", back_populates="owner")
