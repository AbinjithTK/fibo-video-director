#!/usr/bin/env python3
"""
Test Frontend-Backend Communication
"""

import requests
import json
import time

def test_frontend_backend():
    """Test the frontend-backend communication."""
    print("🔗 Testing Frontend-Backend Communication")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:3000"
    
    # Test 1: Backend Health
    print("1. Testing Backend Health...")
    try:
        response = requests.get(f"{backend_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend healthy: {data.get('message', 'Unknown')}")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        return False
    
    # Test 2: CORS Headers
    print("2. Testing CORS Headers...")
    try:
        response = requests.options(f"{backend_url}/api/generate-plan", 
                                  headers={'Origin': 'http://localhost:3000'})
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        print(f"   CORS Headers: {cors_headers}")
        if cors_headers['Access-Control-Allow-Origin'] in ['*', 'http://localhost:3000']:
            print("   ✅ CORS configured correctly")
        else:
            print("   ⚠️  CORS may have issues")
    except Exception as e:
        print(f"   ⚠️  CORS test failed: {e}")
    
    # Test 3: API Endpoint
    print("3. Testing API Endpoint...")
    test_script = """FADE IN:

EXT. TEST LOCATION - DAY

A simple test scene for debugging.

FADE OUT."""
    
    try:
        response = requests.post(
            f"{backend_url}/api/generate-plan",
            json={"script_text": test_script},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API working: {data.get('project_title', 'Unknown')}")
            print(f"   📊 Checkpoints: {len(data.get('checkpoints', []))}")
            
            # Verify structure
            required_fields = ['project_id', 'project_title', 'checkpoints']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print("   ✅ Response structure valid")
                
        else:
            print(f"   ❌ API failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    # Test 4: Frontend Accessibility
    print("4. Testing Frontend...")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend accessible")
            if "FIBO Video Director" in response.text:
                print("   ✅ Frontend content loaded")
            else:
                print("   ⚠️  Frontend content may not be fully loaded")
        else:
            print(f"   ❌ Frontend failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Frontend test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 DEBUGGING INSTRUCTIONS:")
    print("1. Open browser to http://localhost:3000")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Paste a script and click 'Generate Video Plan'")
    print("5. Check console for detailed logs:")
    print("   - Look for '=== SCRIPT SUBMISSION STARTED ==='")
    print("   - Look for '=== API: generateVideoPlan called ==='")
    print("   - Look for '=== PLAN RECEIVED ==='")
    print("   - Look for '=== APP.JS: handlePlanGenerated called ==='")
    print("6. If you see errors, copy them and let me know!")
    
    return True

if __name__ == "__main__":
    test_frontend_backend()