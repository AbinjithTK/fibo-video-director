#!/usr/bin/env python3
"""
Complete System Test for FIBO Video Director
Tests all components: Strands Agents, FAL integration, API server, and Working Director
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_setup():
    """Test that all environment variables are properly set."""
    print("🔧 Testing Environment Setup...")
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API',
        'FAL_KEY': 'FAL.ai API',
        'FIBO_S3_BUCKET': 'S3 Bucket'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"   ✅ {description}: {value[:20]}...")
        else:
            print(f"   ❌ {description}: NOT SET")
            all_good = False
    
    return all_good

def test_strands_agents():
    """Test Strands agents functionality."""
    print("\n🤖 Testing Strands Agents...")
    
    try:
        from strands import Agent, tool
        from strands.models.gemini import GeminiModel
        
        @tool
        def test_tool(message: str) -> str:
            """A simple test tool.
            
            Args:
                message: Test message to echo
            """
            return f"Tool received: {message}"
        
        # Create model
        model = GeminiModel(
            client_args={"api_key": os.environ.get("GOOGLE_API_KEY")},
            model_id="gemini-2.5-flash",
            params={"temperature": 0.3}
        )
        
        # Create agent
        agent = Agent(
            model=model,
            tools=[test_tool],
            system_prompt="You are a test agent. Use the test_tool when asked."
        )
        
        # Test the agent
        response = agent("Use the test tool with message 'Hello FIBO'")
        response_text = str(response)
        print(f"   ✅ Strands Agent Response: {response_text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Strands Agents Error: {e}")
        return False

def test_working_director():
    """Test the Working FIBO Director."""
    print("\n🎬 Testing Working FIBO Director...")
    
    try:
        from working_fibo_director import WorkingFIBODirector
        
        director = WorkingFIBODirector()
        
        test_script = """
        EXT. SPACE STATION - DAY
        
        The International Space Station orbits Earth. 
        ASTRONAUT SARAH floats in the observation module, 
        watching the blue planet below.
        
        SARAH
        Mission Control, we have a beautiful view today.
        """
        
        video_plan = director.create_video_plan(test_script)
        
        print(f"   ✅ Project: {video_plan['project_title']}")
        print(f"   ✅ Duration: {video_plan['total_duration_sec']} seconds")
        print(f"   ✅ Checkpoints: {len(video_plan['checkpoints'])}")
        
        # Test checkpoint export
        checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, 1)
        if 'error' not in checkpoint_data:
            print(f"   ✅ Checkpoint Export: Success")
        else:
            print(f"   ❌ Checkpoint Export: {checkpoint_data['error']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Working Director Error: {e}")
        return False

def test_fal_integration():
    """Test FAL integration."""
    print("\n🖼️ Testing FAL Integration...")
    
    try:
        import fal_client
        
        # Test FAL client initialization
        fal_key = os.environ.get("FAL_KEY")
        if not fal_key:
            print("   ❌ FAL_KEY not set")
            return False
        
        print("   ✅ FAL Client available")
        print("   ✅ FAL API Key configured")
        
        # Note: We don't actually call FAL API to avoid costs
        # but we verify the integration is ready
        
        return True
        
    except ImportError:
        print("   ❌ FAL Client not installed")
        return False
    except Exception as e:
        print(f"   ❌ FAL Integration Error: {e}")
        return False

def test_api_server():
    """Test the API server."""
    print("\n🌐 Testing API Server...")
    
    base_url = "http://localhost:8000"
    
    # Wait for server to be ready
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("   ✅ API Server is running")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                print(f"   ⏳ Waiting for server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("   ❌ API Server not responding")
                return False
    
    try:
        # Test health endpoint (root endpoint)
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test video plan creation
        test_script = {
            "script_text": "EXT. CYBERPUNK CITY - NIGHT\nJack walks through neon-lit streets."
        }
        
        response = requests.post(
            f"{base_url}/api/generate-plan",
            json=test_script,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Video Plan API: {data.get('project_title', 'Success')}")
        else:
            print(f"   ❌ Video Plan API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ API Server Error: {e}")
        return False

def main():
    """Run all system tests."""
    print("🧪 FIBO Video Director - Complete System Test")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Strands Agents", test_strands_agents),
        ("Working Director", test_working_director),
        ("FAL Integration", test_fal_integration),
        ("API Server", test_api_server),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
        print("🚀 FIBO Video Director is ready for production!")
    else:
        print("⚠️  Some components need attention")
    
    return passed == total

if __name__ == "__main__":
    main()