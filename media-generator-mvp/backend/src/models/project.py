from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProjectStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationMode(str, Enum):
    TOOL = "tool"
    VEO = "veo"

class Project(BaseModel):
    id: str
    user_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: ProjectStatus
    mode: GenerationMode
    input_text: str
    input_source: str  # "file", "book", "custom"
    
    # Generation results
    sequences: List[Dict[str, Any]] = []
    image_paths: List[str] = []
    audio_paths: List[str] = []
    video_path: Optional[str] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    
    # Validation
    validation_result: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    
    class Config:
        use_enum_values = True

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    mode: GenerationMode
    input_text: str
    input_source: str

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: ProjectStatus
    mode: GenerationMode
    input_source: str
    video_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    processing_time: Optional[float]
    quality_score: Optional[float]
    sequence_count: int = 0

class ProjectDetail(ProjectResponse):
    sequences: List[Dict[str, Any]]
    image_paths: List[str]
    audio_paths: List[str]
    validation_result: Optional[Dict[str, Any]]

class BookCatalogItem(BaseModel):
    id: str
    title: str
    author: str
    description: str
    language: str
    word_count: int
    file_path: str
    cover_image: Optional[str] = None
    
class GenerationRequest(BaseModel):
    text: Optional[str] = None
    book_id: Optional[str] = None
    mode: GenerationMode
    custom_text: Optional[str] = None
    
class GenerationStatus(BaseModel):
    project_id: str
    status: str
    progress: float  # 0-100
    current_step: str
    estimated_time_remaining: Optional[float] = None
    error_message: Optional[str] = None
