import os
import io
import logging
from typing import List, Optional
import torch
import torchaudio
from TTS.api import TTS
import numpy as np
from pydub import AudioSegment
import tempfile

class AudioGenerator:
    """Generates audio using TTS (Text-to-Speech)"""
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.tts = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize TTS
        self._initialize_tts()
    
    def _initialize_tts(self):
        """Initialize the TTS model"""
        try:
            self.logger.info(f"Initializing TTS model: {self.model_name}")
            
            # Initialize TTS with the specified model
            self.tts = TTS(
                model_name=self.model_name,
                gpu=torch.cuda.is_available()
            )
            
            self.logger.info("TTS model initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS model: {str(e)}")
            # Try with a simpler model as fallback
            try:
                self.logger.info("Trying fallback TTS model...")
                self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                self.logger.info("Fallback TTS model initialized")
            except Exception as e2:
                self.logger.error(f"Fallback TTS also failed: {str(e2)}")
                self.tts = None
    
    def generate_audio(
        self, 
        text: str, 
        language: str = "it",
        speaker: Optional[str] = None,
        emotion: str = "neutral",
        speed: float = 1.0
    ) -> Optional[bytes]:
        """
        Generate audio from text
        
        Args:
            text: Text to convert to speech
            language: Language code (it, en, etc.)
            speaker: Speaker voice to use
            emotion: Emotion to convey
            speed: Speech speed multiplier
            
        Returns:
            Audio data as bytes or None if generation fails
        """
        if self.tts is None:
            self.logger.error("TTS model not initialized")
            return self._generate_silence(duration=3.0)
        
        try:
            self.logger.info(f"Generating audio for text: {text[:50]}...")
            
            # Clean text for better TTS
            cleaned_text = self._clean_text_for_tts(text)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                # Generate audio with TTS
                if hasattr(self.tts, 'tts_to_file'):
                    self.tts.tts_to_file(
                        text=cleaned_text,
                        file_path=tmp_path,
                        language=language if language in ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja"] else "en"
                    )
                else:
                    # Fallback method
                    wav = self.tts.tts(text=cleaned_text, language=language)
                    torchaudio.save(tmp_path, torch.tensor(wav).unsqueeze(0), 22050)
                
                # Load and process audio
                audio = AudioSegment.from_wav(tmp_path)
                
                # Apply speed modification
                if speed != 1.0:
                    audio = audio.speedup(playback_speed=speed)
                
                # Convert to bytes
                buffer = io.BytesIO()
                audio.export(buffer, format="wav")
                audio_bytes = buffer.getvalue()
                
                # Cleanup
                os.unlink(tmp_path)
                
                self.logger.info("Audio generated successfully")
                return audio_bytes
                
            except Exception as e:
                # Cleanup on error
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise e
                
        except Exception as e:
            self.logger.error(f"Error generating audio: {str(e)}")
            return self._generate_silence(duration=len(text) * 0.1)  # Rough estimation
    
    def generate_sequence_audio(
        self, 
        sequences: List[dict],
        language: str = "it",
        narrator_voice: Optional[str] = None,
        add_pauses: bool = True
    ) -> List[bytes]:
        """
        Generate audio for a sequence of text segments
        
        Args:
            sequences: List of sequence dictionaries
            language: Language for TTS
            narrator_voice: Specific voice to use
            add_pauses: Whether to add pauses between sequences
            
        Returns:
            List of audio data as bytes
        """
        audio_segments = []
        
        for i, sequence in enumerate(sequences):
            try:
                text = sequence.get('text', sequence.get('summary', ''))
                
                # Adjust emotion based on sequence metadata
                emotions = sequence.get('emotions', ['neutrale'])
                emotion = self._map_emotion_to_tts(emotions[0])
                
                # Adjust speed based on action level
                action_level = sequence.get('action_level', 0.5)
                speed = 0.9 + (action_level * 0.3)  # 0.9 to 1.2
                
                # Generate audio
                audio_data = self.generate_audio(
                    text=text,
                    language=language,
                    speaker=narrator_voice,
                    emotion=emotion,
                    speed=speed
                )
                
                if audio_data:
                    audio_segments.append(audio_data)
                    
                    # Add pause between sequences
                    if add_pauses and i < len(sequences) - 1:
                        pause = self._generate_silence(duration=0.5)
                        audio_segments.append(pause)
                
                self.logger.info(f"Generated audio for sequence {i+1}/{len(sequences)}")
                
            except Exception as e:
                self.logger.error(f"Error generating audio for sequence {i}: {str(e)}")
                # Add silence as fallback
                audio_segments.append(self._generate_silence(duration=3.0))
        
        return audio_segments
    
    def combine_audio_segments(self, audio_segments: List[bytes]) -> bytes:
        """Combine multiple audio segments into one"""
        try:
            combined = AudioSegment.empty()
            
            for audio_data in audio_segments:
                if audio_data:
                    segment = AudioSegment.from_wav(io.BytesIO(audio_data))
                    combined += segment
            
            # Export combined audio
            buffer = io.BytesIO()
            combined.export(buffer, format="wav")
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error combining audio segments: {str(e)}")
            return self._generate_silence(duration=10.0)
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        import re
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Replace some problematic characters
        text = text.replace('"', '')
        text = text.replace("'", "'")
        text = text.replace('—', '-')
        text = text.replace('–', '-')
        
        # Ensure sentences end properly
        if not text.endswith(('.', '!', '?')):
            text += '.'
        
        # Limit length for TTS
        if len(text) > 500:
            # Split at sentence boundaries and take first part
            sentences = re.split(r'[.!?]+', text)
            total_length = 0
            result_sentences = []
            
            for sentence in sentences:
                if total_length + len(sentence) < 500:
                    result_sentences.append(sentence)
                    total_length += len(sentence)
                else:
                    break
            
            text = '. '.join(result_sentences) + '.'
        
        return text.strip()
    
    def _map_emotion_to_tts(self, emotion: str) -> str:
        """Map our emotion categories to TTS-compatible emotions"""
        emotion_mapping = {
            "gioia": "happy",
            "tristezza": "sad",
            "paura": "fearful", 
            "rabbia": "angry",
            "sorpresa": "surprised",
            "amore": "warm",
            "neutrale": "neutral"
        }
        
        return emotion_mapping.get(emotion, "neutral")
    
    def _generate_silence(self, duration: float) -> bytes:
        """Generate silence audio of specified duration"""
        try:
            # Create silence
            silence = AudioSegment.silent(duration=int(duration * 1000))  # Convert to milliseconds
            
            # Export to bytes
            buffer = io.BytesIO()
            silence.export(buffer, format="wav")
            return buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error generating silence: {str(e)}")
            # Return minimal audio data
            return b'\x00' * 1024
    
    def save_audio(self, audio_data: bytes, filepath: str) -> bool:
        """Save audio data to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(audio_data)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving audio to {filepath}: {str(e)}")
            return False
