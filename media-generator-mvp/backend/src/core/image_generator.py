import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import logging
import os
from typing import List, Optional
import hashlib
import time

class ImageGenerator:
    """Generates images using Stable Diffusion"""
    
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        self.logger = logging.getLogger(__name__)
        self.model_id = model_id
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the Stable Diffusion pipeline"""
        try:
            self.logger.info(f"Initializing Stable Diffusion pipeline on {self.device}")
            
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True
            )
            
            self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory efficient attention if on CUDA
            if self.device == "cuda":
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_xformers_memory_efficient_attention()
            
            self.logger.info("Stable Diffusion pipeline initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Stable Diffusion: {str(e)}")
            self.pipeline = None
    
    def generate_image(
        self, 
        prompt: str, 
        negative_prompt: str = None,
        width: int = 1024,
        height: int = 1024,
        num_inference_steps: int = 20,
        guidance_scale: float = 7.5,
        seed: Optional[int] = None
    ) -> Optional[Image.Image]:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the image
            negative_prompt: What to avoid in the image
            width: Image width
            height: Image height
            num_inference_steps: Number of denoising steps
            guidance_scale: How closely to follow the prompt
            seed: Random seed for reproducibility
            
        Returns:
            PIL Image or None if generation fails
        """
        if self.pipeline is None:
            self.logger.error("Pipeline not initialized")
            return self._generate_placeholder_image(width, height)
        
        try:
            # Set seed for reproducibility
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
            
            # Default negative prompt
            if negative_prompt is None:
                negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy"
            
            self.logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            start_time = time.time()
            
            # Generate image
            result = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
            
            generation_time = time.time() - start_time
            self.logger.info(f"Image generated in {generation_time:.2f} seconds")
            
            return result.images[0]
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            return self._generate_placeholder_image(width, height)
    
    def generate_sequence_images(
        self, 
        sequences: List[dict],
        style_prompt: str = "cinematic, high quality, detailed",
        consistent_seed: bool = True
    ) -> List[Image.Image]:
        """
        Generate a sequence of coherent images for narrative sequences
        
        Args:
            sequences: List of sequence dictionaries with text and metadata
            style_prompt: Common style elements for consistency
            consistent_seed: Whether to use similar seeds for consistency
            
        Returns:
            List of PIL Images
        """
        images = []
        base_seed = hash(sequences[0].get('text', '')) % 1000000 if consistent_seed else None
        
        for i, sequence in enumerate(sequences):
            try:
                # Create detailed prompt
                prompt = self._create_detailed_prompt(sequence, style_prompt)
                
                # Use incremental seed for consistency
                seed = base_seed + i if base_seed is not None else None
                
                # Generate image
                image = self.generate_image(
                    prompt=prompt,
                    seed=seed,
                    width=1024,
                    height=1024,
                    num_inference_steps=25,
                    guidance_scale=7.5
                )
                
                images.append(image)
                self.logger.info(f"Generated image {i+1}/{len(sequences)}")
                
            except Exception as e:
                self.logger.error(f"Error generating image for sequence {i}: {str(e)}")
                images.append(self._generate_placeholder_image(1024, 1024))
        
        return images
    
    def _create_detailed_prompt(self, sequence: dict, style_prompt: str) -> str:
        """Create a detailed prompt from sequence metadata"""
        base_text = sequence.get('summary', sequence.get('text', ''))[:200]
        
        # Add character information
        characters = sequence.get('characters', [])
        if characters:
            char_desc = f", featuring {', '.join(characters[:2])}"
        else:
            char_desc = ""
        
        # Add location
        location = sequence.get('location', '')
        if location and location != "Non specificato":
            location_desc = f", in {location}"
        else:
            location_desc = ""
        
        # Add emotion/mood
        emotions = sequence.get('emotions', ['neutrale'])
        emotion_desc = f", {emotions[0]} mood" if emotions else ""
        
        # Add action level description
        action_level = sequence.get('action_level', 0.5)
        if action_level > 0.7:
            action_desc = ", dynamic action scene"
        elif action_level < 0.3:
            action_desc = ", peaceful calm scene"
        else:
            action_desc = ""
        
        # Combine all elements
        full_prompt = f"{base_text}{char_desc}{location_desc}{emotion_desc}{action_desc}, {style_prompt}"
        
        return full_prompt
    
    def _generate_placeholder_image(self, width: int, height: int) -> Image.Image:
        """Generate a simple placeholder image when generation fails"""
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple colored rectangle
        image = Image.new('RGB', (width, height), color='lightgray')
        draw = ImageDraw.Draw(image)
        
        # Add text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text = "Immagine non disponibile"
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            draw.text((x, y), text, fill='black', font=font)
        
        return image
    
    def save_image(self, image: Image.Image, filepath: str) -> bool:
        """Save image to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            image.save(filepath, quality=95, optimize=True)
            return True
        except Exception as e:
            self.logger.error(f"Error saving image to {filepath}: {str(e)}")
            return False
