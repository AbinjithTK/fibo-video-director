#!/usr/bin/env python3
"""
FIBO Video Director Application Launcher
Starts both backend and frontend servers for local development
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting FIBO Video Director Backend...")
    # Go back to project root
    project_root = Path(__file__).parent.parent
    return subprocess.Popen([
        sys.executable, "app.py"
    ], cwd=project_root)

def start_frontend():
    """Start the React frontend development server."""
    print("🌐 Starting React Frontend...")
    frontend_dir = Path(__file__).parent.parent / "frontend"
    return subprocess.Popen([
        "npm", "start"
    ], cwd=frontend_dir)

def main():
    """Main application launcher."""
    print("🎬 FIBO Video Director - Application Launcher")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Check if we're in the right directory
    if not (project_root / "core" / "api_server.py").exists():
        print("❌ Error: core/api_server.py not found. Please run from project root.")
        sys.exit(1)
    
    if not (project_root / "frontend" / "package.json").exists():
        print("❌ Error: Frontend not found. Please ensure frontend is set up.")
        sys.exit(1)
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Give backend time to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n✅ Both servers started successfully!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n⏹️  Press Ctrl+C to stop both servers")
        
        # Wait for user interrupt
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for processes to terminate
            backend_process.wait()
            frontend_process.wait()
            
            print("✅ Servers stopped successfully!")
            
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()