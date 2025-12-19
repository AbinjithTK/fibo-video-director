#!/usr/bin/env python3
"""
Deployment Verification Script
Tests the deployed backend and frontend integration
"""

import requests
import json
import sys
from urllib.parse import urljoin

def test_backend(backend_url):
    """Test backend endpoints."""
    print(f"🔍 Testing backend: {backend_url}")
    
    tests = [
        ("/health", "Health check"),
        ("/", "Root endpoint"),
        ("/api/director-mode", "Director mode"),
        ("/api/cache-stats", "Cache stats"),
    ]
    
    results = []
    
    for endpoint, description in tests:
        try:
            url = urljoin(backend_url, endpoint)
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                results.append(True)
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: {str(e)}")
            results.append(False)
    
    return all(results)

def test_cors(backend_url, frontend_url):
    """Test CORS configuration."""
    print(f"🔍 Testing CORS from {frontend_url} to {backend_url}")
    
    try:
        headers = {
            'Origin': frontend_url,
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options(
            urljoin(backend_url, '/api/generate-plan'),
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print("✅ CORS: OK")
            return True
        else:
            print(f"❌ CORS: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS: {str(e)}")
        return False

def test_api_integration(backend_url):
    """Test API integration with a simple request."""
    print("🔍 Testing API integration")
    
    try:
        url = urljoin(backend_url, '/api/generate-plan')
        data = {
            "script_text": "Test script for deployment verification"
        }
        
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'project_id' in result:
                print("✅ API Integration: OK")
                return True
            else:
                print("❌ API Integration: Invalid response format")
                return False
        else:
            print(f"❌ API Integration: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Integration: {str(e)}")
        return False

def main():
    """Main verification function."""
    print("🚀 FIBO Video Director - Deployment Verification")
    print("=" * 60)
    
    # Get URLs from user
    backend_url = input("Enter your App Runner backend URL: ").strip()
    frontend_url = input("Enter your Amplify frontend URL: ").strip()
    
    if not backend_url or not frontend_url:
        print("❌ Both URLs are required")
        sys.exit(1)
    
    # Ensure URLs have proper format
    if not backend_url.startswith('http'):
        backend_url = f"https://{backend_url}"
    if not frontend_url.startswith('http'):
        frontend_url = f"https://{frontend_url}"
    
    print(f"\n🔧 Configuration:")
    print(f"Backend: {backend_url}")
    print(f"Frontend: {frontend_url}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_backend(backend_url):
        tests_passed += 1
    
    if test_cors(backend_url, frontend_url):
        tests_passed += 1
    
    if test_api_integration(backend_url):
        tests_passed += 1
    
    # Results
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your deployment is working correctly.")
        print("\n✅ Next steps:")
        print("1. Update Amplify environment variables:")
        print(f"   REACT_APP_API_URL = {backend_url}")
        print("2. Test the full application in your browser")
        print("3. Generate a video plan to verify end-to-end functionality")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\n🔧 Troubleshooting:")
        print("1. Verify App Runner service is running")
        print("2. Check environment variables in App Runner")
        print("3. Review CORS configuration")
        print("4. Check CloudWatch logs for errors")

if __name__ == "__main__":
    main()