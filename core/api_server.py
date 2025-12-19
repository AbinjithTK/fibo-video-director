#!/usr/bin/env python3
"""
FIBO Video Director API Server - Local Development
Enhanced version with Strands multi-agent system
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import uvicorn
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (look in parent directory)
parent_dir = Path(__file__).parent.parent
env_file = parent_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)

# Import the working FIBO directors
from fibo_video_director import FIBOVideoDirector

# Try to import enhanced director with Strands
try:
    from enhanced_fibo_director import EnhancedFIBODirector
    ENHANCED_AVAILABLE = True
    print("✅ Enhanced FIBO Director with Strands available")
except ImportError as e:
    ENHANCED_AVAILABLE = False
    print(f"⚠️ Enhanced FIBO Director not available: {e}")

# Try to import FAL integration
try:
    from fal_fibo_integration import get_fal_integration
    FAL_AVAILABLE = True
    print("✅ FAL FIBO integration available")
except ImportError as e:
    FAL_AVAILABLE = False
    print(f"⚠️ FAL integration not available: {e}")

app = FastAPI(title="FIBO Video Director API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
fibo_director = None
enhanced_director = None
projects_cache = {}
generation_status = {}
use_enhanced = True  # Enhanced director enabled by default
cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)

class ScriptRequest(BaseModel):
    script_text: str

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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global fibo_director, enhanced_director, use_enhanced
    
    print("🚀 Starting FIBO Video Director API Server...")
    
    # Get API keys
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    fal_key = os.environ.get("FAL_KEY")
    
    if not google_api_key:
        print("⚠️ GOOGLE_API_KEY not set - using fallback mode")
        use_enhanced = False
    
    if fal_key:
        print(f"✅ FAL_KEY configured ({fal_key[:10]}...)")
    else:
        print("⚠️ FAL_KEY not set - image generation will be limited")
    
    # Initialize Enhanced FIBO Director with Strands if available
    if ENHANCED_AVAILABLE:
        try:
            enhanced_director = EnhancedFIBODirector(google_api_key)
            use_enhanced = True
            print("✅ Enhanced FIBO Director with Multi-Agent Swarm initialized")
            print("🤖 Multi-Agent System: Script Analyst + Visual Director + FIBO Specialist")
        except Exception as e:
            print(f"⚠️ Failed to initialize Enhanced Director: {e}")
            use_enhanced = False
    else:
        use_enhanced = False
    
    # Initialize standard FIBO Video Director as fallback
    try:
        fibo_director = FIBOVideoDirector(google_api_key)
        print("✅ Standard FIBO Video Director initialized")
    except Exception as e:
        print(f"❌ Failed to initialize FIBO Director: {e}")
        fibo_director = None

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "FIBO Video Director API - Local Development",
        "status": "running",
        "enhanced_available": ENHANCED_AVAILABLE,
        "enhanced_enabled": use_enhanced,
        "fal_available": FAL_AVAILABLE,
        "fibo_available": fibo_director is not None,
        "google_api_configured": bool(os.environ.get("GOOGLE_API_KEY")),
        "fal_configured": bool(os.environ.get("FAL_KEY")),
        "active_mode": "enhanced" if use_enhanced and enhanced_director else "standard",
        "version": "2.0.0-local"
    }

@app.get("/api/director-mode")
async def get_director_mode():
    """Get current director mode."""
    return {
        "enhanced_available": ENHANCED_AVAILABLE,
        "enhanced_enabled": use_enhanced,
        "fal_available": FAL_AVAILABLE,
        "mode": "enhanced" if use_enhanced and enhanced_director else "standard"
    }

@app.post("/api/director-mode")
async def set_director_mode(enable_enhanced: bool = True):
    """Toggle between director modes."""
    global use_enhanced
    
    if enable_enhanced and not ENHANCED_AVAILABLE:
        raise HTTPException(
            status_code=400,
            detail="Enhanced director not available"
        )
    
    use_enhanced = enable_enhanced
    
    return {
        "enhanced_enabled": use_enhanced,
        "mode": "enhanced" if use_enhanced and enhanced_director else "standard"
    }

@app.post("/api/generate-plan")
async def generate_plan(request: ScriptRequest):
    """Generate video production plan from script."""
    try:
        if not request.script_text.strip():
            raise HTTPException(status_code=400, detail="Script text is required")
        
        print(f"📝 Processing script: {request.script_text[:100]}...")
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Use Enhanced Director with Strands if available and enabled
        if use_enhanced and enhanced_director:
            print("🧠 Using Enhanced FIBO Director with Strands multi-agent system")
            video_plan = enhanced_director.process_script(request.script_text)
        elif fibo_director:
            print("🤖 Using Standard FIBO Video Director with Gemini")
            video_plan = fibo_director.create_video_plan(request.script_text)
        else:
            print("📝 Using intelligent fallback")
            video_plan = create_intelligent_fallback_plan(request.script_text)
        
        # Cache the project
        projects_cache[project_id] = {
            'video_plan': video_plan,
            'created_at': datetime.now().isoformat(),
            'script_text': request.script_text
        }
        
        # Save to file for persistence
        project_file = cache_dir / f"project_{project_id}.json"
        with open(project_file, "w") as f:
            json.dump(projects_cache[project_id], f, indent=2)
        
        print(f"✅ Created project {project_id}: {video_plan['project_title']}")
        
        return {
            'project_id': project_id,
            'project_title': video_plan.get('project_title', 'FIBO Video Production'),
            'total_duration_sec': video_plan.get('total_duration_sec', 16),
            'checkpoints': video_plan.get('checkpoints', []),
            'visual_style': video_plan.get('visual_style', {}),
            'metadata': video_plan.get('metadata', {})
        }
        
    except Exception as e:
        print(f"❌ Error generating plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process script: {str(e)}")

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    if project_id not in projects_cache:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_cache[project_id]
    video_plan = project['video_plan']
    
    return {
        'project_id': project_id,
        'project_title': video_plan.get('project_title', 'FIBO Video Production'),
        'total_duration_sec': video_plan.get('total_duration_sec', 16),
        'checkpoints': video_plan.get('checkpoints', []),
        'visual_style': video_plan.get('visual_style', {}),
        'created_at': project['created_at']
    }

@app.get("/api/checkpoint/{project_id}/{checkpoint_id}")
async def get_checkpoint(project_id: str, checkpoint_id: int):
    """Get checkpoint details."""
    if project_id not in projects_cache:
        # Try to load from file
        project_file = cache_dir / f"project_{project_id}.json"
        if project_file.exists():
            with open(project_file, "r") as f:
                projects_cache[project_id] = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Project not found")
    
    video_plan = projects_cache[project_id]['video_plan']
    
    # Use appropriate director's export method
    if use_enhanced and enhanced_director:
        checkpoint_data = enhanced_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
    elif fibo_director:
        checkpoint_data = fibo_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
    else:
        # Fallback to direct lookup
        for checkpoint in video_plan.get('checkpoints', []):
            if checkpoint['checkpoint_id'] == checkpoint_id:
                return {
                    'checkpoint_id': checkpoint_id,
                    'scene_description': checkpoint.get('scene_description', ''),
                    'duration_sec': checkpoint.get('duration_sec', 8),
                    'visual_style': video_plan.get('visual_style', {}),
                    'fibo_start_frame': checkpoint.get('fibo_start_frame', {}),
                    'fibo_end_frame': checkpoint.get('fibo_end_frame', {}),
                    'video_generation_notes': checkpoint.get('video_generation_notes', '')
                }
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    if "error" in checkpoint_data:
        raise HTTPException(status_code=404, detail=checkpoint_data["error"])
    
    return checkpoint_data

@app.post("/api/generate-frames")
async def generate_frames(request: GenerateFramesRequest, background_tasks: BackgroundTasks):
    """Generate frames for a checkpoint."""
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
    """Background task for generating FIBO frames."""
    try:
        # Update status
        generation_status[generation_id].status = "generating"
        generation_status[generation_id].progress = 0.1
        generation_status[generation_id].message = "Getting checkpoint data..."
        print(f"\n🎬 Starting frame generation for checkpoint {checkpoint_id}")
        
        # Get checkpoint data
        if project_id not in projects_cache:
            # Try to load from file
            project_file = cache_dir / f"project_{project_id}.json"
            if project_file.exists():
                with open(project_file, "r") as f:
                    projects_cache[project_id] = json.load(f)
            else:
                raise Exception("Project not found")
        
        video_plan = projects_cache[project_id]["video_plan"]
        
        # Use appropriate director for export
        if use_enhanced and enhanced_director:
            checkpoint_data = enhanced_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
        elif fibo_director:
            checkpoint_data = fibo_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
        else:
            raise Exception("No director available")
        
        if "error" in checkpoint_data:
            raise Exception(checkpoint_data["error"])
        
        print(f"   ✅ Checkpoint data retrieved")
        
        # Update progress
        generation_status[generation_id].progress = 0.3
        generation_status[generation_id].message = "Generating FIBO frames..."
        
        # Try FAL integration if available
        if FAL_AVAILABLE:
            try:
                fal = get_fal_integration()
                print(f"   ✅ FAL integration initialized")
                
                # Generate both frames using FAL
                generated_files = await fal.generate_checkpoint_frames(
                    checkpoint_data["fibo_start_frame"],
                    checkpoint_data["fibo_end_frame"],
                    checkpoint_id,
                    project_id,
                    seed=checkpoint_id * 42 + 1000
                )
                
                # Update progress
                generation_status[generation_id].progress = 0.9
                generation_status[generation_id].message = "Saving generated files..."
                
                # Save JSON prompts locally for backup
                import shutil
                start_json_cache = cache_dir / f"start_frame_{generation_id}.json"
                end_json_cache = cache_dir / f"end_frame_{generation_id}.json"
                
                shutil.copy2(generated_files["start_frame_json"], start_json_cache)
                shutil.copy2(generated_files["end_frame_json"], end_json_cache)
                
                # Update final status
                generation_status[generation_id].status = "completed"
                generation_status[generation_id].progress = 1.0
                
                gen_times = generated_files.get("generation_times", {})
                total_time = sum(gen_times.values()) if gen_times else 0
                generation_status[generation_id].generation_time_sec = total_time
                generation_status[generation_id].start_frame_cached = generated_files.get("start_frame_cached", False)
                generation_status[generation_id].end_frame_cached = generated_files.get("end_frame_cached", False)
                
                # Check if we have actual image URLs from FAL
                start_image_url = generated_files.get("start_frame_url")
                end_image_url = generated_files.get("end_frame_url")
                
                has_start_image = bool(start_image_url and (start_image_url.startswith('http') or generated_files.get("start_frame_image")))
                has_end_image = bool(end_image_url and (end_image_url.startswith('http') or generated_files.get("end_frame_image")))
                
                if has_start_image and has_end_image:
                    generation_status[generation_id].message = f"✅ Both frames ready in {total_time:.1f}s"
                elif has_start_image or has_end_image:
                    generation_status[generation_id].message = f"⚠️ One frame ready in {total_time:.1f}s"
                else:
                    generation_status[generation_id].message = "⚠️ JSON prompts ready (image generation failed)"
                
                # Set URLs - prefer FAL URLs, fallback to local files
                if start_image_url and start_image_url.startswith('http'):
                    generation_status[generation_id].start_frame_url = start_image_url
                elif generated_files.get("start_frame_image"):
                    # Copy local image to cache and serve it
                    start_image_cache = cache_dir / f"start_frame_{generation_id}.png"
                    shutil.copy2(generated_files["start_frame_image"], start_image_cache)
                    generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.png"
                else:
                    generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.json"
                
                if end_image_url and end_image_url.startswith('http'):
                    generation_status[generation_id].end_frame_url = end_image_url
                elif generated_files.get("end_frame_image"):
                    # Copy local image to cache and serve it
                    end_image_cache = cache_dir / f"end_frame_{generation_id}.png"
                    shutil.copy2(generated_files["end_frame_image"], end_image_cache)
                    generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.png"
                else:
                    generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.json"
                
                print(f"   🎉 Generation complete in {total_time:.1f}s!")
                
            except Exception as fal_error:
                print(f"   ❌ FAL generation failed: {fal_error}")
                raise fal_error
        else:
            # Fallback: Save structured prompts only
            print("   📝 FAL not available, saving structured prompts only")
            
            start_frame_file = cache_dir / f"start_frame_{generation_id}.json"
            end_frame_file = cache_dir / f"end_frame_{generation_id}.json"
            
            with open(start_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_start_frame"], f, indent=2)
            
            with open(end_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_end_frame"], f, indent=2)
            
            generation_status[generation_id].status = "completed"
            generation_status[generation_id].progress = 1.0
            generation_status[generation_id].message = "✅ FIBO structured prompts ready"
            generation_status[generation_id].start_frame_url = f"/api/download/start_frame_{generation_id}.json"
            generation_status[generation_id].end_frame_url = f"/api/download/end_frame_{generation_id}.json"
            generation_status[generation_id].generation_time_sec = 2.0
        
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        generation_status[generation_id].status = "error"
        generation_status[generation_id].message = f"Error: {str(e)}"

@app.get("/api/generation-status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get generation status."""
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

@app.get("/api/proxy-image")
async def proxy_image(url: str):
    """Proxy external image URLs to avoid CORS issues."""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            # Determine content type
            content_type = response.headers.get("content-type", "image/png")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                    "Access-Control-Allow-Origin": "*"
                }
            )
    except Exception as e:
        print(f"❌ Proxy error for {url}: {e}")
        raise HTTPException(status_code=404, detail=f"Failed to proxy image: {str(e)}")

@app.get("/api/cache-stats")
async def get_cache_stats():
    """Get cache statistics."""
    try:
        # Try to get S3 cache stats if available
        from s3_storage import get_s3_storage
        storage = get_s3_storage()
        return storage.get_cache_stats()
    except ImportError:
        # Fallback to local cache stats
        return {
            'projects_cached': len(projects_cache),
            'generations_tracked': len(generation_status),
            'cache_type': 'local',
            's3_available': False
        }
    except Exception as e:
        return {
            'projects_cached': len(projects_cache),
            'generations_tracked': len(generation_status),
            'cache_type': 'local',
            'error': str(e),
            's3_available': False
        }

def create_intelligent_fallback_plan(script_text: str) -> Dict[str, Any]:
    """Create intelligent fallback plan when FIBO director is not available."""
    
    # Analyze script content
    script_lower = script_text.lower()
    
    # Determine project title based on content
    if any(word in script_lower for word in ['forest', 'tree', 'nature', 'woods', 'magical']):
        title = "Enchanted Forest Adventure"
        environment = "Mystical forest with ancient trees and magical atmosphere"
        lighting = "Dappled sunlight filtering through magical forest canopy"
    elif any(word in script_lower for word in ['city', 'street', 'urban', 'building']):
        title = "Urban Chronicles"
        environment = "Modern cityscape with urban architecture"
        lighting = "Urban lighting with neon and street lights"
    elif any(word in script_lower for word in ['mountain', 'peak', 'summit', 'climb']):
        title = "Mountain Peak Journey"
        environment = "Majestic mountain landscape with panoramic views"
        lighting = "Golden hour mountain lighting with dramatic shadows"
    elif any(word in script_lower for word in ['wizard', 'magic', 'spell', 'mystical', 'staff']):
        title = "Mystical Realms"
        environment = "Magical realm with mystical energy and enchanted elements"
        lighting = "Magical lighting with glowing mystical energy"
    else:
        title = "Cinematic Vision"
        environment = "Professional cinematic environment"
        lighting = "Cinematic three-point lighting"
    
    return {
        'project_title': title,
        'production_id': f"local_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'created_at': datetime.now().isoformat(),
        'total_duration_sec': 16,
        'visual_style': {
            'lighting_style': lighting,
            'color_palette': 'Natural, cinematic color grading with rich tones',
            'camera_style': 'Professional 50mm lens, f/2.8 aperture, cinematic depth',
            'environment_theme': environment,
            'artistic_direction': 'Photorealistic, high production value, cinematic quality'
        },
        'checkpoints': [
            {
                'checkpoint_id': 1,
                'start_time_sec': 0,
                'end_time_sec': 8,
                'duration_sec': 8,
                'scene_description': f"Opening scene: {script_text[:200]}",
                'is_continuation': False,
                'visual_consistency_notes': 'Establishes the visual style and cinematic tone',
                'fibo_start_frame': create_intelligent_fibo_prompt('start', environment, lighting),
                'fibo_end_frame': create_intelligent_fibo_prompt('transition', environment, lighting),
                'video_generation_notes': 'Smooth cinematic introduction with establishing shots'
            },
            {
                'checkpoint_id': 2,
                'start_time_sec': 8,
                'end_time_sec': 16,
                'duration_sec': 8,
                'scene_description': f"Concluding scene: {script_text[len(script_text)//2:len(script_text)//2+200]}",
                'is_continuation': True,
                'visual_consistency_notes': 'Maintains visual continuity while building to climax',
                'fibo_start_frame': create_intelligent_fibo_prompt('continuation', environment, lighting),
                'fibo_end_frame': create_intelligent_fibo_prompt('conclusion', environment, lighting),
                'video_generation_notes': 'Dramatic conclusion with impactful visual storytelling'
            }
        ],
        'metadata': {
            'agent_system': 'Intelligent Fallback Director',
            'model': 'local-analysis',
            'version': '1.0.0-local'
        }
    }

def create_intelligent_fibo_prompt(frame_type: str, environment: str, lighting: str) -> Dict[str, Any]:
    """Create intelligent FIBO structured prompt."""
    return {
        'short_description': f'{frame_type.title()} frame with cinematic composition',
        'objects': [
            {
                'description': 'Main character from scene analysis',
                'location': 'Center frame using rule of thirds composition',
                'relationship': 'Primary subject and focal point of the scene',
                'relative_size': 'Prominent figure occupying 1/3 of frame height',
                'shape_and_color': 'Natural, realistic human proportions with authentic coloring',
                'texture': 'Photorealistic skin and fabric textures with fine detail',
                'appearance_details': 'High-resolution facial features, detailed clothing, realistic materials',
                'pose': 'Natural, contextually appropriate positioning',
                'expression': 'Emotionally appropriate to scene context',
                'orientation': 'Facing camera or in contextually appropriate direction'
            }
        ],
        'background_setting': environment,
        'lighting': lighting,
        'aesthetics': {
            'composition': 'Cinematic rule of thirds with balanced visual weight',
            'color_scheme': 'Rich, saturated colors with natural harmony',
            'mood_atmosphere': 'Epic, cinematic atmosphere with emotional depth'
        },
        'photographic_characteristics': {
            'depth_of_field': 'Shallow depth of field with subject in sharp focus',
            'camera_angle': 'Eye-level perspective with slight heroic angle',
            'lens_focal_length': '50mm equivalent with natural perspective'
        },
        'style_medium': 'Photorealistic digital cinematography, high production value'
    }

if __name__ == "__main__":
    print("🎬 FIBO Video Director - Local Development Server")
    print("=" * 50)
    print("🌐 Starting server at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
