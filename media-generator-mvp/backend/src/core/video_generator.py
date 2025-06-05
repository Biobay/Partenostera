"""
Video Generator Module
Integrates the Image_to_video functionality for converting images to videos using Replicate API
"""

import os
import replicate
import base64
import io
import asyncio
from typing import List, Optional, Dict, Any
from PIL import Image
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    image_path: str = Field(..., description="Path to the input image")
    prompt: str = Field(default="", description="Prompt to guide video generation")
    seed: int = Field(default=-1, description="Seed for generation (-1 for random)")
    output_path: Optional[str] = Field(default=None, description="Path where to save the video")

class VideoGenerationResult(BaseModel):
    """Result model for video generation"""
    success: bool = Field(..., description="Whether the generation was successful")
    video_url: Optional[str] = Field(default=None, description="URL of the generated video")
    local_path: Optional[str] = Field(default=None, description="Local path of downloaded video")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")

class ReplicateVideoGenerator:
    """Video generator using Replicate's CogVideo model"""
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the video generator
        
        Args:
            api_token: Replicate API token. If None, reads from environment
        """
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        
        self.client = replicate.Client(api_token=self.api_token)
        self.model_version = "nightmareai/cogvideo:00b1c7885c5f1d44b51bcb56c378abc8f141eeacf94c1e64998606515fe63a8d"
    
    def image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Convert an image to base64 format
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string or None if failed
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG')
                img_data = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/jpeg;base64,{img_data}"
        except Exception as e:
            logger.error(f"Error converting image to base64: {e}")
            return None
    
    async def generate_video_async(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """
        Generate video from image asynchronously
        
        Args:
            request: Video generation request
            
        Returns:
            VideoGenerationResult with the result
        """
        import time
        start_time = time.time()
        
        try:
            # Check if image file exists
            if not os.path.exists(request.image_path):
                return VideoGenerationResult(
                    success=False,
                    error_message=f"Image file not found: {request.image_path}"
                )
            
            # Convert image to base64
            base64_image = self.image_to_base64(request.image_path)
            if not base64_image:
                return VideoGenerationResult(
                    success=False,
                    error_message="Failed to convert image to base64"
                )
            
            logger.info(f"Starting video generation for: {request.image_path}")
            logger.info(f"Prompt: {request.prompt}")
            logger.info(f"Seed: {request.seed}")
            
            # Prepare input for Replicate API
            input_data = {
                "image": base64_image,
                "prompt": request.prompt,
                "seed": str(request.seed)
            }
            
            # Call Replicate API in streaming mode
            video_url = None
            for event in self.client.stream(self.model_version, input=input_data):
                logger.debug(f"Received event: {event}")
                
                # If event is a URL, return it
                if isinstance(event, str) and event.startswith("http"):
                    video_url = event
                    break
            
            if video_url:
                processing_time = time.time() - start_time
                logger.info(f"Video generated successfully in {processing_time:.2f}s: {video_url}")
                
                return VideoGenerationResult(
                    success=True,
                    video_url=video_url,
                    processing_time=processing_time
                )
            else:
                return VideoGenerationResult(
                    success=False,
                    error_message="No video URL received from Replicate"
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Error during video generation: {str(e)}"
            logger.error(error_msg)
            
            return VideoGenerationResult(
                success=False,
                error_message=error_msg,
                processing_time=processing_time
            )
    
    def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """
        Generate video from image synchronously
        
        Args:
            request: Video generation request
            
        Returns:
            VideoGenerationResult with the result
        """
        # Run async function in sync context
        return asyncio.run(self.generate_video_async(request))
    
    async def generate_videos_from_images(
        self, 
        image_paths: List[str], 
        prompt: str = "", 
        seed: int = -1
    ) -> List[VideoGenerationResult]:
        """
        Generate videos from multiple images
        
        Args:
            image_paths: List of image file paths
            prompt: Prompt for video generation
            seed: Seed for generation
            
        Returns:
            List of VideoGenerationResult
        """
        results = []
        
        for image_path in image_paths:
            request = VideoGenerationRequest(
                image_path=image_path,
                prompt=prompt,
                seed=seed
            )
            
            result = await self.generate_video_async(request)
            results.append(result)
            
            # Add small delay between requests to avoid rate limiting
            if len(image_paths) > 1:
                await asyncio.sleep(1)
        
        return results

class VideoProcessor:
    """High-level video processor that combines scene images into videos"""
    
    def __init__(self, video_generator: Optional[ReplicateVideoGenerator] = None):
        """
        Initialize video processor
        
        Args:
            video_generator: Video generator instance. If None, creates a new one
        """
        self.video_generator = video_generator or ReplicateVideoGenerator()
    
    async def process_scene_images_to_videos(
        self, 
        scene_images: List[Dict[str, Any]], 
        base_prompt: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Process scene images to videos
        
        Args:
            scene_images: List of scene image data with paths and metadata
            base_prompt: Base prompt for video generation
            
        Returns:
            List of scenes with video data added
        """
        results = []
        
        for scene_data in scene_images:
            image_path = scene_data.get('image_path')
            scene_prompt = scene_data.get('prompt', '')
            scene_id = scene_data.get('scene_id', 'unknown')
            
            if not image_path or not os.path.exists(image_path):
                logger.warning(f"Image not found for scene {scene_id}: {image_path}")
                results.append({
                    **scene_data,
                    'video_generation': {
                        'success': False,
                        'error': 'Image file not found'
                    }
                })
                continue
            
            # Combine base prompt with scene-specific prompt
            full_prompt = f"{base_prompt} {scene_prompt}".strip()
            
            request = VideoGenerationRequest(
                image_path=image_path,
                prompt=full_prompt,
                seed=-1  # Random seed for variety
            )
            
            video_result = await self.video_generator.generate_video_async(request)
            
            # Add video result to scene data
            scene_with_video = {
                **scene_data,
                'video_generation': {
                    'success': video_result.success,
                    'video_url': video_result.video_url,
                    'error': video_result.error_message,
                    'processing_time': video_result.processing_time
                }
            }
            
            results.append(scene_with_video)
            
            logger.info(f"Processed scene {scene_id}: {'✅' if video_result.success else '❌'}")
        
        return results

# Factory function for easy instantiation
def create_video_generator(api_token: Optional[str] = None) -> ReplicateVideoGenerator:
    """
    Create a video generator instance
    
    Args:
        api_token: Replicate API token
        
    Returns:
        ReplicateVideoGenerator instance
    """
    return ReplicateVideoGenerator(api_token)

def create_video_processor(api_token: Optional[str] = None) -> VideoProcessor:
    """
    Create a video processor instance
    
    Args:
        api_token: Replicate API token
        
    Returns:
        VideoProcessor instance
    """
    video_generator = create_video_generator(api_token)
    return VideoProcessor(video_generator)