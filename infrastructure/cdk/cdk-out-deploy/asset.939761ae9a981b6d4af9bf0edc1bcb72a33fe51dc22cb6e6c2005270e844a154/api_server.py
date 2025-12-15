#!/usr/bin/env python3
"""
FIBO Video Director API Server

FastAPI backend for the FIBO video generation frontend.
Provides endpoints for script processing, checkpoint management, and FIBO generation.
"""

import os
import json
import uuid
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from fibo_video_director import FIBOVideoDirector

# Try to import enhanced director (falls back to standard if unavailable)
try:
    from enhanced_fibo_director import EnhancedFIBODirector
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Initialize FastAPI app
app = FastAPI(title="FIBO Video Director API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global director instance
director = None
enhanced_director = None
use_enhanced = False  # Toggle for enhanced multi-agent system
cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)

# Request/Response Models
class ScriptRequest(BaseModel):
    script_text: str

class VideoPlanResponse(BaseModel):
    project_id: str
    project_title: str
    total_duration_sec: int
    visual_style: Dict
    checkpoints: List[Dict]

class GenerateFramesRequest(BaseModel):
    project_id: str
    checkpoint_id: int

class GenerationStatus(BaseModel):
    status: str  # "pending", "generating", "completed", "error"
    progress: float
    message: str
    start_frame_url: Optional[str] = None
    end_frame_url: Optional[str] = None
    start_frame_cached: Optional[bool] = None
    end_frame_cached: Optional[bool] = None
    generation_time_sec: Optional[float] = None

# In-memory storage for projects and generation status
projects_cache = {}
generation_status = {}

@app.on_event("startup")
async def startup_event():
    """Initialize the FIBO director on startup."""
    global director, enhanced_director, use_enhanced
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY environment variable not set")
    
    # Check FAL_KEY
    fal_key = os.environ.get("FAL_KEY")
    if fal_key:
        print(f"✅ FAL_KEY configured ({fal_key[:10]}...)")
    else:
        print("⚠️ FAL_KEY not set - image generation will fail!")
    
    # Initialize standard director
    director = FIBOVideoDirector(api_key)
    
    # Initialize enhanced director if available
    if ENHANCED_AVAILABLE:
        try:
            enhanced_director = EnhancedFIBODirector(api_key)
            use_enhanced = os.environ.get("USE_ENHANCED_DIRECTOR", "false").lower() == "true"
            print(f"✅ Enhanced FIBO Director available (enabled: {use_enhanced})")
        except Exception as e:
            print(f"⚠️ Enhanced director init failed: {e}")
    
    print("✅ FIBO Video Director API Server started")

@app.get("/")
async def root():
    """Health check endpoint."""
    fal_configured = bool(os.environ.get("FAL_KEY"))
    return {
        "message": "FIBO Video Director API",
        "status": "running",
        "enhanced_available": ENHANCED_AVAILABLE,
        "enhanced_enabled": use_enhanced,
        "fal_configured": fal_configured
    }


@app.get("/api/director-mode")
async def get_director_mode():
    """Get current director mode status."""
    return {
        "enhanced_available": ENHANCED_AVAILABLE,
        "enhanced_enabled": use_enhanced,
        "mode": "enhanced" if use_enhanced else "standard"
    }


@app.post("/api/director-mode")
async def set_director_mode(enable_enhanced: bool = False):
    """Toggle between standard and enhanced director modes."""
    global use_enhanced
    
    if enable_enhanced and not ENHANCED_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Enhanced director not available"
        )
    
    use_enhanced = enable_enhanced
    return {
        "enhanced_enabled": use_enhanced,
        "mode": "enhanced" if use_enhanced else "standard"
    }

@app.post("/api/generate-plan", response_model=VideoPlanResponse)
async def generate_plan(request: ScriptRequest):
    """Generate a video plan from a movie script."""
    try:
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Use enhanced director if enabled, otherwise standard
        if use_enhanced and enhanced_director:
            video_plan = enhanced_director.process_script(request.script_text)
        else:
            video_plan = director.create_video_plan(request.script_text)
        
        if not video_plan:
            raise HTTPException(status_code=500, detail="Failed to generate video plan")
        
        # Cache the project
        projects_cache[project_id] = {
            "video_plan": video_plan,
            "created_at": datetime.now().isoformat(),
            "script_text": request.script_text
        }
        
        # Save to file for persistence
        project_file = cache_dir / f"project_{project_id}.json"
        with open(project_file, "w") as f:
            json.dump(projects_cache[project_id], f, indent=2)
        
        return VideoPlanResponse(
            project_id=project_id,
            project_title=video_plan.get("project_title", "Untitled Project"),
            total_duration_sec=video_plan.get("total_duration_sec", 0),
            visual_style=video_plan.get("visual_style", {}),
            checkpoints=video_plan.get("checkpoints", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get project details by ID."""
    if project_id not in projects_cache:
        # Try to load from file
        project_file = cache_dir / f"project_{project_id}.json"
        if project_file.exists():
            with open(project_file, "r") as f:
                projects_cache[project_id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_cache[project_id]
    video_plan = project["video_plan"]
    
    return VideoPlanResponse(
        project_id=project_id,
        project_title=video_plan.get("project_title", "Untitled Project"),
        total_duration_sec=video_plan.get("total_duration_sec", 0),
        visual_style=video_plan.get("visual_style", {}),
        checkpoints=video_plan.get("checkpoints", [])
    )

@app.get("/api/checkpoint/{project_id}/{checkpoint_id}")
async def get_checkpoint_prompts(project_id: str, checkpoint_id: int):
    """Get FIBO structured prompts for a specific checkpoint."""
    if project_id not in projects_cache:
        raise HTTPException(status_code=404, detail="Project not found")
    
    video_plan = projects_cache[project_id]["video_plan"]
    
    # Use appropriate director for export
    if use_enhanced and enhanced_director:
        checkpoint_data = enhanced_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
    else:
        checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
    
    if "error" in checkpoint_data:
        raise HTTPException(status_code=404, detail=checkpoint_data["error"])
    
    return checkpoint_data

@app.post("/api/generate-frames")
async def generate_frames(request: GenerateFramesRequest, background_tasks: BackgroundTasks):
    """Generate FIBO frames for a checkpoint."""
    generation_id = f"{request.project_id}_{request.checkpoint_id}"
    
    # Initialize generation status
    generation_status[generation_id] = GenerationStatus(
        status="pending",
        progress=0.0,
        message="Initializing frame generation..."
    )
    
    # Start background generation
    background_tasks.add_task(
        generate_frames_background,
        request.project_id,
        request.checkpoint_id,
        generation_id
    )
    
    return {"generation_id": generation_id, "status": "started"}

async def generate_frames_background(project_id: str, checkpoint_id: int, generation_id: str):
    """Background task for generating FIBO frames using FAL.ai API."""
    try:
        # Update status
        generation_status[generation_id].status = "generating"
        generation_status[generation_id].progress = 0.1
        generation_status[generation_id].message = "Getting checkpoint data..."
        print(f"\n🎬 Starting frame generation for checkpoint {checkpoint_id}")
        
        # Get checkpoint data
        if project_id not in projects_cache:
            raise Exception("Project not found")
        
        video_plan = projects_cache[project_id]["video_plan"]
        
        # Use appropriate director for export
        if use_enhanced and enhanced_director:
            checkpoint_data = enhanced_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
        else:
            checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
        
        if "error" in checkpoint_data:
            raise Exception(checkpoint_data["error"])
        
        print(f"   ✅ Checkpoint data retrieved")
        print(f"   Start frame description: {checkpoint_data['fibo_start_frame'].get('short_description', 'N/A')[:100]}...")
        
        # Update progress
        generation_status[generation_id].progress = 0.2
        generation_status[generation_id].message = "Initializing FAL FIBO API..."
        
        # Try FAL integration
        try:
            from fal_fibo_integration import get_fal_integration
            fal = get_fal_integration()
            print(f"   ✅ FAL integration initialized")
            
            # Update progress
            generation_status[generation_id].progress = 0.3
            generation_status[generation_id].message = "Generating start frame with FAL FIBO..."
            
            # Generate both frames using FAL
            generated_files = await fal.generate_checkpoint_frames(
                checkpoint_data["fibo_start_frame"],
                checkpoint_data["fibo_end_frame"],
                checkpoint_id,
                project_id,
                seed=checkpoint_id * 42 + 1000  # Deterministic seed based on checkpoint
            )
            
            # Update progress
            generation_status[generation_id].progress = 0.9
            generation_status[generation_id].message = "Saving generated files..."
            
            # Copy generated files to cache directory for serving
            import shutil
            
            # Copy start frame files
            start_image_cache = cache_dir / f"start_frame_{generation_id}.png"
            start_json_cache = cache_dir / f"start_frame_{generation_id}.json"
            
            has_start_image = False
            if generated_files.get("start_frame_image"):
                shutil.copy2(generated_files["start_frame_image"], start_image_cache)
                has_start_image = True
                print(f"   ✅ Start frame image copied to cache")
            shutil.copy2(generated_files["start_frame_json"], start_json_cache)
            
            # Copy end frame files
            end_image_cache = cache_dir / f"end_frame_{generation_id}.png"
            end_json_cache = cache_dir / f"end_frame_{generation_id}.json"
            
            has_end_image = False
            if generated_files.get("end_frame_image"):
                shutil.copy2(generated_files["end_frame_image"], end_image_cache)
                has_end_image = True
                print(f"   ✅ End frame image copied to cache")
            shutil.copy2(generated_files["end_frame_json"], end_json_cache)
            
            # Update final status with URLs
            generation_status[generation_id].status = "completed"
            generation_status[generation_id].progress = 1.0
            
            # Add timing and cache info
            gen_times = generated_files.get("generation_times", {})
            total_time = sum(gen_times.values()) if gen_times else 0
            generation_status[generation_id].generation_time_sec = total_time
            generation_status[generation_id].start_frame_cached = generated_files.get("start_frame_cached", False)
            generation_status[generation_id].end_frame_cached = generated_files.get("end_frame_cached", False)
            
            # Determine success message with timing
            cache_info = []
            if generated_files.get("start_frame_cached"):
                cache_info.append("start: cached")
            if generated_files.get("end_frame_cached"):
                cache_info.append("end: cached")
            
            if has_start_image and has_end_image:
                cache_str = f" ({', '.join(cache_info)})" if cache_info else ""
                generation_status[generation_id].message = f"✅ Both frames ready in {total_time:.1f}s{cache_str}"
            elif has_start_image or has_end_image:
                generation_status[generation_id].message = f"⚠️ Partial success in {total_time:.1f}s"
            else:
                generation_status[generation_id].message = "⚠️ JSON prompts ready (image generation failed)"
            
            # Set URLs - prefer S3/FAL URLs, fallback to local
            if generated_files.get("start_frame_url"):
                generation_status[generation_id].start_frame_url = generated_files["start_frame_url"]
            elif has_start_image:
                generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.png"
            else:
                generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.json"
            
            if generated_files.get("end_frame_url"):
                generation_status[generation_id].end_frame_url = generated_files["end_frame_url"]
            elif has_end_image:
                generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.png"
            else:
                generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.json"
            
            print(f"   🎉 Generation complete in {total_time:.1f}s!")
            print(f"   Start URL: {generation_status[generation_id].start_frame_url[:80]}...")
            print(f"   End URL: {generation_status[generation_id].end_frame_url[:80]}...")
            
        except Exception as fal_error:
            # If FAL generation fails, fall back to JSON-only mode
            print(f"   ❌ FAL FIBO generation failed: {fal_error}")
            import traceback
            traceback.print_exc()
            
            generation_status[generation_id].progress = 0.8
            generation_status[generation_id].message = "FAL API failed, saving structured prompts..."
            
            # Save structured prompts as fallback
            start_frame_file = cache_dir / f"start_frame_{generation_id}.json"
            end_frame_file = cache_dir / f"end_frame_{generation_id}.json"
            
            with open(start_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_start_frame"], f, indent=2)
            
            with open(end_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_end_frame"], f, indent=2)
            
            # Update status with fallback completion
            generation_status[generation_id].status = "completed"
            generation_status[generation_id].progress = 1.0
            generation_status[generation_id].message = f"JSON prompts ready (FAL error: {str(fal_error)[:100]})"
            generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.json"
            generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.json"
        
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        generation_status[generation_id].status = "error"
        generation_status[generation_id].message = f"Error: {str(e)}"

@app.get("/api/generation-status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get the status of frame generation."""
    if generation_id not in generation_status:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation_status[generation_id]

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated files."""
    file_path = cache_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    if filename.endswith('.png'):
        media_type = "image/png"
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        media_type = "image/jpeg"
    elif filename.endswith('.json'):
        media_type = "application/json"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.get("/api/fibo-status")
async def get_fibo_status():
    """Get FIBO installation and configuration status."""
    try:
        from fibo_integration import get_fibo_integration
        
        fibo = get_fibo_integration()
        status = fibo.check_fibo_status()
        models = fibo.get_available_models()
        
        return {
            "status": status,
            "available_models": models,
            "integration_ready": all([
                status.get("generate_script", False),
                status.get("src_directory", False),
                status.get("output_writable", False),
                status.get("google_api_key", False)
            ])
        }
        
    except Exception as e:
        return {
            "status": {"error": str(e)},
            "available_models": {},
            "integration_ready": False
        }


@app.get("/api/cache-stats")
async def get_cache_stats():
    """Get frame cache statistics."""
    try:
        from s3_storage import get_s3_storage
        storage = get_s3_storage()
        return storage.get_cache_stats()
    except ImportError:
        return {"error": "S3 storage not available", "s3_available": False}
    except Exception as e:
        return {"error": str(e), "s3_available": False}

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )