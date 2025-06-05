"""
Image Generator Core Module
Integrates AI Horde for image generation from text prompts
"""

import asyncio
import requests
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIHordeImageGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AI_HORDE_API_KEY", "xbCXATE-9l8CPYqfojI9iQ")
        self.base_url = "https://stablehorde.net/api/v2"
        self.session = requests.Session()
        self.session.headers.update({
            "apikey": self.api_key,
            "Content-Type": "application/json"
        })
        self.output_dir = Path("data/outputs/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_images_from_chunks(self, chunks: List[Dict[str, Any]], project_id: str) -> List[Dict[str, Any]]:
        """
        Generate images for all chunks in a project
        """
        generated_images = []
        
        for i, chunk in enumerate(chunks):
            print(f"🎨 Generating image {i+1}/{len(chunks)} for project {project_id}")
            
            try:
                image_result = await self.generate_image(
                    prompt=chunk.get('image_prompt', ''),
                    project_id=project_id,
                    order=i + 1
                )
                
                if image_result:
                    generated_images.append({
                        "id": f"img_{project_id}_{i+1}",
                        "url": image_result["url"],
                        "prompt": chunk.get('image_prompt', ''),
                        "order": i + 1,
                        "status": "completed",
                        "validated": True,
                        "timestamp": time.time()
                    })
                else:
                    print(f"❌ Failed to generate image for chunk {i+1}")
                    
            except Exception as e:
                print(f"❌ Error generating image for chunk {i+1}: {e}")
                
        return generated_images

    async def generate_image(self, prompt: str, project_id: str, order: int, width: int = 512, height: int = 512, steps: int = 25, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a single image using AI Horde
        """
        # If no model specified, get a popular one
        if model is None:
            models = await self.get_available_models()
            if models:
                # Choose a model with many workers
                popular_models = sorted(models, key=lambda x: x.get('count', 0), reverse=True)
                model = popular_models[0]['name']
            else:
                model = "stable_diffusion"  # fallback
        
        payload = {
            "prompt": prompt,
            "params": {
                "width": width,
                "height": height,
                "steps": steps,
                "sampler_name": "k_euler_a",
                "cfg_scale": 7.5,
                "seed_variation": 1,
                "post_processing": ["RealESRGAN_x4plus"]
            },
            "models": [model],
            "r2": True,
            "shared": False,
            "replacement_filter": True
        }
        
        print(f"🎨 Generating image with prompt: {prompt[:50]}...")
        print(f"📐 Dimensions: {width}x{height}")
        print(f"🤖 Model: {model}")
        
        try:
            # Submit request
            response = await asyncio.to_thread(
                self.session.post,
                f"{self.base_url}/generate/async",
                json=payload,
                timeout=15
            )
            
            if response.status_code != 202:
                print(f"❌ Error submitting request: {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            result = response.json()
            job_id = result.get("id")
            
            if not job_id:
                print("❌ No job ID received")
                return None
            
            print(f"✅ Request submitted! Job ID: {job_id}")
            
            # Wait and download
            return await self.wait_and_download(job_id, project_id, order)
            
        except Exception as e:
            print(f"❌ Error in image generation: {e}")
            return None
    
    async def wait_and_download(self, job_id: str, project_id: str, order: int) -> Optional[Dict[str, Any]]:
        """
        Wait for completion and download the result
        """
        max_wait = 300  # 5 minutes
        start_time = time.time()
        
        print("⏳ Waiting for completion...")
        
        while time.time() - start_time < max_wait:
            try:
                # Check status
                response = await asyncio.to_thread(
                    self.session.get,
                    f"{self.base_url}/generate/check/{job_id}",
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"❌ Error checking status: {response.status_code}")
                    return None
                
                status = response.json()
                
                # Show progress
                queue_pos = status.get("queue_position", 0)
                wait_time = status.get("wait_time", 0)
                
                if queue_pos > 0:
                    print(f"📊 Position {queue_pos}, wait ~{wait_time}s")
                
                # Check if completed
                if status.get("done", False):
                    print("✅ Generation completed!")
                    return await self.download_result(job_id, project_id, order)
                
                # Check if failed
                if status.get("faulted", False):
                    print("❌ Generation failed")
                    return None
                
                await asyncio.sleep(5)  # Wait 5 seconds
                
            except Exception as e:
                print(f"❌ Error monitoring: {e}")
                return None
        
        print("⏰ Timeout reached")
        return None
    
    async def download_result(self, job_id: str, project_id: str, order: int) -> Optional[Dict[str, Any]]:
        """
        Download the generated image
        """
        try:
            # Get result status
            response = await asyncio.to_thread(
                self.session.get,
                f"{self.base_url}/generate/status/{job_id}",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"❌ Error getting result status: {response.status_code}")
                return None
            
            status = response.json()
            generations = status.get("generations", [])
            
            if not generations:
                print("❌ No generations found")
                return None
            
            # Download first generation
            generation = generations[0]
            img_url = generation.get("img")
            
            if not img_url:
                print("❌ No image URL found")
                return None
            
            # Download image
            img_response = await asyncio.to_thread(
                requests.get,
                img_url,
                timeout=30
            )
            
            if img_response.status_code != 200:
                print(f"❌ Error downloading image: {img_response.status_code}")
                return None
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_horde_{project_id}_{order}_{timestamp}.webp"
            filepath = self.output_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            
            print(f"💾 Image saved: {filepath}")
            
            return {
                "url": f"/api/images/{filename}",
                "local_path": str(filepath),
                "filename": filename
            }
            
        except Exception as e:
            print(f"❌ Error downloading result: {e}")
            return None
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models
        """
        try:
            response = await asyncio.to_thread(
                requests.get,
                f"{self.base_url}/status/models",
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json()
                # Filter only active models
                return [m for m in models if m.get('count', 0) > 0]
            return []
        except Exception as e:
            print(f"❌ Error getting models: {e}")
            return []
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get user information
        """
        try:
            response = self.session.get(f"{self.base_url}/find_user", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None

class ImageGenerator:
    """
    Main Image Generator class that coordinates different image generation services
    """
    def __init__(self):
        self.ai_horde = AIHordeImageGenerator()
    
    async def generate_images(self, project_id: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate images for a project using AI Horde
        """
        print(f"🎨 Starting image generation for project {project_id}")
        print(f"📋 Processing {len(chunks)} chunks")
        
        return await self.ai_horde.generate_images_from_chunks(chunks, project_id)

# Factory function for easy instantiation
def create_image_generator(api_key: Optional[str] = None) -> AIHordeImageGenerator:
    """
    Create an image generator instance
    
    Args:
        api_key: AI Horde API key
        
    Returns:
        AIHordeImageGenerator instance
    """
    return AIHordeImageGenerator(api_key)