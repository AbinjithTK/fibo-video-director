#!/usr/bin/env python3
"""
FIBO Video Director - Main Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add core directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "core"))

# Import and run the API server
from api_server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)