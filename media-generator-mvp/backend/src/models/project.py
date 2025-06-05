"""
Project models for the media generator application
Includes complete workflow support: text → scenes → images → videos
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class ProjectStatus(str, Enum):
    """Project processing status"""
    CREATED = "created"
    TEXT_ANALYZING = "text_analyzing"
    TEXT_ANALYZED = "text_analyzed"
    IMAGES_GENERATING = "images_generating"
    IMAGES_GENERATED = "images_generated"
    VIDEOS_GENERATING = "videos_generating"
    VIDEOS_GENERATED = "videos_generated"
    COMPLETED = "completed"
    FAILED = "failed"

class ProcessingStep(str, Enum):
    """Individual processing step status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Scene(BaseModel):
    """Scene model with complete processing pipeline support"""
    id: str = Field(..., description="Unique scene identifier")
    title: str = Field(..., description="Scene title")
    content: str = Field(..., description="Scene text content")
    summary: str = Field(..., description="Scene summary")
    
    # Context and metadata
    chapter_number: Optional[int] = Field(default=None, description="Chapter number")
    scene_number: Optional[int] = Field(default=None, description="Scene number within chapter")
    characters: List[str] = Field(default_factory=list, description="Characters in this scene")
    setting: Optional[str] = Field(default=None, description="Scene setting/location")
    mood: Optional[str] = Field(default=None, description="Scene mood/atmosphere")
    themes: List[str] = Field(default_factory=list, description="Scene themes")
    
    # Image generation
    image_prompt: Optional[str] = Field(default=None, description="Generated image prompt")
    image_generation_status: ProcessingStep = Field(default=ProcessingStep.PENDING)
    image_url: Optional[str] = Field(default=None, description="Generated image URL")
    image_path: Optional[str] = Field(default=None, description="Local image path")
    image_error: Optional[str] = Field(default=None, description="Image generation error")
    
    # Video generation
    video_prompt: Optional[str] = Field(default=None, description="Video generation prompt")
    video_generation_status: ProcessingStep = Field(default=ProcessingStep.PENDING)
    video_url: Optional[str] = Field(default=None, description="Generated video URL")
    video_path: Optional[str] = Field(default=None, description="Local video path")
    video_error: Optional[str] = Field(default=None, description="Video generation error")
    
    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = Field(default=None, description="Total processing time in seconds")

class TextChunk(BaseModel):
    """Text chunk model for analyzing large texts"""
    id: str = Field(..., description="Unique chunk identifier")
    content: str = Field(..., description="Chunk text content")
    start_position: int = Field(..., description="Starting position in original text")
    end_position: int = Field(..., description="Ending position in original text")
    word_count: int = Field(..., description="Number of words in chunk")
    
    # Analysis results
    scenes: List[Scene] = Field(default_factory=list, description="Scenes extracted from this chunk")
    processing_status: ProcessingStep = Field(default=ProcessingStep.PENDING)
    processing_error: Optional[str] = Field(default=None, description="Processing error message")
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ProjectSettings(BaseModel):
    """Project settings and configuration"""
    # Text analysis settings
    chunk_size: int = Field(default=4000, description="Text chunk size for processing")
    overlap_size: int = Field(default=200, description="Overlap between chunks")
    
    # Image generation settings
    image_style: str = Field(default="cinematic", description="Image generation style")
    image_quality: str = Field(default="high", description="Image quality setting")
    image_aspect_ratio: str = Field(default="16:9", description="Image aspect ratio")
    
    # Video generation settings
    video_duration: int = Field(default=5, description="Video duration in seconds")
    video_quality: str = Field(default="high", description="Video quality setting")
    video_fps: int = Field(default=24, description="Video frames per second")
    
    # Processing settings
    max_concurrent_requests: int = Field(default=3, description="Max concurrent API requests")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed requests")
    
    # API settings
    openai_model: str = Field(default="gpt-4", description="OpenAI model for text analysis")
    use_openrouter: bool = Field(default=False, description="Use OpenRouter instead of OpenAI")

class ProcessingStats(BaseModel):
    """Processing statistics and metrics"""
    total_scenes: int = Field(default=0, description="Total number of scenes")
    scenes_completed: int = Field(default=0, description="Number of completed scenes")
    images_generated: int = Field(default=0, description="Number of images generated")
    videos_generated: int = Field(default=0, description="Number of videos generated")
    
    total_processing_time: float = Field(default=0.0, description="Total processing time in seconds")
    estimated_remaining_time: Optional[float] = Field(default=None, description="Estimated remaining time")
    
    # Error tracking
    failed_scenes: int = Field(default=0, description="Number of failed scenes")
    failed_images: int = Field(default=0, description="Number of failed image generations")
    failed_videos: int = Field(default=0, description="Number of failed video generations")
    
    last_updated: datetime = Field(default_factory=datetime.now)

class Project(BaseModel):
    """Complete project model with full workflow support"""
    id: str = Field(..., description="Unique project identifier")
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(default=None, description="Project description")
    
    # Source text
    original_text: Optional[str] = Field(default=None, description="Original text content")
    text_file_path: Optional[str] = Field(default=None, description="Path to uploaded text file")
    word_count: Optional[int] = Field(default=None, description="Total word count")
    
    # Processing pipeline
    status: ProjectStatus = Field(default=ProjectStatus.CREATED, description="Overall project status")
    text_chunks: List[TextChunk] = Field(default_factory=list, description="Text chunks for processing")
    scenes: List[Scene] = Field(default_factory=list, description="All extracted scenes")
    
    # Configuration
    settings: ProjectSettings = Field(default_factory=ProjectSettings, description="Project settings")
    
    # Statistics and monitoring
    stats: ProcessingStats = Field(default_factory=ProcessingStats, description="Processing statistics")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(default=None, description="User who created the project")
    
    # Output paths
    output_directory: Optional[str] = Field(default=None, description="Directory for generated files")
    images_directory: Optional[str] = Field(default=None, description="Directory for generated images")
    videos_directory: Optional[str] = Field(default=None, description="Directory for generated videos")

class ProjectCreate(BaseModel):
    """Model for creating a new project"""
    title: str = Field(..., description="Project title")
    description: Optional[str] = Field(default=None, description="Project description")
    text_content: Optional[str] = Field(default=None, description="Text content to process")
    settings: Optional[ProjectSettings] = Field(default=None, description="Project settings")

class ProjectUpdate(BaseModel):
    """Model for updating a project"""
    title: Optional[str] = Field(default=None, description="Updated project title")
    description: Optional[str] = Field(default=None, description="Updated project description")
    status: Optional[ProjectStatus] = Field(default=None, description="Updated project status")
    settings: Optional[ProjectSettings] = Field(default=None, description="Updated project settings")

class ProjectResponse(BaseModel):
    """Response model for project operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    project: Optional[Project] = Field(default=None, description="Project data")
    message: Optional[str] = Field(default=None, description="Response message")
    error: Optional[str] = Field(default=None, description="Error message if failed")

class ProcessingProgress(BaseModel):
    """Real-time processing progress information"""
    project_id: str = Field(..., description="Project identifier")
    current_step: str = Field(..., description="Current processing step")
    progress_percentage: float = Field(..., description="Progress percentage (0-100)")
    
    # Step-specific progress
    scenes_analyzed: int = Field(default=0, description="Number of scenes analyzed")
    images_generated: int = Field(default=0, description="Number of images generated")
    videos_generated: int = Field(default=0, description="Number of videos generated")
    
    # Current operation
    current_scene_id: Optional[str] = Field(default=None, description="Currently processing scene ID")
    current_operation: Optional[str] = Field(default=None, description="Current operation description")
    
    # Time estimates
    elapsed_time: float = Field(default=0.0, description="Elapsed processing time in seconds")
    estimated_remaining: Optional[float] = Field(default=None, description="Estimated remaining time")
    
    # Status
    is_complete: bool = Field(default=False, description="Whether processing is complete")
    has_errors: bool = Field(default=False, description="Whether there are any errors")
    error_count: int = Field(default=0, description="Number of errors encountered")
    
    last_updated: datetime = Field(default_factory=datetime.now)

class BatchProcessingRequest(BaseModel):
    """Request for batch processing of multiple projects"""
    project_ids: List[str] = Field(..., description="List of project IDs to process")
    processing_order: Optional[List[str]] = Field(default=None, description="Custom processing order")
    max_concurrent: int = Field(default=1, description="Maximum concurrent processing")
    skip_errors: bool = Field(default=True, description="Skip failed projects and continue")

class BatchProcessingResponse(BaseModel):
    """Response for batch processing operations"""
    success: bool = Field(..., description="Whether batch processing started successfully")
    batch_id: str = Field(..., description="Unique batch processing identifier")
    projects_count: int = Field(..., description="Number of projects in batch")
    estimated_total_time: Optional[float] = Field(default=None, description="Estimated total processing time")
    message: Optional[str] = Field(default=None, description="Response message")
    error: Optional[str] = Field(default=None, description="Error message if failed")