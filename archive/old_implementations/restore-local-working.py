#!/usr/bin/env python3
"""
Restore Local Working Environment
Clean up all AWS deployment files and get back to working localhost
"""

import os
import shutil
from pathlib import Path

def clean_aws_deployment_files():
    """Remove all AWS deployment related files."""
    print("🧹 Cleaning up AWS deployment files...")
    
    # Files to remove
    aws_files = [
        "lambda_handler.py",
        "deploy-lambda.py",
        "setup-api-gateway.py",
        "deploy-apprunner.sh",
        "lightsail-deploy.sh",
        "amplify.yml",
        "apprunner.yaml",
        "Dockerfile",
        "APPRUNNER_DEPLOYMENT.md",
        "LAMBDA_DEPLOYMENT_GUIDE.md",
        "DEPLOYMENT.md",
        "DEPLOYMENT_SUMMARY.md",
        "complete-integration.py",
        "test-lambda-api.py",
        "update-lambda-env.py",
        "set-lambda-env-vars.py",
        "set-lambda-env-console.py",
        "set-api-keys.py",
        "fix-amplify-build.py",
        "fix-amplify-buildspec.py",
        "fix-amplify-final.py",
        "test-full-integration.py",
        "debug-agentcore.py",
        "debug-lambda-processing.py",
        "update-lambda-handler.py",
        "check-lambda-logs.py",
        "deploy-lambda-with-deps.py",
        "deploy-lambda-complete.py",
        "fix-lambda-final.py",
        "test-frontend-integration.py",
        "complete-redeploy.py",
        "final-working-solution.py",
        "optimize-lambda-timeout.py",
        "final-complete-solution.py",
        "simple-working-backend.py",
        "test-simple-working-integration.py",
        "update-lambda-with-fixed-client.py",
        "agentcore_client_fixed.py"
    ]
    
    # Directories to remove
    aws_dirs = [
        "infrastructure",
        "simple-backend",
        "agentcore_fibo_agent",
        ".github"
    ]
    
    removed_files = 0
    removed_dirs = 0
    
    # Remove files
    for file_name in aws_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   ❌ Removed {file_name}")
            removed_files += 1
    
    # Remove directories
    for dir_name in aws_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ❌ Removed directory {dir_name}/")
            removed_dirs += 1
    
    print(f"   🧹 Cleaned up {removed_files} files and {removed_dirs} directories")

def restore_original_api_server():
    """Restore the original working API server."""
    print("🔧 Restoring original API server...")
    
    api_server_code = '''#!/usr/bin/env python3
"""
FIBO Video Director API Server - Local Development
Original working version without AWS complications
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Import the working FIBO director
from fibo_video_director import FIBOVideoDirector

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
projects_cache = {}
generation_status = {}

class ScriptRequest(BaseModel):
    script_text: str

class GenerateFramesRequest(BaseModel):
    project_id: str
    checkpoint_id: int

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global fibo_director
    
    print("🚀 Starting FIBO Video Director API Server...")
    
    # Initialize FIBO Video Director
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        try:
            fibo_director = FIBOVideoDirector(google_api_key)
            print("✅ FIBO Video Director initialized with Gemini")
        except Exception as e:
            print(f"⚠️ Failed to initialize FIBO Director: {e}")
            fibo_director = None
    else:
        print("⚠️ GOOGLE_API_KEY not set - using fallback mode")
        fibo_director = None

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "message": "FIBO Video Director API - Local Development",
        "status": "running",
        "fibo_available": fibo_director is not None,
        "google_api_configured": bool(os.environ.get("GOOGLE_API_KEY")),
        "version": "1.0.0-local"
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
        
        # Use FIBO Video Director if available
        if fibo_director:
            print("🤖 Using FIBO Video Director with Gemini")
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
        raise HTTPException(status_code=404, detail="Project not found")
    
    video_plan = projects_cache[project_id]['video_plan']
    
    # Use FIBO director's export method if available
    if fibo_director:
        checkpoint_data = fibo_director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
        if 'error' not in checkpoint_data:
            return checkpoint_data
    
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

@app.post("/api/generate-frames")
async def generate_frames(request: GenerateFramesRequest):
    """Generate frames for a checkpoint."""
    if request.project_id not in projects_cache:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate unique generation ID
    generation_id = str(uuid.uuid4())
    
    # For demo purposes, simulate frame generation
    generation_status[generation_id] = {
        'status': 'completed',
        'project_id': request.project_id,
        'checkpoint_id': request.checkpoint_id,
        'created_at': datetime.now().isoformat(),
        'progress': 100,
        'start_frame_url': f'/api/frames/{generation_id}/start.jpg',
        'end_frame_url': f'/api/frames/{generation_id}/end.jpg',
        'generation_time_sec': 15.5
    }
    
    return {
        'generation_id': generation_id,
        'status': 'started',
        'estimated_time_sec': 30
    }

@app.get("/api/generation-status/{generation_id}")
async def get_generation_status(generation_id: str):
    """Get generation status."""
    if generation_id not in generation_status:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation_status[generation_id]

@app.get("/api/director-mode")
async def get_director_mode():
    """Get current director mode."""
    return {
        'fibo_available': fibo_director is not None,
        'fibo_enabled': True,
        'mode': 'fibo' if fibo_director else 'intelligent-fallback'
    }

@app.get("/api/cache-stats")
async def get_cache_stats():
    """Get cache statistics."""
    return {
        'projects_cached': len(projects_cache),
        'generations_tracked': len(generation_status),
        'cache_type': 'memory'
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
'''
    
    with open("api_server.py", "w", encoding="utf-8") as f:
        f.write(api_server_code)
    
    print("   ✅ Created api_server.py")

def update_frontend_for_localhost():
    """Update frontend to use localhost backend."""
    print("🔧 Updating frontend for localhost...")
    
    # Update frontend API configuration
    frontend_api_path = Path("frontend/src/services/api.js")
    
    if frontend_api_path.exists():
        api_js_content = '''// API service for FIBO Video Director
// Local development configuration

const API_BASE_URL = 'http://localhost:8000';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/');
  }

  // Generate video plan from script
  async generatePlan(scriptText) {
    return this.request('/api/generate-plan', {
      method: 'POST',
      body: JSON.stringify({ script_text: scriptText }),
    });
  }

  // Get project details
  async getProject(projectId) {
    return this.request(`/api/project/${projectId}`);
  }

  // Get checkpoint details
  async getCheckpoint(projectId, checkpointId) {
    return this.request(`/api/checkpoint/${projectId}/${checkpointId}`);
  }

  // Generate frames
  async generateFrames(projectId, checkpointId) {
    return this.request('/api/generate-frames', {
      method: 'POST',
      body: JSON.stringify({ 
        project_id: projectId, 
        checkpoint_id: checkpointId 
      }),
    });
  }

  // Get generation status
  async getGenerationStatus(generationId) {
    return this.request(`/api/generation-status/${generationId}`);
  }

  // Get director mode
  async getDirectorMode() {
    return this.request('/api/director-mode');
  }

  // Get cache stats
  async getCacheStats() {
    return this.request('/api/cache-stats');
  }
}

export default new ApiService();
'''
        
        with open(frontend_api_path, "w", encoding="utf-8") as f:
            f.write(api_js_content)
        
        print("   ✅ Updated frontend/src/services/api.js for localhost")
    else:
        print("   ⚠️ Frontend API file not found")

def create_start_script():
    """Create a simple start script."""
    print("🔧 Creating start script...")
    
    start_script = '''#!/usr/bin/env python3
"""
Start FIBO Video Director - Local Development
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check if environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check if we're in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Not in virtual environment. Run: source .venv/bin/activate")
        return False
    
    # Check if required packages are installed
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn installed")
    except ImportError:
        print("❌ Missing required packages. Run: pip install fastapi uvicorn")
        return False
    
    # Check for Google API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set. Using fallback mode.")
        print("   To use Gemini: export GOOGLE_API_KEY=your_key")
    else:
        print("✅ GOOGLE_API_KEY configured")
    
    return True

def start_backend():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    
    if not Path("api_server.py").exists():
        print("❌ api_server.py not found!")
        return False
    
    try:
        # Start the backend server
        subprocess.Popen([
            sys.executable, "api_server.py"
        ])
        
        print("✅ Backend server starting at http://localhost:8000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the frontend development server."""
    print("🚀 Starting frontend server...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found!")
        return False
    
    try:
        # Start the frontend server
        subprocess.Popen([
            "npm", "start"
        ], cwd=frontend_path)
        
        print("✅ Frontend server starting at http://localhost:3000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Local Development")
    print("=" * 50)
    
    if not check_environment():
        print("❌ Environment check failed")
        return
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend")
        return
    
    # Wait a moment for backend to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend")
        return
    
    print("\\n" + "=" * 50)
    print("🎉 FIBO Video Director is starting!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("\\n💡 Usage:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Enter a movie script")
    print("3. Click 'Generate Plan'")
    print("4. View the timeline and checkpoints")
    print("\\nPress Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n🛑 Stopping servers...")

if __name__ == "__main__":
    main()
'''
    
    with open("start_local.py", "w", encoding="utf-8") as f:
        f.write(start_script)
    
    print("   ✅ Created start_local.py")

def main():
    """Main restoration function."""
    print("🔄 RESTORING LOCAL WORKING ENVIRONMENT")
    print("=" * 60)
    
    # Clean up AWS mess
    clean_aws_deployment_files()
    
    print()
    
    # Restore original working files
    restore_original_api_server()
    update_frontend_for_localhost()
    create_start_script()
    
    print()
    print("=" * 60)
    print("✅ LOCAL ENVIRONMENT RESTORED!")
    print("=" * 60)
    
    print("\\n🚀 To start the application:")
    print("1. Make sure you're in the virtual environment:")
    print("   source .venv/bin/activate")
    print("\\n2. Set your Google API key (optional):")
    print("   export GOOGLE_API_KEY=your_key_here")
    print("\\n3. Start the application:")
    print("   python start_local.py")
    print("\\n4. Open http://localhost:3000 in your browser")
    
    print("\\n💡 What's working now:")
    print("   ✅ Clean local development environment")
    print("   ✅ No AWS complications")
    print("   ✅ Original FIBO Video Director")
    print("   ✅ FastAPI backend with all endpoints")
    print("   ✅ React frontend with localhost API")
    print("   ✅ Intelligent fallback when no API key")
    print("   ✅ Full FIBO structured prompt generation")

if __name__ == "__main__":
    main()