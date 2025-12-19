#!/usr/bin/env python3
"""
Set Environment Variables for FIBO Video Director
"""

import os

def set_environment_variables():
    """Set the required environment variables."""
    
    # API Keys provided by user
    google_api_key = "AIzaSyBDPX59RP7OgVwPn91rRDagWnLwh9-OxPk"
    fal_api_key = "6e7730ad-d8a1-4820-9a12-b0dd603d39de:a91d44688887ea0697c276bed95a63a3"
    
    # Set environment variables
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["FAL_KEY"] = fal_api_key
    
    print("✅ Environment variables set:")
    print(f"   GOOGLE_API_KEY: {google_api_key[:20]}...")
    print(f"   FAL_KEY: {fal_api_key[:20]}...")
    
    # Also create a .env file for persistence
    with open(".env", "w") as f:
        f.write(f"GOOGLE_API_KEY={google_api_key}\n")
        f.write(f"FAL_KEY={fal_api_key}\n")
    
    print("✅ Created .env file for persistence")

if __name__ == "__main__":
    set_environment_variables()