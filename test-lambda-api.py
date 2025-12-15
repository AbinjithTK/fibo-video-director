#!/usr/bin/env python3
"""
Test the deployed Lambda API
"""

import requests
import json
import time

# Configuration
API_URL = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check...")
    
    try:
        response = requests.get(f"{API_URL}/")
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Status: {data.get('status')}")
        print(f"   🤖 AgentCore: {data.get('agentcore_available')}")
        print(f"   🔑 Google API: {data.get('google_api_configured')}")
        print(f"   🎨 FAL: {data.get('fal_configured')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

def test_generate_plan():
    """Test video plan generation."""
    print("\n📝 Testing video plan generation...")
    
    test_script = """
    FADE IN:
    
    EXT. CITY STREET - DAY
    
    A bustling city street with people walking. The camera follows ALEX, a young professional in a business suit, as they walk confidently down the sidewalk.
    
    ALEX stops at a coffee shop and orders their usual morning coffee.
    
    INT. COFFEE SHOP - CONTINUOUS
    
    Alex waits for their order, checking their phone. The barista calls out their name.
    
    FADE OUT.
    """
    
    try:
        response = requests.post(
            f"{API_URL}/api/generate-plan",
            json={"script_text": test_script},
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Project ID: {data.get('project_id')}")
        print(f"   🎬 Title: {data.get('project_title')}")
        print(f"   ⏱️ Duration: {data.get('total_duration_sec')}s")
        print(f"   📋 Checkpoints: {len(data.get('checkpoints', []))}")
        
        return data.get('project_id')
        
    except Exception as e:
        print(f"   ❌ Plan generation failed: {e}")
        return None

def test_get_project(project_id):
    """Test getting project details."""
    print(f"\n📊 Testing project details for {project_id}...")
    
    try:
        response = requests.get(f"{API_URL}/api/project/{project_id}")
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Project: {data.get('project_title')}")
        print(f"   📋 Checkpoints: {len(data.get('checkpoints', []))}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Get project failed: {e}")
        return False

def test_get_checkpoint(project_id, checkpoint_id=1):
    """Test getting checkpoint details."""
    print(f"\n🎯 Testing checkpoint {checkpoint_id} for {project_id}...")
    
    try:
        response = requests.get(f"{API_URL}/api/checkpoint/{project_id}/{checkpoint_id}")
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Scene: {data.get('scene_description', '')[:50]}...")
        print(f"   ⏱️ Duration: {data.get('duration_sec')}s")
        print(f"   🎨 Start frame: {data.get('fibo_start_frame', {}).get('short_description', 'N/A')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Get checkpoint failed: {e}")
        return False

def test_director_mode():
    """Test director mode endpoints."""
    print("\n🎭 Testing director mode...")
    
    try:
        response = requests.get(f"{API_URL}/api/director-mode")
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ AgentCore available: {data.get('agentcore_available')}")
        print(f"   🤖 AgentCore enabled: {data.get('agentcore_enabled')}")
        print(f"   🎯 Mode: {data.get('mode')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Director mode test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 FIBO Video Director - Lambda API Tests")
    print("=" * 50)
    print(f"🌐 API URL: {API_URL}")
    print()
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed - stopping tests")
        return
    
    # Test director mode
    test_director_mode()
    
    # Test video plan generation
    project_id = test_generate_plan()
    
    if project_id:
        # Test project details
        test_get_project(project_id)
        
        # Test checkpoint details
        test_get_checkpoint(project_id)
    
    print("\n" + "=" * 50)
    print("🎉 API Tests Complete!")
    print("\n📋 Next Steps:")
    print("1. Set Lambda environment variables if any tests failed")
    print("2. Update Amplify frontend REACT_APP_API_URL")
    print("3. Test the full frontend integration")

if __name__ == "__main__":
    main()