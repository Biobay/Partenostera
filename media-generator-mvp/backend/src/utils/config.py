"""
Configuration management for the media generator application
"""

import os
from typing import Optional
from pydantic import BaseModel


class AppConfig(BaseModel):
    """Application configuration"""
    # API Keys
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    ai_horde_api_key: Optional[str] = None
    replicate_api_token: Optional[str] = None
    
    # Processing settings
    max_concurrent_requests: int = 3
    chunk_size: int = 4000
    overlap_size: int = 200
    
    # Directories
    upload_dir: str = "data/uploads"
    output_dir: str = "data/outputs"
    
    # API settings
    use_openrouter: bool = False
    default_model: str = "gpt-4"
    
    # Image generation
    default_image_style: str = "cinematic"
    default_image_quality: str = "high"
    
    # Video generation  
    default_video_duration: int = 5
    default_video_quality: str = "high"


def get_config() -> AppConfig:
    """
    Get application configuration from environment variables
    
    Returns:
        AppConfig instance with loaded configuration
    """
    return AppConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        ai_horde_api_key=os.getenv("AI_HORDE_API_KEY"),
        replicate_api_token=os.getenv("REPLICATE_API_TOKEN"),
        max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "3")),
        chunk_size=int(os.getenv("CHUNK_SIZE", "4000")),
        overlap_size=int(os.getenv("OVERLAP_SIZE", "200")),
        upload_dir=os.getenv("UPLOAD_DIR", "data/uploads"),
        output_dir=os.getenv("OUTPUT_DIR", "data/outputs"),
        use_openrouter=os.getenv("USE_OPENROUTER", "false").lower() == "true",
        default_model=os.getenv("DEFAULT_MODEL", "gpt-4"),
        default_image_style=os.getenv("DEFAULT_IMAGE_STYLE", "cinematic"),
        default_image_quality=os.getenv("DEFAULT_IMAGE_QUALITY", "high"),
        default_video_duration=int(os.getenv("DEFAULT_VIDEO_DURATION", "5")),
        default_video_quality=os.getenv("DEFAULT_VIDEO_QUALITY", "high")
    )