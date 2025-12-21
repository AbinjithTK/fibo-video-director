#!/usr/bin/env python3
"""
Quick test to verify local setup is working correctly
"""

import requests
import json
import time

def test_backend():
    """Test backend endpoints."""
    print("🔍 Testing Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint: HTTP {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint: {data.get('message', 'OK')}")
            print(f"   Enhanced: {data.get('enhanced_enabled', False)}")
            print(f"   FAL: {data.get('fal_available', False)}")
        else:
            print(f"❌ Root endpoint: HTTP {response.status_code}")
            return False
        
        # Test director mode
        response = requests.get("http://127.0.0.1:8000/api/director-mode", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Director mode: {data.get('mode', 'unknown')}")
        else:
            print(f"❌ Director mode: HTTP {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_api_integration():
    """Test API integration with a simple script."""
    print("\n🔍 Testing API Integration...")
    
    try:
        test_script = """
        FADE IN:
        
        EXT. CITY STREET - DAY
        
        A bustling street with people walking. The sun shines brightly.
        
        JOHN walks down the sidewalk, looking at his phone.
        
        JOHN
        (to himself)
        I need to find that coffee shop.
        
        FADE OUT.
        """
        
        response = requests.post(
            "http://127.0.0.1:8000/api/generate-plan",
            json={"script_text": test_script},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'project_id' in data:
                print("✅ Script processing: OK")
                print(f"   Project ID: {data['project_id']}")
                print(f"   Checkpoints: {len(data.get('checkpoints', []))}")
                return True
            else:
                print("❌ Script processing: Invalid response format")
                return False
        else:
            print(f"❌ Script processing: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API integration failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 FIBO Video Director - Local Setup Test")
    print("=" * 50)
    
    # Test backend
    backend_ok = test_backend()
    
    if not backend_ok:
        print("\n❌ Backend tests failed. Please check:")
        print("   1. Backend is running: python app.py")
        print("   2. Port 8000 is not blocked")
        print("   3. Environment variables are set")
        return
    
    # Test API integration
    api_ok = test_api_integration()
    
    # Results
    print("\n📊 Test Results:")
    print(f"   Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"   API Integration: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if backend_ok and api_ok:
        print("\n🎉 All tests passed! Your local setup is working correctly.")
        print("\n✅ Next steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Paste a movie script")
        print("   3. Click 'Generate Video Plan'")
        print("   4. Watch the multi-agent system work!")
    else:
        print("\n❌ Some tests failed. Please check the setup.")

if __name__ == "__main__":
    main()