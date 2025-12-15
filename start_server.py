#!/usr/bin/env python3
"""
FIBO Video Director Server Startup Script

This script starts the FastAPI server with proper environment setup.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up the environment for FIBO integration."""
    
    # Get current directory (should be FIBO project root)
    fibo_root = Path.cwd()
    
    # Set FIBO_ROOT environment variable
    os.environ["FIBO_ROOT"] = str(fibo_root)
    
    # Add FIBO root to PYTHONPATH
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    if str(fibo_root) not in current_pythonpath:
        os.environ["PYTHONPATH"] = f"{current_pythonpath}:{fibo_root}"
    
    # Check for required files
    required_files = [
        "generate.py",
        "src/fibo_inference/",
        "api_server.py",
        "fibo_video_director.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (fibo_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\nPlease ensure you're running this from the FIBO project root directory.")
        sys.exit(1)
    
    # Check for Google API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY not set!")
        print("Please set your Google API key:")
        print("   export GOOGLE_API_KEY=your_key_here")
        print("   # or")
        print("   set GOOGLE_API_KEY=your_key_here  # Windows")
        print("\nGet your API key from: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    print("✅ Environment setup complete")
    print(f"📁 FIBO Root: {fibo_root}")
    print(f"🔑 Google API Key: {'*' * 20}...{os.environ['GOOGLE_API_KEY'][-4:]}")

def main():
    """Main startup function."""
    print("🎬 FIBO Video Director Server")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Import and run the server
    try:
        import uvicorn
        from api_server import app
        
        print("\n🚀 Starting server...")
        print("📡 API Server: http://localhost:8000")
        print("📋 API Docs: http://localhost:8000/docs")
        print("🎯 Frontend: http://localhost:3000 (if running)")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Get port from environment (App Runner sets this)
        port = int(os.environ.get("PORT", 8000))
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            reload=False,  # Disable reload in production
            access_log=True
        )
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install required packages:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()