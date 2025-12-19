#!/usr/bin/env python3
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
    
    print("\n" + "=" * 50)
    print("🎉 FIBO Video Director is starting!")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("\n💡 Usage:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Enter a movie script")
    print("3. Click 'Generate Plan'")
    print("4. View the timeline and checkpoints")
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")

if __name__ == "__main__":
    main()
