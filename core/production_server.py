#!/usr/bin/env python3
"""
FIBO Video Director API Server - Production Configuration
Optimized for AWS deployment with proper CORS, security, and monitoring
"""

import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the existing API server components
from api_server import (
    ScriptRequest, GenerateFramesRequest, GenerationStatus,
    projects_cache, generation_status, cache_dir,
    startup_event, generate_plan, get_project, get_checkpoint,
    generate_frames, get_generation_status, download_file,
    proxy_image, get_director_mode, set_director_mode, get_cache_stats
)

# Create FastAPI app with production settings
app = FastAPI(
    title="FIBO Video Director API",
    description="Production-grade API for AI-powered video production planning",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Production CORS configuration
ALLOWED_ORIGINS = [
    "https://main.d2x8j9k4l5m3n7.amplifyapp.com",  # Your Amplify URL
    "https://*.amplifyapp.com",
    "http://localhost:3000",  # For local development
    "http://localhost:3001",
]

# Add environment-specific origins
if os.getenv("FRONTEND_URL"):
    ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
TRUSTED_HOSTS = ["*"]  # Configure with your actual domains in production
if os.getenv("TRUSTED_HOSTS"):
    TRUSTED_HOSTS = os.getenv("TRUSTED_HOSTS").split(",")

app.add_middleware(TrustedHostMiddleware, allowed_hosts=TRUSTED_HOSTS)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "fibo-video-director-api",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Root endpoint with production info
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "FIBO Video Director API - Production",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs" if os.getenv("ENVIRONMENT") != "production" else "disabled",
        "health": "/health"
    }

# Register all existing endpoints
app.add_event_handler("startup", startup_event)
app.post("/api/generate-plan")(generate_plan)
app.get("/api/project/{project_id}")(get_project)
app.get("/api/checkpoint/{project_id}/{checkpoint_id}")(get_checkpoint)
app.post("/api/generate-frames")(generate_frames)
app.get("/api/generation-status/{generation_id}")(get_generation_status)
app.get("/api/download/{filename}")(download_file)
app.get("/api/proxy-image")(proxy_image)
app.get("/api/director-mode")(get_director_mode)
app.post("/api/director-mode")(set_director_mode)
app.get("/api/cache-stats")(get_cache_stats)

# Production error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "status": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status": 500}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting FIBO Video Director API (Production)")
    print(f"🌐 Server: {host}:{port}")
    print(f"🔒 CORS Origins: {ALLOWED_ORIGINS}")
    print(f"📊 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    uvicorn.run(
        "core.production_server:app",
        host=host,
        port=port,
        reload=False,  # Disabled for production
        access_log=True,
        log_level="info"
    )