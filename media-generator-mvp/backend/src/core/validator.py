import logging
import time
import os
from typing import Dict, List, Any, Tuple
from PIL import Image
import numpy as np
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Result of validation process"""
    is_valid: bool
    quality_score: float
    issues: List[str]
    warnings: List[str]
    processing_time: float

class Validator:
    """Validates generated content for quality and safety"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.min_image_quality = 0.7
        self.min_audio_quality = 0.6
        self.max_processing_time = 300  # 5 minutes
        
        # Content safety keywords to avoid
        self.unsafe_keywords = [
            "violence", "violenza", "sangue", "morte", "uccidere",
            "droga", "drug", "hate", "odio", "razzismo", "racism"
        ]
    
    def validate_output(self, generation_result: Dict[str, Any]) -> ValidationResult:
        """
        Comprehensive validation of generated content
        
        Args:
            generation_result: Dictionary containing all generated content
            
        Returns:
            ValidationResult with validation details
        """
        start_time = time.time()
        issues = []
        warnings = []
        
        try:
            self.logger.info("Starting content validation...")
            
            # Validate images
            if 'images' in generation_result:
                image_issues = self._validate_images(generation_result['images'])
                issues.extend(image_issues)
            
            # Validate audio
            if 'audio_segments' in generation_result:
                audio_issues = self._validate_audio(generation_result['audio_segments'])
                issues.extend(audio_issues)
            
            # Validate video
            if 'video_path' in generation_result:
                video_issues = self._validate_video(generation_result['video_path'])
                issues.extend(video_issues)
            
            # Validate content safety
            if 'sequences' in generation_result:
                safety_issues = self._validate_content_safety(generation_result['sequences'])
                issues.extend(safety_issues)
            
            # Check processing time
            processing_time = generation_result.get('processing_time', 0)
            if processing_time > self.max_processing_time:
                warnings.append(f"Processing time exceeded expected duration: {processing_time:.1f}s")
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(generation_result, issues, warnings)
            
            # Determine if content is valid
            is_valid = len(issues) == 0 and quality_score >= 0.6
            
            validation_time = time.time() - start_time
            
            result = ValidationResult(
                is_valid=is_valid,
                quality_score=quality_score,
                issues=issues,
                warnings=warnings,
                processing_time=validation_time
            )
            
            self.logger.info(f"Validation completed: {'PASSED' if is_valid else 'FAILED'} "
                           f"(Score: {quality_score:.2f})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return ValidationResult(
                is_valid=False,
                quality_score=0.0,
                issues=[f"Validation failed: {str(e)}"],
                warnings=[],
                processing_time=time.time() - start_time
            )
    
    def _validate_images(self, images: List[Image.Image]) -> List[str]:
        """Validate generated images"""
        issues = []
        
        try:
            if not images:
                issues.append("No images generated")
                return issues
            
            for i, image in enumerate(images):
                if image is None:
                    issues.append(f"Image {i+1} is None")
                    continue
                
                # Check image dimensions
                width, height = image.size
                if width < 512 or height < 512:
                    issues.append(f"Image {i+1} resolution too low: {width}x{height}")
                
                # Check if image is not blank
                if self._is_image_blank(image):
                    issues.append(f"Image {i+1} appears to be blank")
                
                # Check image quality (basic metrics)
                quality = self._assess_image_quality(image)
                if quality < self.min_image_quality:
                    issues.append(f"Image {i+1} quality too low: {quality:.2f}")
            
        except Exception as e:
            issues.append(f"Error validating images: {str(e)}")
        
        return issues
    
    def _validate_audio(self, audio_segments: List[bytes]) -> List[str]:
        """Validate generated audio"""
        issues = []
        
        try:
            if not audio_segments:
                issues.append("No audio generated")
                return issues
            
            for i, audio_data in enumerate(audio_segments):
                if not audio_data or len(audio_data) < 1000:  # Very short audio
                    issues.append(f"Audio segment {i+1} is too short or empty")
                
                # Basic audio validation
                if not self._is_valid_audio_data(audio_data):
                    issues.append(f"Audio segment {i+1} has invalid format")
            
        except Exception as e:
            issues.append(f"Error validating audio: {str(e)}")
        
        return issues
    
    def _validate_video(self, video_path: str) -> List[str]:
        """Validate generated video"""
        issues = []
        
        try:
            if not video_path or not os.path.exists(video_path):
                issues.append("Video file not found")
                return issues
            
            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size < 1000:  # Very small file
                issues.append("Video file too small, likely corrupted")
            
            # Check file extension
            if not video_path.lower().endswith(('.mp4', '.avi', '.mov')):
                issues.append("Invalid video file format")
            
            # Try to get video info using moviepy
            try:
                import moviepy.editor as mp
                video = mp.VideoFileClip(video_path)
                
                if video.duration < 1.0:
                    issues.append("Video duration too short")
                
                if video.w < 480 or video.h < 360:
                    issues.append(f"Video resolution too low: {video.w}x{video.h}")
                
                video.close()
                
            except Exception as e:
                issues.append(f"Could not analyze video: {str(e)}")
            
        except Exception as e:
            issues.append(f"Error validating video: {str(e)}")
        
        return issues
    
    def _validate_content_safety(self, sequences: List[Dict]) -> List[str]:
        """Check content for safety issues"""
        issues = []
        
        try:
            for i, sequence in enumerate(sequences):
                text = sequence.get('text', '') + ' ' + sequence.get('summary', '')
                text_lower = text.lower()
                
                # Check for unsafe keywords
                for keyword in self.unsafe_keywords:
                    if keyword in text_lower:
                        issues.append(f"Potentially unsafe content in sequence {i+1}: '{keyword}'")
                
                # Check for extremely negative emotions
                emotions = sequence.get('emotions', [])
                if 'violence' in emotions or 'hate' in emotions:
                    issues.append(f"Inappropriate emotional content in sequence {i+1}")
            
        except Exception as e:
            issues.append(f"Error validating content safety: {str(e)}")
        
        return issues
    
    def _is_image_blank(self, image: Image.Image) -> bool:
        """Check if image is mostly blank"""
        try:
            # Convert to grayscale and get variance
            gray = image.convert('L')
            np_image = np.array(gray)
            variance = np.var(np_image)
            
            # If variance is very low, image is likely blank
            return variance < 100
            
        except Exception:
            return False
    
    def _assess_image_quality(self, image: Image.Image) -> float:
        """Assess image quality using basic metrics"""
        try:
            # Convert to numpy array
            np_image = np.array(image.convert('RGB'))
            
            # Calculate metrics
            variance = np.var(np_image)
            mean_brightness = np.mean(np_image)
            
            # Simple quality score based on variance and brightness
            # High variance usually means more detail
            # Avoid too bright or too dark images
            variance_score = min(variance / 1000, 1.0)  # Normalize
            brightness_score = 1.0 - abs(mean_brightness - 128) / 128  # Penalize extreme brightness
            
            quality = (variance_score * 0.7 + brightness_score * 0.3)
            return max(0.0, min(1.0, quality))
            
        except Exception:
            return 0.5  # Default neutral score
    
    def _is_valid_audio_data(self, audio_data: bytes) -> bool:
        """Basic validation of audio data format"""
        try:
            # Check if it starts with WAV header
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                return True
            
            # Check for other common audio formats
            if audio_data.startswith((b'ID3', b'\xff\xfb', b'\xff\xf3', b'\xff\xf2')):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _calculate_quality_score(
        self, 
        generation_result: Dict[str, Any], 
        issues: List[str], 
        warnings: List[str]
    ) -> float:
        """Calculate overall quality score"""
        try:
            base_score = 1.0
            
            # Penalize for issues
            issue_penalty = len(issues) * 0.2
            warning_penalty = len(warnings) * 0.1
            
            # Bonus for completeness
            completeness_bonus = 0.0
            if 'images' in generation_result and generation_result['images']:
                completeness_bonus += 0.3
            if 'audio_segments' in generation_result and generation_result['audio_segments']:
                completeness_bonus += 0.3
            if 'video_path' in generation_result and os.path.exists(generation_result.get('video_path', '')):
                completeness_bonus += 0.4
            
            # Calculate final score
            final_score = base_score - issue_penalty - warning_penalty + completeness_bonus
            
            return max(0.0, min(1.0, final_score))
            
        except Exception:
            return 0.5
    
    def create_validation_report(self, result: ValidationResult) -> str:
        """Create a human-readable validation report"""
        report = f"""
=== VALIDATION REPORT ===
Status: {'✅ PASSED' if result.is_valid else '❌ FAILED'}
Quality Score: {result.quality_score:.2f}/1.00
Processing Time: {result.processing_time:.2f}s

"""
        
        if result.issues:
            report += "🚨 ISSUES:\n"
            for issue in result.issues:
                report += f"  - {issue}\n"
            report += "\n"
        
        if result.warnings:
            report += "⚠️  WARNINGS:\n"
            for warning in result.warnings:
                report += f"  - {warning}\n"
            report += "\n"
        
        if not result.issues and not result.warnings:
            report += "✅ No issues found!\n\n"
        
        report += "=== END REPORT ===\n"
        
        return report
