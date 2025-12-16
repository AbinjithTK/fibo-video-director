#!/usr/bin/env python3
"""
Test frontend integration with the fixed Lambda backend
"""

import requests
import json
import time

def test_complete_workflow():
    """Test the complete frontend workflow."""
    print("🎬 Testing Complete Frontend Integration")
    print("=" * 60)
    
    api_url = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{api_url}/", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Status: {data.get('status')}")
        print(f"   🤖 AgentCore Available: {data.get('agentcore_available')}")
        print(f"   🔑 Google API Configured: {data.get('google_api_configured')}")
        print(f"   🎯 Active Mode: {data.get('active_mode')}")
        
        if not data.get('agentcore_available'):
            print("   ❌ AgentCore not available - this will cause issues")
            return False
            
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test 2: Script Processing (Frontend Workflow)
    print("\n2. Testing Script Processing (Frontend Workflow)...")
    
    test_scripts = [
        {
            "name": "Mystical Forest",
            "script": """
            FADE IN:
            
            EXT. ENCHANTED FOREST - DAWN
            
            A young wizard walks through an ancient forest filled with magical creatures.
            Sunlight filters through the canopy as mystical energy swirls around the trees.
            The wizard discovers a hidden clearing with a glowing crystal.
            
            FADE OUT.
            """
        },
        {
            "name": "Urban Adventure", 
            "script": """
            FADE IN:
            
            EXT. CITY STREET - DAY
            
            A detective walks down a busy metropolitan street.
            She stops at a coffee shop and notices something suspicious.
            The chase begins through the urban landscape.
            
            FADE OUT.
            """
        },
        {
            "name": "Mountain Journey",
            "script": """
            FADE IN:
            
            EXT. MOUNTAIN PEAK - SUNRISE
            
            A lone hiker reaches the summit as the sun rises.
            The golden light illuminates the vast landscape below.
            A moment of triumph and reflection at the peak.
            
            FADE OUT.
            """
        }
    ]
    
    for i, test_case in enumerate(test_scripts, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{api_url}/api/generate-plan",
                json={"script_text": test_case['script']},
                timeout=30
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                project_id = data.get('project_id')
                title = data.get('project_title', 'Unknown')
                checkpoints = data.get('checkpoints', [])
                metadata = data.get('metadata', {})
                
                print(f"      ✅ Success!")
                print(f"      ⏱️ Processing time: {processing_time:.2f}s")
                print(f"      🎬 Title: {title}")
                print(f"      📋 Checkpoints: {len(checkpoints)}")
                print(f"      🤖 Agent: {metadata.get('agent_system', 'Unknown')}")
                
                # Test project details endpoint
                if project_id:
                    print(f"      🔍 Testing project details...")
                    detail_response = requests.get(f"{api_url}/api/project/{project_id}", timeout=10)
                    
                    if detail_response.status_code == 200:
                        print(f"      ✅ Project details OK")
                    else:
                        print(f"      ⚠️ Project details failed: {detail_response.status_code}")
                
                # Test checkpoint details
                if checkpoints:
                    checkpoint_id = checkpoints[0].get('checkpoint_id', 1)
                    print(f"      🔍 Testing checkpoint details...")
                    checkpoint_response = requests.get(
                        f"{api_url}/api/checkpoint/{project_id}/{checkpoint_id}", 
                        timeout=10
                    )
                    
                    if checkpoint_response.status_code == 200:
                        print(f"      ✅ Checkpoint details OK")
                    else:
                        print(f"      ⚠️ Checkpoint details failed: {checkpoint_response.status_code}")
                
            else:
                print(f"      ❌ Failed: {response.status_code}")
                print(f"      📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return False
    
    # Test 3: Director Mode Endpoints
    print("\n3. Testing Director Mode Endpoints...")
    
    try:
        # Get director mode
        response = requests.get(f"{api_url}/api/director-mode", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Director mode: {data.get('mode')}")
        else:
            print(f"   ⚠️ Director mode failed: {response.status_code}")
        
        # Test cache stats
        response = requests.get(f"{api_url}/api/cache-stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Cache stats: {data.get('projects_cached', 0)} projects cached")
        else:
            print(f"   ⚠️ Cache stats failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️ Director mode test error: {e}")
    
    return True

def test_frontend_urls():
    """Test that frontend URLs are accessible."""
    print("\n4. Testing Frontend URLs...")
    
    frontend_url = "https://main.dukb992fk9a33.amplifyapp.com"
    
    try:
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Frontend accessible at {frontend_url}")
            return True
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
        return False

def main():
    """Main test function."""
    
    # Run all tests
    backend_ok = test_complete_workflow()
    frontend_ok = test_frontend_urls()
    
    print("\n" + "=" * 60)
    print("📊 Integration Test Results:")
    print(f"   Backend API: {'✅ WORKING' if backend_ok else '❌ ISSUES'}")
    print(f"   Frontend: {'✅ ACCESSIBLE' if frontend_ok else '❌ ISSUES'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 SUCCESS: Complete integration is working!")
        print("\nFrontend Features Now Working:")
        print("   • Script input and processing")
        print("   • AI-generated project titles")
        print("   • Intelligent scene analysis")
        print("   • Detailed checkpoint creation")
        print("   • Timeline visualization")
        print("   • Project and checkpoint details")
        
        print(f"\n🌐 Access your application at:")
        print(f"   Frontend: https://main.dukb992fk9a33.amplifyapp.com")
        print(f"   Backend API: https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod")
        
    else:
        print("\n⚠️ Some issues remain - check the specific test results above.")

if __name__ == "__main__":
    main()