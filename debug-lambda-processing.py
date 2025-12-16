#!/usr/bin/env python3
"""
Debug Lambda processing to see why it's not using Gemini
"""

import requests
import json
import time

# Configuration
API_URL = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"

def test_lambda_processing():
    """Test Lambda processing step by step."""
    print("🔧 Debugging Lambda processing...")
    
    # Test health check first
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ Status: {data.get('status')}")
        print(f"   🤖 AgentCore Available: {data.get('agentcore_available')}")
        print(f"   🔑 Google API Configured: {data.get('google_api_configured')}")
        print(f"   🎨 FAL Configured: {data.get('fal_configured')}")
        print(f"   🎯 Active Mode: {data.get('active_mode')}")
        
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test script processing with timing
    print("\n2. Testing script processing with timing...")
    test_script = """
    FADE IN:
    
    EXT. CITY STREET - DAY
    
    A young woman SARAH walks down a busy street, checking her phone.
    She stops at a coffee shop and orders a latte.
    
    FADE OUT.
    """
    
    try:
        print("   📝 Sending script to Lambda...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/api/generate-plan",
            json={"script_text": test_script},
            timeout=120  # 2 minutes timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            checkpoints = data.get('checkpoints', [])
            metadata = data.get('metadata', {})
            
            print(f"   ✅ Response received!")
            print(f"   🎬 Project Title: {title}")
            print(f"   📋 Checkpoints: {len(checkpoints)}")
            print(f"   🤖 Agent System: {metadata.get('agent_system', 'Unknown')}")
            print(f"   🔧 Model: {metadata.get('model', 'Unknown')}")
            
            # Check if it's a real response or fallback
            if processing_time < 2.0:
                print(f"   ⚠️ ISSUE: Processing too fast ({processing_time:.2f}s) - likely using cached/fallback response")
                return False
            elif 'Fallback' in title:
                print(f"   ⚠️ ISSUE: Using fallback mode instead of AI processing")
                return False
            else:
                print(f"   ✅ Appears to be real AI processing!")
                return True
                
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Processing test failed: {e}")
        return False

def check_lambda_logs():
    """Check Lambda logs for errors."""
    print("\n3. Checking Lambda configuration...")
    
    try:
        import boto3
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Get function configuration
        response = lambda_client.get_function_configuration(
            FunctionName='fibo-video-director'
        )
        
        env_vars = response.get('Environment', {}).get('Variables', {})
        
        print(f"   📊 Memory: {response.get('MemorySize')}MB")
        print(f"   ⏱️ Timeout: {response.get('Timeout')}s")
        print(f"   🔑 GOOGLE_API_KEY: {'Set' if env_vars.get('GOOGLE_API_KEY') else 'Missing'}")
        print(f"   🎨 FAL_KEY: {'Set' if env_vars.get('FAL_KEY') else 'Missing'}")
        
        # Check if Google API key looks valid
        google_key = env_vars.get('GOOGLE_API_KEY', '')
        if google_key and len(google_key) > 20 and google_key.startswith('AIza'):
            print(f"   ✅ Google API key format looks correct")
        else:
            print(f"   ⚠️ Google API key may be invalid: {google_key[:10]}...")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Lambda config check failed: {e}")
        return False

def main():
    """Main debug function."""
    print("🎬 FIBO Video Director - Debug Lambda Processing")
    print("=" * 60)
    
    # Run all tests
    processing_ok = test_lambda_processing()
    config_ok = check_lambda_logs()
    
    print("\n" + "=" * 60)
    print("📊 Debug Results:")
    print(f"   Processing: {'✅ WORKING' if processing_ok else '❌ ISSUE FOUND'}")
    print(f"   Configuration: {'✅ OK' if config_ok else '❌ ISSUE FOUND'}")
    
    if not processing_ok:
        print("\n🔧 Likely Issues:")
        print("1. Lambda is using fallback/cached responses instead of calling Gemini")
        print("2. Google API key may not be working properly")
        print("3. AgentCore client may not be initialized correctly")
        print("4. Lambda may be hitting an error and falling back")
        
        print("\n💡 Solutions:")
        print("1. Check CloudWatch logs: /aws/lambda/fibo-video-director")
        print("2. Verify Google API key is valid and has quota")
        print("3. Test Gemini API directly")
        print("4. Update Lambda code to add more debugging")
    else:
        print("\n🎉 Lambda processing appears to be working correctly!")

if __name__ == "__main__":
    main()