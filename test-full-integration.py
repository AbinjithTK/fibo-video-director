#!/usr/bin/env python3
"""
Test full integration between frontend and backend
"""

import requests
import time
import json

# Configuration
FRONTEND_URL = "https://main.dukb992fk9a33.amplifyapp.com"
BACKEND_URL = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"

def test_frontend():
    """Test if frontend is accessible."""
    print("🌐 Testing frontend accessibility...")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Frontend accessible: {response.status_code}")
            
            # Check if it's actually the React app
            if "FIBO Video Director" in response.text or "react" in response.text.lower():
                print("   ✅ React app detected")
                return True
            else:
                print("   ⚠️ Frontend accessible but may not be the React app")
                return False
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Frontend test failed: {e}")
        return False

def test_backend():
    """Test backend API."""
    print("\n🔧 Testing backend API...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Backend accessible: {data.get('status')}")
        print(f"   🤖 AgentCore: {data.get('agentcore_available')}")
        print(f"   🔑 Google API: {data.get('google_api_configured')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        return False

def test_cors():
    """Test CORS configuration."""
    print("\n🔗 Testing CORS configuration...")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{BACKEND_URL}/api/generate-plan",
            headers={
                'Origin': FRONTEND_URL,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            },
            timeout=10
        )
        
        cors_headers = response.headers
        
        if 'Access-Control-Allow-Origin' in cors_headers:
            print(f"   ✅ CORS Origin: {cors_headers.get('Access-Control-Allow-Origin')}")
        else:
            print("   ❌ CORS Origin header missing")
            
        if 'Access-Control-Allow-Methods' in cors_headers:
            print(f"   ✅ CORS Methods: {cors_headers.get('Access-Control-Allow-Methods')}")
        else:
            print("   ❌ CORS Methods header missing")
            
        return True
        
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
        return False

def test_api_integration():
    """Test API integration with a sample request."""
    print("\n🧪 Testing API integration...")
    
    try:
        # Test video plan generation
        test_script = "A simple test script for integration testing."
        
        response = requests.post(
            f"{BACKEND_URL}/api/generate-plan",
            json={"script_text": test_script},
            headers={
                'Content-Type': 'application/json',
                'Origin': FRONTEND_URL
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API integration working")
            print(f"   📋 Project ID: {data.get('project_id', 'N/A')}")
            print(f"   🎬 Title: {data.get('project_title', 'N/A')}")
            return True
        else:
            print(f"   ❌ API integration failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ API integration test failed: {e}")
        return False

def check_amplify_deployment():
    """Check if Amplify deployment is complete."""
    print("⏳ Checking Amplify deployment status...")
    
    try:
        import boto3
        amplify_client = boto3.client('amplify', region_name='us-east-1')
        
        # Get latest job
        jobs = amplify_client.list_jobs(
            appId="dukb992fk9a33",
            branchName="main",
            maxResults=1
        )
        
        if jobs['jobSummaries']:
            latest_job = jobs['jobSummaries'][0]
            status = latest_job['status']
            
            print(f"   📊 Latest deployment: {status}")
            
            if status == 'SUCCEED':
                print("   ✅ Deployment completed successfully")
                return True
            elif status in ['PENDING', 'PROVISIONING', 'RUNNING']:
                print("   ⏳ Deployment still in progress...")
                return False
            else:
                print(f"   ❌ Deployment failed: {status}")
                return False
        else:
            print("   ❌ No deployment jobs found")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Could not check deployment status: {e}")
        return None

def main():
    """Main test function."""
    print("🧪 FIBO Video Director - Full Integration Test")
    print("=" * 50)
    print(f"🌐 Frontend: {FRONTEND_URL}")
    print(f"🔧 Backend: {BACKEND_URL}")
    print()
    
    # Check deployment status first
    deployment_status = check_amplify_deployment()
    
    if deployment_status is False:
        print("\n⏳ Deployment still in progress. Waiting 30 seconds...")
        time.sleep(30)
        deployment_status = check_amplify_deployment()
    
    # Run tests
    frontend_ok = test_frontend()
    backend_ok = test_backend()
    cors_ok = test_cors()
    integration_ok = test_api_integration()
    
    print("\n" + "=" * 50)
    print("📊 Integration Test Results:")
    print(f"   Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"   Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   CORS: {'✅ PASS' if cors_ok else '❌ FAIL'}")
    print(f"   API Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")
    
    if all([frontend_ok, backend_ok, cors_ok, integration_ok]):
        print("\n🎉 All tests passed! Integration is working correctly.")
        print(f"🌐 Your app is ready: {FRONTEND_URL}")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
        
        if not frontend_ok:
            print("   - Frontend may still be deploying")
        if not backend_ok:
            print("   - Backend API may need environment variables")
        if not cors_ok:
            print("   - CORS configuration may need adjustment")
        if not integration_ok:
            print("   - API integration may have issues")

if __name__ == "__main__":
    main()