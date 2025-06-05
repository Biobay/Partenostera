"""
FastAPI Media Generator Application
Complete workflow: Text Analysis → Scene Extraction → Image Generation → Video Generation
"""

import os
import asyncio
import logging
import httpx
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Internal imports
from .models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProcessingProgress, BatchProcessingRequest, BatchProcessingResponse,
    ProjectStatus, ProcessingStep, Scene, ProjectSettings
)
from .core.text_analyzer import TextAnalyzer, create_text_analyzer
from .core.image_generator import AIHordeImageGenerator, create_image_generator
from .core.video_generator import VideoProcessor, create_video_processor
from .utils.config import get_config
from .utils.file_handler import FileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state for projects and processing
projects_db: Dict[str, Project] = {}
active_processing: Dict[str, bool] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Initialize components
config = get_config()
file_handler = FileHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Media Generator API")
    
    # Initialize directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/outputs", exist_ok=True)
    os.makedirs("data/outputs/images", exist_ok=True)
    os.makedirs("data/outputs/videos", exist_ok=True)
    
    yield
    
    logger.info("🛑 Shutting down Media Generator API")

# Create FastAPI app
app = FastAPI(
    title="Media Generator API",
    description="Complete workflow for generating media from text: Text → Scenes → Images → Videos",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for generated media
app.mount("/media", StaticFiles(directory="data/outputs"), name="media")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Project Management Endpoints

@app.post("/projects", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, background_tasks: BackgroundTasks):
    """Create a new project"""
    try:
        import uuid
        project_id = str(uuid.uuid4())
        
        # Create project
        project = Project(
            id=project_id,
            title=project_data.title,
            description=project_data.description,
            original_text=project_data.text_content,
            settings=project_data.settings or ProjectSettings(),
            output_directory=f"data/outputs/{project_id}",
            images_directory=f"data/outputs/{project_id}/images",
            videos_directory=f"data/outputs/{project_id}/videos"
        )
          # Create output directories
        if project.output_directory:
            os.makedirs(project.output_directory, exist_ok=True)
        if project.images_directory:
            os.makedirs(project.images_directory, exist_ok=True)
        if project.videos_directory:
            os.makedirs(project.videos_directory, exist_ok=True)
        
        # Store project
        projects_db[project_id] = project
        
        # Start processing in background if text provided
        if project_data.text_content:
            background_tasks.add_task(process_project_pipeline, project_id)
        
        logger.info(f"Created project {project_id}: {project.title}")
        
        return ProjectResponse(
            success=True,
            project=project,
            message="Project created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project by ID"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ProjectResponse(
        success=True,
        project=projects_db[project_id]
    )

@app.get("/projects", response_model=List[Project])
async def list_projects():
    """List all projects"""
    return list(projects_db.values())

@app.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, update_data: ProjectUpdate):
    """Update project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Update fields
    if update_data.title is not None:
        project.title = update_data.title
    if update_data.description is not None:
        project.description = update_data.description
    if update_data.status is not None:
        project.status = update_data.status
    if update_data.settings is not None:
        project.settings = update_data.settings
    
    project.updated_at = datetime.now()
    
    return ProjectResponse(
        success=True,
        project=project,
        message="Project updated successfully"
    )

@app.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Stop any active processing
    if project_id in active_processing:
        active_processing[project_id] = False
    
    # Remove project
    del projects_db[project_id]
    
    return {"success": True, "message": "Project deleted successfully"}

# File Upload Endpoints

@app.post("/projects/{project_id}/upload-text")
async def upload_text_file(
    project_id: str, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload text file for processing"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Update project
        project = projects_db[project_id]
        project.original_text = text_content
        project.word_count = len(text_content.split())
        project.text_file_path = f"data/uploads/{project_id}_{file.filename}"
        project.updated_at = datetime.now()
        
        # Save file
        file_path = project.text_file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
          # Start processing
        background_tasks.add_task(process_project_pipeline, project_id)
        
        return {
            "success": True,
            "message": "Text file uploaded successfully",
            "word_count": project.word_count
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Processing Endpoints

@app.post("/projects/{project_id}/start-processing")
async def start_processing(project_id: str, background_tasks: BackgroundTasks):
    """Start processing pipeline for project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    if not project.original_text:
        raise HTTPException(status_code=400, detail="No text content available for processing")
    
    if project_id in active_processing and active_processing[project_id]:
        raise HTTPException(status_code=400, detail="Project is already being processed")
    
    # Start processing
    background_tasks.add_task(process_project_pipeline, project_id)
    
    return {
        "success": True,
        "message": "Processing started",
        "project_id": project_id
    }

@app.post("/projects/{project_id}/stop-processing")
async def stop_processing(project_id: str):
    """Stop processing for project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project_id in active_processing:
        active_processing[project_id] = False
    
    return {
        "success": True,
        "message": "Processing stopped",
        "project_id": project_id
    }

@app.get("/projects/{project_id}/progress")
async def get_progress(project_id: str):
    """Get processing progress for project"""
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Calculate progress
    total_scenes = len(project.scenes)
    completed_scenes = sum(1 for scene in project.scenes if 
                          scene.image_generation_status == ProcessingStep.COMPLETED and 
                          scene.video_generation_status == ProcessingStep.COMPLETED)
    
    progress_percentage = (completed_scenes / total_scenes * 100) if total_scenes > 0 else 0
    
    return ProcessingProgress(
        project_id=project_id,
        current_step=project.status.value,
        progress_percentage=progress_percentage,
        scenes_analyzed=len(project.scenes),
        images_generated=project.stats.images_generated,
        videos_generated=project.stats.videos_generated,
        elapsed_time=project.stats.total_processing_time,
        is_complete=project.status == ProjectStatus.COMPLETED,
        has_errors=project.stats.failed_scenes > 0,
        error_count=project.stats.failed_scenes + project.stats.failed_images + project.stats.failed_videos
    )

# Batch Processing

@app.post("/batch/process", response_model=BatchProcessingResponse)
async def start_batch_processing(
    batch_request: BatchProcessingRequest,
    background_tasks: BackgroundTasks
):
    """Start batch processing of multiple projects"""
    import uuid
    batch_id = str(uuid.uuid4())
    
    # Validate projects exist
    for project_id in batch_request.project_ids:
        if project_id not in projects_db:
            raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    # Start batch processing
    background_tasks.add_task(
        process_batch_pipeline, 
        batch_id, 
        batch_request.project_ids,
        batch_request.max_concurrent,
        batch_request.skip_errors
    )
    
    return BatchProcessingResponse(
        success=True,
        batch_id=batch_id,
        projects_count=len(batch_request.project_ids),
        message="Batch processing started"
    )

# WebSocket for real-time updates

@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket endpoint for real-time project updates"""
    await websocket.accept()
    websocket_connections[project_id] = websocket
    
    try:
        while True:
            # Send progress updates
            if project_id in projects_db:
                progress = await get_progress(project_id)
                await websocket.send_json(progress.dict())
            
            await asyncio.sleep(2)  # Send updates every 2 seconds
            
    except WebSocketDisconnect:
        if project_id in websocket_connections:
            del websocket_connections[project_id]

# Text Analysis Endpoints

class TextAnalysisRequest(BaseModel):
    text: str

class TextAnalysisResponse(BaseModel):
    success: bool
    scenes: List[Scene]
    message: str = ""

@app.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text and extract scenes using text-chunker service"""
    try:
        logger.info(f"Starting text analysis for {len(request.text)} characters")
        
        # Call text-chunker service
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout
            response = await client.post(
                "http://localhost:8001/split-scenes",
                json={"text": request.text}
            )
            
            if response.status_code != 200:
                logger.error(f"Text-chunker service error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Text analysis service error: {response.status_code}"
                )
            
            chunker_result = response.json()
              # Convert scenes to our format
            scenes = []
            for i, scene_data in enumerate(chunker_result.get("scenes", [])):
                # Convert personaggi from string to array if needed
                personaggi = scene_data.get("personaggi", "")
                if isinstance(personaggi, str):
                    # Split by comma if it's a comma-separated string
                    personaggi_array = [p.strip() for p in personaggi.split(",") if p.strip()]
                else:
                    personaggi_array = personaggi if isinstance(personaggi, list) else [str(personaggi)]
                
                scene = Scene(
                    id=f"scene_{i+1}",
                    title=f"Scena {i+1}",
                    content=scene_data.get("elementi_narrativi", ""),
                    summary=scene_data.get("azione_in_corso", ""),
                    characters=personaggi_array,
                    setting=scene_data.get("ambientazione", ""),
                    mood=scene_data.get("mood_vibe", "")
                )
                scenes.append(scene)
            
            logger.info(f"Text analysis completed. Extracted {len(scenes)} scenes")
            
            return TextAnalysisResponse(
                success=True,
                scenes=scenes,
                message=f"Successfully extracted {len(scenes)} scenes"
            )
            
    except httpx.TimeoutException:
        logger.error("Text analysis timeout")
        raise HTTPException(status_code=504, detail="Text analysis service timeout")
    except httpx.RequestError as e:
        logger.error(f"Text analysis request error: {e}")
        raise HTTPException(status_code=503, detail="Text analysis service unavailable")
    except Exception as e:
        logger.error(f"Error in text analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Processing Pipeline Functions

async def process_project_pipeline(project_id: str):
    """Complete processing pipeline for a project"""
    if project_id not in projects_db:
        logger.error(f"Project {project_id} not found")
        return
    
    active_processing[project_id] = True
    project = projects_db[project_id]
    
    try:
        logger.info(f"🔄 Starting processing pipeline for project {project_id}")
        
        # Step 1: Text Analysis
        await process_text_analysis(project)
        
        # Step 2: Image Generation
        if active_processing.get(project_id, False):
            await process_image_generation(project)
        
        # Step 3: Video Generation
        if active_processing.get(project_id, False):
            await process_video_generation(project)
        
        # Mark as completed
        if active_processing.get(project_id, False):
            project.status = ProjectStatus.COMPLETED
            project.updated_at = datetime.now()
            logger.info(f"✅ Processing completed for project {project_id}")
        
    except Exception as e:
        logger.error(f"❌ Error processing project {project_id}: {e}")
        project.status = ProjectStatus.FAILED
        project.updated_at = datetime.now()
    
    finally:
        active_processing[project_id] = False
        
        # Send final update via WebSocket
        if project_id in websocket_connections:
            try:
                progress = await get_progress(project_id)
                await websocket_connections[project_id].send_json(progress.dict())
            except:
                pass

async def process_text_analysis(project: Project):
    """Process text analysis step"""
    logger.info(f"📚 Analyzing text for project {project.id}")
    project.status = ProjectStatus.TEXT_ANALYZING
    
    # Create text analyzer
    text_analyzer = create_text_analyzer()    # Check if text exists
    if not project.original_text:
        raise Exception("No text content available for analysis")
    
    # Analyze text
    text_chunks = await text_analyzer.analyze_text(project.original_text)
    
    # Convert TextChunks to project scenes
    project.scenes = []
    for i, chunk in enumerate(text_chunks):
        # Convert personaggi to list if it's a string
        characters = []
        if hasattr(chunk.scene, 'personaggi') and chunk.scene.personaggi:
            if isinstance(chunk.scene.personaggi, str):
                characters = [name.strip() for name in chunk.scene.personaggi.split(',') if name.strip()]
            elif isinstance(chunk.scene.personaggi, list):
                characters = chunk.scene.personaggi
        
        scene = Scene(
            id=f"{project.id}_scene_{i}",
            title=f"Scene {i+1}",
            content=chunk.content,
            summary=chunk.scene.azione_in_corso if hasattr(chunk.scene, 'azione_in_corso') else '',
            characters=characters,
            setting=chunk.scene.ambientazione if hasattr(chunk.scene, 'ambientazione') else None,
            mood=chunk.scene.mood_vibe if hasattr(chunk.scene, 'mood_vibe') else None,
            themes=[],  # themes not available in current Scene model
            image_prompt=chunk.image_prompt if hasattr(chunk, 'image_prompt') else ''
        )
        project.scenes.append(scene)
    
    project.status = ProjectStatus.TEXT_ANALYZED
    project.stats.total_scenes = len(project.scenes)
    logger.info(f"✅ Text analysis completed: {len(project.scenes)} scenes extracted")

async def process_image_generation(project: Project):
    """Process image generation step"""
    logger.info(f"🎨 Generating images for project {project.id}")
    project.status = ProjectStatus.IMAGES_GENERATING
    
    # Create image generator
    image_generator = create_image_generator()
    
    for scene in project.scenes:
        if not active_processing.get(project.id, False):
            break
            
        logger.info(f"Generating image for scene: {scene.title}")
        scene.image_generation_status = ProcessingStep.PROCESSING
        
        try:
            # Generate image
            prompt = scene.image_prompt or "cinematic scene"  # Default prompt if None
            image_result = await image_generator.generate_image(
                prompt=prompt,
                project_id=project.id,
                order=project.scenes.index(scene)
            )
            
            if image_result and image_result.get('local_path'):
                scene.image_url = image_result.get('url', '')
                scene.image_path = image_result.get('local_path', '')
                scene.image_generation_status = ProcessingStep.COMPLETED
                project.stats.images_generated += 1
                
            else:
                scene.image_error = 'Image generation failed'
                scene.image_generation_status = ProcessingStep.FAILED
                project.stats.failed_images += 1
                
        except Exception as e:
            scene.image_error = str(e)
            scene.image_generation_status = ProcessingStep.FAILED
            project.stats.failed_images += 1
            logger.error(f"Error generating image for scene {scene.id}: {e}")
    
    project.status = ProjectStatus.IMAGES_GENERATED
    logger.info(f"✅ Image generation completed: {project.stats.images_generated} images generated")

async def process_video_generation(project: Project):
    """Process video generation step"""
    logger.info(f"🎬 Generating videos for project {project.id}")
    project.status = ProjectStatus.VIDEOS_GENERATING
    
    # Create video processor
    video_processor = create_video_processor()
    
    for scene in project.scenes:
        if not active_processing.get(project.id, False):
            break
            
        # Skip if no image was generated
        if scene.image_generation_status != ProcessingStep.COMPLETED or not scene.image_path:
            continue
            
        logger.info(f"Generating video for scene: {scene.title}")
        scene.video_generation_status = ProcessingStep.PROCESSING
        
        try:
            # Prepare scene data for video processing
            scene_data = {
                'scene_id': scene.id,
                'image_path': scene.image_path,
                'prompt': scene.content[:200]  # Use first 200 chars as video prompt
            }
            
            # Generate video
            video_results = await video_processor.process_scene_images_to_videos(
                [scene_data],
                base_prompt=f"cinematic {project.settings.image_style} style"
            )
            
            if video_results and video_results[0]['video_generation']['success']:
                scene.video_url = video_results[0]['video_generation']['video_url']
                scene.video_path = f"{project.videos_directory}/{scene.id}.mp4"
                scene.video_generation_status = ProcessingStep.COMPLETED
                project.stats.videos_generated += 1
            else:
                error_msg = video_results[0]['video_generation'].get('error', 'Unknown error') if video_results else 'No results'
                scene.video_error = error_msg
                scene.video_generation_status = ProcessingStep.FAILED
                project.stats.failed_videos += 1
                
        except Exception as e:
            scene.video_error = str(e)
            scene.video_generation_status = ProcessingStep.FAILED
            project.stats.failed_videos += 1
            logger.error(f"Error generating video for scene {scene.id}: {e}")
    
    project.status = ProjectStatus.VIDEOS_GENERATED
    logger.info(f"✅ Video generation completed: {project.stats.videos_generated} videos generated")

async def process_batch_pipeline(
    batch_id: str, 
    project_ids: List[str], 
    max_concurrent: int, 
    skip_errors: bool
):
    """Process multiple projects in batch"""
    logger.info(f"🔄 Starting batch processing {batch_id} for {len(project_ids)} projects")
    
    # Process projects with concurrency limit
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single_project(project_id: str):
        async with semaphore:
            try:
                await process_project_pipeline(project_id)
                logger.info(f"✅ Batch: Completed project {project_id}")
            except Exception as e:
                logger.error(f"❌ Batch: Failed project {project_id}: {e}")
                if not skip_errors:
                    raise
    
    # Start all projects
    tasks = [process_single_project(pid) for pid in project_ids]
    
    if skip_errors:
        # Wait for all, don't fail on individual errors
        results = await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"✅ Batch processing {batch_id} completed with {sum(1 for r in results if not isinstance(r, Exception))} successes")
    else:
        # Fail fast on any error
        await asyncio.gather(*tasks)
        logger.info(f"✅ Batch processing {batch_id} completed successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)