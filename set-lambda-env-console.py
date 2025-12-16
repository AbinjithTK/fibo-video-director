#!/usr/bin/env python3
"""
Set Lambda environment variables via AWS Console commands
"""

import boto3

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"

def set_environment_variables():
    """Set Lambda environment variables."""
    print("🔧 Setting Lambda environment variables...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Get user input for API keys
    print("\n🔑 Please provide your API keys:")
    print("   Get Google API key from: https://aistudio.google.com/apikey")
    print("   Get FAL API key from: https://fal.ai/dashboard")
    print()
    
    google_api_key = input("Enter your Google API Key: ").strip()
    fal_key = input("Enter your FAL API Key (optional, press Enter to skip): ").strip()
    
    if not google_api_key:
        print("❌ Google API Key is required!")
        return False
    
    try:
        # Get current function configuration
        response = lambda_client.get_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        
        # Update environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        current_env['GOOGLE_API_KEY'] = google_api_key
        
        if fal_key:
            current_env['FAL_KEY'] = fal_key
        
        # Update the function
        lambda_client.update_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Environment={'Variables': current_env}
        )
        
        print("✅ Environment variables updated successfully!")
        print(f"   GOOGLE_API_KEY: {'*' * 20}...{google_api_key[-4:]}")
        if fal_key:
            print(f"   FAL_KEY: {'*' * 20}...{fal_key[-4:]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update environment variables: {e}")
        return False

def test_after_update():
    """Test the API after updating environment variables."""
    print("\n🧪 Testing API after environment variable update...")
    
    import requests
    import time
    
    # Wait a moment for Lambda to update
    print("   ⏳ Waiting 10 seconds for Lambda to update...")
    time.sleep(10)
    
    try:
        # Test the health endpoint
        response = requests.get(
            "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod/",
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"   ✅ API Status: {data.get('status')}")
        print(f"   🤖 AgentCore: {data.get('agentcore_available')}")
        print(f"   🔑 Google API: {data.get('google_api_configured')}")
        print(f"   🎨 FAL: {data.get('fal_configured')}")
        
        # Test script processing
        print("\n   🧪 Testing script processing...")
        test_script = "A young woman walks through a bustling city street, checking her phone."
        
        response = requests.post(
            "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod/api/generate-plan",
            json={"script_text": test_script},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            
            if 'Fallback' not in title:
                print(f"   ✅ AgentCore working! Title: {title}")
                return True
            else:
                print(f"   ⚠️ Still using fallback mode: {title}")
                return False
        else:
            print(f"   ❌ Script processing failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Set Lambda Environment Variables")
    print("=" * 60)
    
    success = set_environment_variables()
    
    if success:
        # Test the update
        test_success = test_after_update()
        
        print("\n" + "=" * 60)
        if test_success:
            print("🎉 Environment Variables Set Successfully!")
            print("🤖 AgentCore integration is now working!")
        else:
            print("⚠️ Environment variables set, but AgentCore may need more time to activate")
            print("   Try refreshing your frontend in a few minutes")
        
        print("\n📋 Next Steps:")
        print("1. Refresh your frontend: https://main.dukb992fk9a33.amplifyapp.com/")
        print("2. Try generating a new video plan")
        print("3. You should now see proper project titles instead of 'Fallback'")
        
    else:
        print("\n❌ Failed to set environment variables")
        print("\n🔧 Manual Setup:")
        print("1. Go to AWS Lambda Console")
        print("2. Find function: fibo-video-director")
        print("3. Go to Configuration → Environment variables")
        print("4. Add GOOGLE_API_KEY with your Google API key")
        print("5. Optionally add FAL_KEY with your FAL API key")

if __name__ == "__main__":
    main()