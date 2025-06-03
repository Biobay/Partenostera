from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import json
import uuid
from typing import List, Optional
from datetime import datetime

from .services.tool_service import ToolService
from .services.veo_service import VeoService
from .core.validator import Validator
from .utils.file_handler import FileHandler
from .utils.config import Config

# Initialize configuration
config = Config()

app = FastAPI(
    title="Media Generator MVP", 
    version="1.0.0",
    description="Generazione automatica di immagini, audio e video da testo"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("data/outputs", exist_ok=True)
app.mount("/static", StaticFiles(directory="data/outputs"), name="static")

# Initialize services
tool_service = ToolService()
veo_service = VeoService()
validator = Validator()
file_handler = FileHandler()

# Store for active generations
active_generations = {}

@app.get("/")
async def root():
    return {
        "message": "Media Generator MVP API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/books")
async def get_books():
    """Get available books from catalog"""
    try:
        books = file_handler.get_available_books()
        return {"success": True, "books": books}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/generate")
async def generate_media(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    book_id: Optional[str] = Form(None),
    user_mode: str = Form(...),
    custom_text: Optional[str] = Form(None)
):
    """Generate media content from text input"""
    try:
        # Validate input
        if not any([file, book_id, custom_text]):
            raise HTTPException(status_code=400, detail="Nessun input fornito")
        
        if user_mode not in ["tool", "veo"]:
            raise HTTPException(status_code=400, detail="Modalità utente non valida")
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Store initial status
        active_generations[project_id] = {
            "status": "initializing",
            "progress": 0,
            "created_at": datetime.now().isoformat()
        }
        
        # Get text content
        if file:
            content = await file_handler.process_uploaded_file(file)
        elif book_id:
            content = file_handler.get_book_content(book_id)
        else:
            content = custom_text
        
        # Start generation in background
        if user_mode == "tool":
            background_tasks.add_task(
                tool_service.generate_media_async, 
                content, 
                project_id, 
                active_generations
            )
        else:
            background_tasks.add_task(
                veo_service.generate_media_async, 
                content, 
                project_id, 
                active_generations
            )
        
        return {
            "success": True,
            "project_id": project_id,
            "message": "Generazione avviata"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/generation/status/{project_id}")
async def get_generation_status(project_id: str):
    """Get generation status"""
    if project_id not in active_generations:
        raise HTTPException(status_code=404, detail="Progetto non trovato")
    
    return active_generations[project_id]

@app.get("/projects")
async def get_projects():
    """Get all generated projects"""
    try:
        projects = file_handler.get_all_projects()
        return {"success": True, "projects": projects}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/project/{project_id}")
async def get_project(project_id: str):
    """Get specific project details"""
    try:
        project = file_handler.get_project_details(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Progetto non trovato")
        return {"success": True, "project": project}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/project/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    try:
        success = file_handler.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Progetto non trovato")
        
        # Remove from active generations if present
        if project_id in active_generations:
            del active_generations[project_id]
            
        return {"success": True, "message": "Progetto eliminato"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/config")
async def get_config():
    """Get system configuration"""
    return {
        "max_file_size": config.get("generation.max_file_size"),
        "supported_formats": config.get("generation.supported_formats"),
        "max_sequences": config.get("generation.max_sequences")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=config.get("server.host", "0.0.0.0"), 
        port=config.get("server.port", 8000),
        reload=config.get("server.debug", True)
    )
