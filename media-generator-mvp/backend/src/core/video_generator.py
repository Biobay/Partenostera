import os
import logging
import tempfile
import io
from typing import List, Tuple, Optional
from PIL import Image
import moviepy.editor as mp
from moviepy.video.fx.all import resize, fadein, fadeout
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
import numpy as np

class VideoGenerator:
    """Generates videos by combining images and audio"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
    
    def create_video_from_sequences(
        self,
        images: List[Image.Image],
        audio_segments: List[bytes],
        output_path: str,
        fps: int = 24,
        transition_duration: float = 0.5,
        image_display_time: float = None
    ) -> bool:
        """
        Create a video from images and audio segments
        
        Args:
            images: List of PIL Images
            audio_segments: List of audio data in bytes
            output_path: Path where to save the video
            fps: Frames per second
            transition_duration: Duration of transitions between images
            image_display_time: How long to display each image (auto if None)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Starting video creation...")
            
            if len(images) != len(audio_segments):
                self.logger.warning(f"Mismatch: {len(images)} images vs {len(audio_segments)} audio segments")
                # Pad with silence or duplicate last elements as needed
                images, audio_segments = self._balance_sequences(images, audio_segments)
            
            # Calculate timing
            audio_durations = self._get_audio_durations(audio_segments)
            
            if image_display_time is None:
                image_durations = audio_durations
            else:
                image_durations = [image_display_time] * len(images)
            
            # Create video clips for each image
            video_clips = self._create_image_clips(images, image_durations, fps, transition_duration)
            
            # Create audio clips
            audio_clips = self._create_audio_clips(audio_segments)
            
            # Combine everything
            final_video = self._combine_clips(video_clips, audio_clips, transition_duration)
            
            # Save video
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            self.logger.info(f"Rendering video to {output_path}...")
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None  # Suppress moviepy logs
            )
            
            # Cleanup
            final_video.close()
            self._cleanup_temp_files()
            
            self.logger.info("Video created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating video: {str(e)}")
            self._cleanup_temp_files()
            return False
    
    def _balance_sequences(
        self, 
        images: List[Image.Image], 
        audio_segments: List[bytes]
    ) -> Tuple[List[Image.Image], List[bytes]]:
        """Balance the number of images and audio segments"""
        target_length = max(len(images), len(audio_segments))
        
        # Extend images if needed
        while len(images) < target_length:
            if images:
                images.append(images[-1])  # Duplicate last image
            else:
                # Create placeholder if no images
                images.append(self._create_placeholder_image())
        
        # Extend audio if needed
        while len(audio_segments) < target_length:
            if audio_segments:
                audio_segments.append(audio_segments[-1])  # Duplicate last audio
            else:
                # Create silence if no audio
                audio_segments.append(self._create_silence_bytes(3.0))
        
        return images[:target_length], audio_segments[:target_length]
    
    def _get_audio_durations(self, audio_segments: List[bytes]) -> List[float]:
        """Get duration of each audio segment"""
        durations = []
        
        for audio_data in audio_segments:
            try:
                # Save to temp file to analyze
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(audio_data)
                    temp_path = f.name
                
                # Load with moviepy to get duration
                audio_clip = mp.AudioFileClip(temp_path)
                durations.append(audio_clip.duration)
                audio_clip.close()
                
                # Cleanup
                os.unlink(temp_path)
                
            except Exception as e:
                self.logger.warning(f"Could not determine audio duration: {str(e)}")
                durations.append(3.0)  # Default 3 seconds
        
        return durations
    
    def _create_image_clips(
        self, 
        images: List[Image.Image], 
        durations: List[float], 
        fps: int,
        transition_duration: float
    ) -> List[mp.VideoClip]:
        """Create video clips from images"""
        clips = []
        
        for i, (image, duration) in enumerate(zip(images, durations)):
            try:
                # Save image to temp file
                temp_path = os.path.join(self.temp_dir, f"image_{i}.png")
                image.save(temp_path, 'PNG')
                
                # Create image clip
                clip = mp.ImageClip(temp_path, duration=duration)
                
                # Resize to standard resolution
                clip = resize(clip, height=720)  # 720p
                
                # Add fade effects
                if transition_duration > 0:
                    clip = fadein(clip, transition_duration)
                    clip = fadeout(clip, transition_duration)
                
                clips.append(clip)
                
            except Exception as e:
                self.logger.error(f"Error creating clip for image {i}: {str(e)}")
                # Create a black clip as fallback
                clips.append(mp.ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration))
        
        return clips
    
    def _create_audio_clips(self, audio_segments: List[bytes]) -> List[mp.AudioClip]:
        """Create audio clips from audio data"""
        clips = []
        
        for i, audio_data in enumerate(audio_segments):
            try:
                # Save audio to temp file
                temp_path = os.path.join(self.temp_dir, f"audio_{i}.wav")
                with open(temp_path, 'wb') as f:
                    f.write(audio_data)
                
                # Create audio clip
                audio_clip = mp.AudioFileClip(temp_path)
                
                # Add fade effects
                audio_clip = audio_fadein(audio_clip, 0.1)
                audio_clip = audio_fadeout(audio_clip, 0.1)
                
                clips.append(audio_clip)
                
            except Exception as e:
                self.logger.error(f"Error creating audio clip {i}: {str(e)}")
                # Create silent audio as fallback
                clips.append(mp.AudioClip(lambda t: [0, 0], duration=3.0))
        
        return clips
    
    def _combine_clips(
        self, 
        video_clips: List[mp.VideoClip], 
        audio_clips: List[mp.AudioClip],
        transition_duration: float
    ) -> mp.VideoClip:
        """Combine video and audio clips into final video"""
        try:
            # Synchronize video and audio durations
            synchronized_clips = []
            
            for video_clip, audio_clip in zip(video_clips, audio_clips):
                # Match video duration to audio duration
                video_duration = audio_clip.duration
                video_clip = video_clip.set_duration(video_duration)
                
                # Set audio to video clip
                final_clip = video_clip.set_audio(audio_clip)
                synchronized_clips.append(final_clip)
            
            # Concatenate all clips
            if len(synchronized_clips) == 1:
                final_video = synchronized_clips[0]
            else:
                final_video = mp.concatenate_videoclips(
                    synchronized_clips, 
                    transition=mp.CompositeVideoClip if transition_duration > 0 else None
                )
            
            return final_video
            
        except Exception as e:
            self.logger.error(f"Error combining clips: {str(e)}")
            # Return a simple black video as fallback
            return mp.ColorClip(size=(1280, 720), color=(0, 0, 0), duration=10)
    
    def _create_placeholder_image(self) -> Image.Image:
        """Create a placeholder image"""
        image = Image.new('RGB', (1280, 720), color='black')
        return image
    
    def _create_silence_bytes(self, duration: float) -> bytes:
        """Create silence audio data"""
        try:
            from pydub import AudioSegment
            silence = AudioSegment.silent(duration=int(duration * 1000))
            buffer = io.BytesIO()
            silence.export(buffer, format="wav")
            return buffer.getvalue()
        except:
            return b'\x00' * 1024
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.temp_dir = tempfile.mkdtemp()
        except Exception as e:
            self.logger.warning(f"Could not clean up temp files: {str(e)}")
    
    def add_subtitles(
        self, 
        video_path: str, 
        sequences: List[dict], 
        output_path: str
    ) -> bool:
        """Add subtitles to video"""
        try:
            from moviepy.video.tools.subtitles import SubtitlesClip
            
            # Create subtitle file
            subtitle_data = []
            current_time = 0
            
            for sequence in sequences:
                text = sequence.get('summary', sequence.get('text', ''))[:100]
                duration = 3.0  # Default duration
                
                subtitle_data.append(((current_time, current_time + duration), text))
                current_time += duration
            
            # Load video
            video = mp.VideoFileClip(video_path)
            
            # Create subtitles
            subtitles = SubtitlesClip(subtitle_data, 
                                    font='Arial-Bold', 
                                    fontsize=24, 
                                    color='white')
            
            # Composite video with subtitles
            final_video = mp.CompositeVideoClip([video, subtitles])
            
            # Save
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Cleanup
            video.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding subtitles: {str(e)}")
            return False
