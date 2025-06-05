"""
File handling utilities for the media generator application
"""

import os
import shutil
import uuid
from typing import Optional, List, BinaryIO
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file operations for the media generator"""
    
    def __init__(self, base_dir: str = "data"):
        """
        Initialize file handler
        
        Args:
            base_dir: Base directory for all file operations
        """
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.outputs_dir = self.base_dir / "outputs"
        
        # Create directories if they don't exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str, project_id: str) -> str:
        """
        Save uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            project_id: Project ID for organization
            
        Returns:
            Path to saved file
        """
        # Create project upload directory
        project_upload_dir = self.uploads_dir / project_id
        project_upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = project_upload_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Saved uploaded file: {file_path}")
        return str(file_path)
    
    def create_project_directories(self, project_id: str) -> dict:
        """
        Create directory structure for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with directory paths
        """
        project_dir = self.outputs_dir / project_id
        images_dir = project_dir / "images"
        videos_dir = project_dir / "videos"
        
        # Create directories
        project_dir.mkdir(exist_ok=True)
        images_dir.mkdir(exist_ok=True)
        videos_dir.mkdir(exist_ok=True)
        
        return {
            'project_dir': str(project_dir),
            'images_dir': str(images_dir),
            'videos_dir': str(videos_dir)
        }
    
    def save_generated_image(self, image_data: bytes, project_id: str, scene_id: str) -> str:
        """
        Save generated image
        
        Args:
            image_data: Image data as bytes
            project_id: Project ID
            scene_id: Scene ID
            
        Returns:
            Path to saved image
        """
        images_dir = self.outputs_dir / project_id / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = images_dir / f"{scene_id}.webp"
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Saved generated image: {image_path}")
        return str(image_path)
    
    def save_generated_video(self, video_data: bytes, project_id: str, scene_id: str) -> str:
        """
        Save generated video
        
        Args:
            video_data: Video data as bytes
            project_id: Project ID
            scene_id: Scene ID
            
        Returns:
            Path to saved video
        """
        videos_dir = self.outputs_dir / project_id / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        
        video_path = videos_dir / f"{scene_id}.mp4"
        
        with open(video_path, 'wb') as f:
            f.write(video_data)
        
        logger.info(f"Saved generated video: {video_path}")
        return str(video_path)
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        if not path.exists():
            return {'exists': False}
        
        stat = path.stat()
        
        return {
            'exists': True,
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'extension': path.suffix,
            'name': path.name
        }
    
    def delete_project_files(self, project_id: str) -> bool:
        """
        Delete all files for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete output directory
            project_output_dir = self.outputs_dir / project_id
            if project_output_dir.exists():
                shutil.rmtree(project_output_dir)
            
            # Delete upload directory
            project_upload_dir = self.uploads_dir / project_id
            if project_upload_dir.exists():
                shutil.rmtree(project_upload_dir)
            
            logger.info(f"Deleted all files for project {project_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting files for project {project_id}: {e}")
            return False
    
    def list_project_files(self, project_id: str) -> dict:
        """
        List all files for a project
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with file lists
        """
        project_output_dir = self.outputs_dir / project_id
        project_upload_dir = self.uploads_dir / project_id
        
        def list_files_in_dir(directory: Path) -> List[dict]:
            if not directory.exists():
                return []
            
            files = []
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    files.append({
                        'path': str(file_path),
                        'name': file_path.name,
                        'size': file_path.stat().st_size,
                        'relative_path': str(file_path.relative_to(directory))
                    })
            return files
        
        return {
            'uploaded_files': list_files_in_dir(project_upload_dir),
            'generated_files': list_files_in_dir(project_output_dir),
            'images': list_files_in_dir(project_output_dir / "images"),
            'videos': list_files_in_dir(project_output_dir / "videos")
        }
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up old files
        
        Args:
            days_old: Delete files older than this many days
            
        Returns:
            Number of files deleted
        """
        import time
        
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        for directory in [self.uploads_dir, self.outputs_dir]:
            for file_path in directory.rglob('*'):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting old file {file_path}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} old files")
        return deleted_count