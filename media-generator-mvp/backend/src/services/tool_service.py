import os
import logging
import time
from typing import Dict, List, Any
from datetime import datetime

from ..core.text_analyzer import TextAnalyzer
from ..core.image_generator import ImageGenerator  
from ..core.audio_generator import AudioGenerator
from ..core.video_generator import VideoGenerator
from ..core.validator import Validator
from ..utils.file_handler import FileHandler

class ToolService:
    """Service for generating media using traditional tools (Stable Diffusion, TTS, MoviePy)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.text_analyzer = TextAnalyzer()
        self.image_generator = ImageGenerator()
        self.audio_generator = AudioGenerator()
        self.video_generator = VideoGenerator()
        self.validator = Validator()
        self.file_handler = FileHandler()
        
        self.logger.info("ToolService initialized")
    
    async def generate_media_async(
        self, 
        text_content: str, 
        project_id: str, 
        status_tracker: Dict[str, Any]
    ):
        """Generate media asynchronously and update status"""
        try:
            self.logger.info(f"Starting media generation for project {project_id}")
            start_time = time.time()
            
            # Update status
            status_tracker[project_id].update({
                "status": "processing",
                "progress": 10,
                "current_step": "Analyzing text"
            })
            
            # 1. Analyze text
            sequences = self.text_analyzer.analyze_text(text_content, max_sequences=10)
            self.logger.info(f"Analyzed text into {len(sequences)} sequences")
            
            status_tracker[project_id].update({
                "progress": 30,
                "current_step": "Generating images"
            })
            
            # 2. Generate images
            sequence_dicts = [
                {
                    'text': seq.text,
                    'summary': seq.summary,
                    'characters': seq.characters,
                    'location': seq.location,
                    'emotions': seq.emotions,
                    'action_level': seq.action_level
                }
                for seq in sequences
            ]
            
            images = self.image_generator.generate_sequence_images(sequence_dicts)
            self.logger.info(f"Generated {len(images)} images")
            
            status_tracker[project_id].update({
                "progress": 60,
                "current_step": "Generating audio"
            })
            
            # 3. Generate audio
            audio_segments = self.audio_generator.generate_sequence_audio(sequence_dicts)
            self.logger.info(f"Generated {len(audio_segments)} audio segments")
            
            status_tracker[project_id].update({
                "progress": 80,
                "current_step": "Creating video"
            })
            
            # 4. Create video
            output_dir = os.path.join("data/outputs", project_id)
            os.makedirs(output_dir, exist_ok=True)
            
            video_path = os.path.join(output_dir, f"{project_id}.mp4")
            video_success = self.video_generator.create_video_from_sequences(
                images, audio_segments, video_path
            )
            
            if not video_success:
                raise Exception("Failed to create video")
            
            self.logger.info(f"Video created at {video_path}")
            
            status_tracker[project_id].update({
                "progress": 90,
                "current_step": "Validating output"
            })
            
            # 5. Validate output
            generation_result = {
                'images': images,
                'audio_segments': audio_segments,
                'video_path': video_path,
                'sequences': sequence_dicts,
                'processing_time': time.time() - start_time
            }
            
            validation_result = self.validator.validate_output(generation_result)
            
            # 6. Save project data
            project_data = {
                'project_id': project_id,
                'title': f"Generated Content {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'status': 'completed',
                'mode': 'tool',
                'input_text': text_content[:500] + "..." if len(text_content) > 500 else text_content,
                'input_source': 'custom',
                'sequences': sequence_dicts,
                'video_path': video_path,
                'created_at': datetime.now().isoformat(),
                'completed_at': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'validation_result': {
                    'is_valid': validation_result.is_valid,
                    'quality_score': validation_result.quality_score,
                    'issues': validation_result.issues,
                    'warnings': validation_result.warnings
                },
                'quality_score': validation_result.quality_score
            }
            
            self.file_handler.save_project(project_data)
            
            # Update final status
            status_tracker[project_id].update({
                "status": "completed",
                "progress": 100,
                "current_step": "Completed",
                "video_path": video_path,
                "quality_score": validation_result.quality_score,
                "validation_result": validation_result.__dict__
            })
            
            self.logger.info(f"Media generation completed for project {project_id}")
            
        except Exception as e:
            self.logger.error(f"Error in media generation for project {project_id}: {str(e)}")
            
            # Update error status
            status_tracker[project_id].update({
                "status": "failed",
                "progress": 0,
                "current_step": "Failed",
                "error_message": str(e)
            })
            
            # Save failed project data
            try:
                project_data = {
                    'project_id': project_id,
                    'title': f"Failed Generation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'status': 'failed',
                    'mode': 'tool',
                    'input_text': text_content[:500] + "..." if len(text_content) > 500 else text_content,
                    'created_at': datetime.now().isoformat(),
                    'error_message': str(e)
                }
                self.file_handler.save_project(project_data)
            except:
                pass
    
    def generate_media(self, text_content: str) -> Dict[str, Any]:
        """Synchronous version for testing"""
        try:
            start_time = time.time()
            
            # Analyze text
            sequences = self.text_analyzer.analyze_text(text_content, max_sequences=5)
            
            # Generate images
            sequence_dicts = [
                {
                    'text': seq.text,
                    'summary': seq.summary,
                    'characters': seq.characters,
                    'location': seq.location,
                    'emotions': seq.emotions,
                    'action_level': seq.action_level
                }
                for seq in sequences
            ]
            
            images = self.image_generator.generate_sequence_images(sequence_dicts)
            
            # Generate audio
            audio_segments = self.audio_generator.generate_sequence_audio(sequence_dicts)
            
            # Create video
            project_id = f"sync_{int(time.time())}"
            output_dir = os.path.join("data/outputs", project_id)
            os.makedirs(output_dir, exist_ok=True)
            
            video_path = os.path.join(output_dir, f"{project_id}.mp4")
            video_success = self.video_generator.create_video_from_sequences(
                images, audio_segments, video_path
            )
            
            if not video_success:
                raise Exception("Failed to create video")
            
            return {
                'project_id': project_id,
                'video_path': video_path,
                'sequences': sequence_dicts,
                'images': images,
                'audio_segments': audio_segments,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Error in synchronous media generation: {str(e)}")
            raise e
