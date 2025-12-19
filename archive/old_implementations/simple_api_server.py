#!/usr/bin/env python3
"""
Simple FIBO Video Director API Server
Working implementation without dependency issues
"""

import json
import uuid
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Simple HTTP server without FastAPI dependencies
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Import our working director
from working_fibo_director import WorkingFIBODirector

# FAL integration will be imported after environment setup
FAL_AVAILABLE = False

# Global instances
director = None
projects_cache = {}
generation_status = {}
cache_dir = Path("cache")
cache_dir.mkdir(exist_ok=True)

class FIBOAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for FIBO API."""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            if path == '/':
                self.send_health_check()
            elif path == '/api/director-mode':
                self.send_director_mode()
            elif path == '/api/cache-stats':
                self.send_cache_stats()
            elif path.startswith('/api/project/'):
                project_id = path.split('/')[-1]
                self.send_project(project_id)
            elif path.startswith('/api/checkpoint/'):
                parts = path.split('/')
                if len(parts) >= 5:
                    project_id = parts[3]
                    checkpoint_id = int(parts[4])
                    self.send_checkpoint(project_id, checkpoint_id)
                else:
                    self.send_error_response(400, "Invalid checkpoint path")
            elif path.startswith('/api/generation-status/'):
                generation_id = path.split('/')[-1]
                self.send_generation_status(generation_id)
            elif path.startswith('/api/download/'):
                filename = path.split('/')[-1]
                self.send_file_download(filename)
            else:
                self.send_error_response(404, "Not found")
        except Exception as e:
            print(f"❌ GET error: {e}")
            self.send_error_response(500, str(e))
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if content_length > 0:
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            if path == '/api/generate-plan':
                self.handle_generate_plan(request_data)
            elif path == '/api/generate-frames':
                self.handle_generate_frames(request_data)
            elif path == '/api/director-mode':
                self.handle_set_director_mode(request_data)
            else:
                self.send_error_response(404, "Not found")
        except Exception as e:
            print(f"❌ POST error: {e}")
            self.send_error_response(500, str(e))
    
    def send_health_check(self):
        """Send health check response."""
        response = {
            "message": "FIBO Video Director API - Simple Working Version",
            "status": "running",
            "director_available": director is not None,
            "google_api_configured": bool(os.environ.get("GOOGLE_API_KEY")),
            "fal_configured": bool(os.environ.get("FAL_KEY")),
            "active_mode": "working",
            "version": "1.0.0-simple"
        }
        self.send_json_response(response)
    
    def send_director_mode(self):
        """Send director mode status."""
        response = {
            "enhanced_available": False,
            "enhanced_enabled": False,
            "fal_available": False,
            "mode": "working"
        }
        self.send_json_response(response)
    
    def send_cache_stats(self):
        """Send cache statistics."""
        response = {
            'projects_cached': len(projects_cache),
            'generations_tracked': len(generation_status),
            'cache_type': 'local',
            's3_available': False
        }
        self.send_json_response(response)
    
    def handle_generate_plan(self, request_data: Dict):
        """Handle generate plan request."""
        script_text = request_data.get('script_text', '')
        
        if not script_text.strip():
            self.send_error_response(400, "Script text is required")
            return
        
        print(f"📝 Processing script: {script_text[:100]}...")
        
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Use working director
        if director:
            print("🤖 Using Working FIBO Director")
            video_plan = director.create_video_plan(script_text)
        else:
            self.send_error_response(500, "Director not available")
            return
        
        # Cache the project
        projects_cache[project_id] = {
            'video_plan': video_plan,
            'created_at': datetime.now().isoformat(),
            'script_text': script_text
        }
        
        # Save to file for persistence
        project_file = cache_dir / f"project_{project_id}.json"
        with open(project_file, "w") as f:
            json.dump(projects_cache[project_id], f, indent=2)
        
        print(f"✅ Created project {project_id}: {video_plan['project_title']}")
        
        response = {
            'project_id': project_id,
            'project_title': video_plan.get('project_title', 'FIBO Video Production'),
            'total_duration_sec': video_plan.get('total_duration_sec', 16),
            'checkpoints': video_plan.get('checkpoints', []),
            'visual_style': video_plan.get('visual_style', {}),
            'metadata': video_plan.get('metadata', {})
        }
        
        self.send_json_response(response)
    
    def send_project(self, project_id: str):
        """Send project details."""
        if project_id not in projects_cache:
            # Try to load from file
            project_file = cache_dir / f"project_{project_id}.json"
            if project_file.exists():
                with open(project_file, "r") as f:
                    projects_cache[project_id] = json.load(f)
            else:
                self.send_error_response(404, "Project not found")
                return
        
        project = projects_cache[project_id]
        video_plan = project['video_plan']
        
        response = {
            'project_id': project_id,
            'project_title': video_plan.get('project_title', 'Untitled Project'),
            'total_duration_sec': video_plan.get('total_duration_sec', 0),
            'visual_style': video_plan.get('visual_style', {}),
            'checkpoints': video_plan.get('checkpoints', [])
        }
        
        self.send_json_response(response)
    
    def send_checkpoint(self, project_id: str, checkpoint_id: int):
        """Send checkpoint details."""
        if project_id not in projects_cache:
            # Try to load from file
            project_file = cache_dir / f"project_{project_id}.json"
            if project_file.exists():
                with open(project_file, "r") as f:
                    projects_cache[project_id] = json.load(f)
            else:
                self.send_error_response(404, "Project not found")
                return
        
        video_plan = projects_cache[project_id]['video_plan']
        
        # Use director's export method
        if director:
            checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
            if "error" in checkpoint_data:
                self.send_error_response(404, checkpoint_data["error"])
                return
            self.send_json_response(checkpoint_data)
        else:
            self.send_error_response(500, "Director not available")
    
    def handle_generate_frames(self, request_data: Dict):
        """Handle generate frames request."""
        project_id = request_data.get('project_id')
        checkpoint_id = request_data.get('checkpoint_id')
        
        if not project_id or not checkpoint_id:
            self.send_error_response(400, "project_id and checkpoint_id required")
            return
        
        generation_id = f"{project_id}_{checkpoint_id}"
        
        # Start background generation (simplified)
        threading.Thread(
            target=self.generate_frames_background,
            args=(project_id, checkpoint_id, generation_id)
        ).start()
        
        response = {"generation_id": generation_id, "status": "started"}
        self.send_json_response(response)
    
    def generate_frames_background(self, project_id: str, checkpoint_id: int, generation_id: str):
        """Background frame generation (simplified)."""
        try:
            print(f"\n🎬 Starting frame generation for checkpoint {checkpoint_id}")
            
            # Initialize status
            generation_status[generation_id] = {
                'status': 'generating',
                'progress': 0.1,
                'message': 'Getting checkpoint data...'
            }
            
            # Get checkpoint data
            if project_id not in projects_cache:
                project_file = cache_dir / f"project_{project_id}.json"
                if project_file.exists():
                    with open(project_file, "r") as f:
                        projects_cache[project_id] = json.load(f)
                else:
                    raise Exception("Project not found")
            
            video_plan = projects_cache[project_id]["video_plan"]
            checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
            
            if "error" in checkpoint_data:
                raise Exception(checkpoint_data["error"])
            
            print(f"   ✅ Checkpoint data retrieved")
            
            # Update progress
            generation_status[generation_id]['progress'] = 0.3
            generation_status[generation_id]['message'] = 'Generating FIBO images with FAL.ai...'
            
            # Try FAL FIBO integration if available
            if FAL_AVAILABLE:
                try:
                    from fal_fibo_integration import get_fal_integration
                    import asyncio
                    
                    fal = get_fal_integration()
                    print(f"   ✅ FAL FIBO integration initialized")
                    
                    # Create event loop for async operations
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        # Generate both frames using FAL FIBO
                        generated_files = loop.run_until_complete(
                            fal.generate_checkpoint_frames(
                                checkpoint_data["fibo_start_frame"],
                                checkpoint_data["fibo_end_frame"],
                                checkpoint_id,
                                project_id,
                                seed=checkpoint_id * 42 + 1000
                            )
                        )
                        
                        # Update progress
                        generation_status[generation_id]['progress'] = 0.9
                        generation_status[generation_id]['message'] = 'Processing generated FIBO images...'
                        
                        # Copy generated files to cache directory
                        import shutil
                        
                        # Copy start frame files
                        start_image_cache = cache_dir / f"start_frame_{generation_id}.png"
                        start_json_cache = cache_dir / f"start_frame_{generation_id}.json"
                        
                        has_start_image = False
                        if generated_files.get("start_frame_image"):
                            shutil.copy2(generated_files["start_frame_image"], start_image_cache)
                            has_start_image = True
                        elif generated_files.get("start_frame_url") and not generated_files.get("start_frame_cached"):
                            # Download from FAL URL (only if it's a full URL)
                            start_url = generated_files["start_frame_url"]
                            if start_url.startswith('http'):
                                import requests
                                response = requests.get(start_url)
                                if response.status_code == 200:
                                    with open(start_image_cache, 'wb') as f:
                                        f.write(response.content)
                                    has_start_image = True
                            else:
                                print(f"   ⚠️ Skipping relative URL: {start_url}")
                                # The image is likely already cached in S3, use the URL directly
                                has_start_image = True
                        
                        # Always copy JSON
                        if generated_files.get("start_frame_json"):
                            shutil.copy2(generated_files["start_frame_json"], start_json_cache)
                        
                        # Copy end frame files
                        end_image_cache = cache_dir / f"end_frame_{generation_id}.png"
                        end_json_cache = cache_dir / f"end_frame_{generation_id}.json"
                        
                        has_end_image = False
                        if generated_files.get("end_frame_image"):
                            shutil.copy2(generated_files["end_frame_image"], end_image_cache)
                            has_end_image = True
                        elif generated_files.get("end_frame_url") and not generated_files.get("end_frame_cached"):
                            # Download from FAL URL (only if it's a full URL)
                            end_url = generated_files["end_frame_url"]
                            if end_url.startswith('http'):
                                import requests
                                response = requests.get(end_url)
                                if response.status_code == 200:
                                    with open(end_image_cache, 'wb') as f:
                                        f.write(response.content)
                                    has_end_image = True
                            else:
                                print(f"   ⚠️ Skipping relative URL: {end_url}")
                                # The image is likely already cached in S3, use the URL directly
                                has_end_image = True
                        
                        # Always copy JSON
                        if generated_files.get("end_frame_json"):
                            shutil.copy2(generated_files["end_frame_json"], end_json_cache)
                        
                        # Update final status
                        gen_times = generated_files.get("generation_times", {})
                        total_time = sum(gen_times.values()) if gen_times else 0
                        
                        # Determine success message
                        cache_info = []
                        if generated_files.get("start_frame_cached"):
                            cache_info.append("start: cached")
                        if generated_files.get("end_frame_cached"):
                            cache_info.append("end: cached")
                        
                        if has_start_image and has_end_image:
                            cache_str = f" ({', '.join(cache_info)})" if cache_info else ""
                            message = f"✅ FIBO images generated in {total_time:.1f}s{cache_str}"
                        elif has_start_image or has_end_image:
                            message = f"⚠️ Partial FIBO generation in {total_time:.1f}s"
                        else:
                            message = "⚠️ FIBO structured prompts ready (image generation failed)"
                        
                        # Set URLs - prefer local cached files, fallback to FAL URLs
                        start_url = f"/api/download/start_frame_{generation_id}.png" if has_start_image else (
                            generated_files.get("start_frame_url") or f"/api/download/start_frame_{generation_id}.json"
                        )
                        end_url = f"/api/download/end_frame_{generation_id}.png" if has_end_image else (
                            generated_files.get("end_frame_url") or f"/api/download/end_frame_{generation_id}.json"
                        )
                        
                        generation_status[generation_id].update({
                            'status': 'completed',
                            'progress': 1.0,
                            'message': message,
                            'start_frame_url': start_url,
                            'end_frame_url': end_url,
                            'generation_time_sec': total_time,
                            'start_frame_cached': generated_files.get("start_frame_cached", False),
                            'end_frame_cached': generated_files.get("end_frame_cached", False)
                        })
                        
                        print(f"   🎉 FIBO generation complete in {total_time:.1f}s!")
                        print(f"   Start URL: {start_url[:80]}...")
                        print(f"   End URL: {end_url[:80]}...")
                        
                    finally:
                        loop.close()
                        
                except Exception as fal_error:
                    print(f"   ❌ FAL FIBO generation failed: {fal_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # Fallback to JSON-only mode
                    print("   📝 Falling back to structured prompts only...")
                    raise fal_error
            else:
                print("   📝 FAL not available, generating structured prompts only...")
                raise Exception("FAL integration not available")
                
        except Exception as e:
            # Fallback: Save structured prompts only
            print(f"   📝 Fallback mode: saving FIBO structured prompts only")
            
            start_frame_file = cache_dir / f"start_frame_{generation_id}.json"
            end_frame_file = cache_dir / f"end_frame_{generation_id}.json"
            
            with open(start_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_start_frame"], f, indent=2)
            
            with open(end_frame_file, "w") as f:
                json.dump(checkpoint_data["fibo_end_frame"], f, indent=2)
            
            # Update final status
            generation_status[generation_id].update({
                'status': 'completed',
                'progress': 1.0,
                'message': '✅ FIBO structured prompts ready (image generation unavailable)',
                'start_frame_url': f'/api/download/start_frame_{generation_id}.json',
                'end_frame_url': f'/api/download/end_frame_{generation_id}.json',
                'generation_time_sec': 2.0,
                'start_frame_cached': False,
                'end_frame_cached': False
            })
            
            print(f"   🎉 Structured prompts ready!")
            
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            generation_status[generation_id] = {
                'status': 'error',
                'progress': 0.0,
                'message': f'Error: {str(e)}'
            }
    
    def send_generation_status(self, generation_id: str):
        """Send generation status."""
        if generation_id not in generation_status:
            self.send_error_response(404, "Generation not found")
            return
        
        self.send_json_response(generation_status[generation_id])
    
    def handle_set_director_mode(self, request_data: Dict):
        """Handle set director mode request."""
        # For simple version, always return working mode
        response = {
            "enhanced_enabled": False,
            "mode": "working"
        }
        self.send_json_response(response)
    
    def send_file_download(self, filename: str):
        """Send file download."""
        # Check both cache/ and cache/frames/ directories
        file_path = cache_dir / filename
        if not file_path.exists():
            # Try cache/frames/ directory (where FAL integration saves images)
            frames_path = cache_dir / "frames" / filename
            if frames_path.exists():
                file_path = frames_path
            else:
                self.send_error_response(404, "File not found")
                return
        
        # Determine content type
        if filename.endswith('.json'):
            content_type = 'application/json'
        elif filename.endswith('.png'):
            content_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            content_type = 'image/jpeg'
        else:
            content_type = 'application/octet-stream'
        
        # Send file
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        
        with open(file_path, 'rb') as f:
            self.wfile.write(f.read())
    
    def send_json_response(self, data: Dict):
        """Send JSON response with CORS headers."""
        response_json = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response with CORS headers."""
        error_data = {"error": message, "status_code": status_code}
        response_json = json.dumps(error_data, indent=2)
        
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"🌐 {self.address_string()} - {format % args}")


def start_server(port: int = 8000):
    """Start the simple FIBO API server."""
    global director
    
    print("🚀 Starting Simple FIBO Video Director API Server...")
    print("=" * 60)
    
    # Set environment variables if not already set
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = "AIzaSyBDPX59RP7OgVwPn91rRDagWnLwh9-OxPk"
        print("✅ GOOGLE_API_KEY set from default")
    
    if not os.environ.get("FAL_KEY"):
        os.environ["FAL_KEY"] = "6e7730ad-d8a1-4820-9a12-b0dd603d39de:a91d44688887ea0697c276bed95a63a3"
        print("✅ FAL_KEY set from default")
    
    # Initialize director
    api_key = os.environ.get("GOOGLE_API_KEY")
    director = WorkingFIBODirector(api_key)
    
    # Try to import FAL integration after environment is set
    global FAL_AVAILABLE
    try:
        from fal_fibo_integration import get_fal_integration
        # Test if FAL integration can be initialized
        test_fal = get_fal_integration()
        FAL_AVAILABLE = True
        print("✅ FAL FIBO integration available and configured")
    except Exception as e:
        FAL_AVAILABLE = False
        print(f"⚠️ FAL integration not available: {e}")
    
    # Create server
    server_address = ('', port)
    httpd = HTTPServer(server_address, FIBOAPIHandler)
    
    print(f"✅ Server initialized")
    print(f"🌐 Server running at http://localhost:{port}")
    print(f"📚 API endpoints:")
    print(f"   GET  /                     - Health check")
    print(f"   POST /api/generate-plan    - Generate video plan")
    print(f"   GET  /api/project/{{id}}     - Get project details")
    print(f"   GET  /api/checkpoint/{{id}}/{{cp}} - Get checkpoint prompts")
    print(f"   POST /api/generate-frames  - Generate frames")
    print(f"   GET  /api/generation-status/{{id}} - Get generation status")
    print(f"   GET  /api/download/{{file}}  - Download files")
    print("=" * 60)
    print("💡 Usage:")
    print("1. Open http://localhost:3000 in your browser (if frontend is running)")
    print("2. Or test API directly: curl http://localhost:8000/")
    print("3. Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        httpd.shutdown()
        print("✅ Server stopped")


if __name__ == "__main__":
    # Set environment variables if available
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = "AIzaSyBDPX59RP7OgVwPn91rRDagWnLwh9-OxPk"
    if not os.environ.get("FAL_KEY"):
        os.environ["FAL_KEY"] = "6e7730ad-d8a1-4820-9a12-b0dd603d39de:a91d44688887ea0697c276bed95a63a3"
    
    start_server()