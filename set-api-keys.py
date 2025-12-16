#!/usr/bin/env python3
"""
Set the provided API keys in Lambda environment variables
"""

import boto3
import requests
import time

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"
GOOGLE_API_KEY = "AIzaSyBDPX59RP7OgVwPn91rRDagWnLwh9-OxPk"
FAL_API_KEY = "6e7730ad-d8a1-4820-9a12-b0dd603d39de:a91d44688887ea0697c276bed95a63a3"

def set_environment_variables():
    """Set Lambda environment variables with the provided API keys."""
    print("🔧 Setting Lambda environment variables...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Get current function configuration
        response = lambda_client.get_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        
        # Update environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        current_env['GOOGLE_API_KEY'] = GOOGLE_API_KEY
        current_env['FAL_KEY'] = FAL_API_KEY
        
        # Update the function
        lambda_client.update_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Environment={'Variables': current_env}
        )
        
        print("✅ Environment variables updated successfully!")
        print(f"   GOOGLE_API_KEY: {'*' * 20}...{GOOGLE_API_KEY[-4:]}")
        print(f"   FAL_KEY: {'*' * 20}...{FAL_API_KEY[-4:]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update environment variables: {e}")
        return False

def test_after_update():
    """Test the API after updating environment variables."""
    print("\n🧪 Testing API after environment variable update...")
    
    # Wait for Lambda to update
    print("   ⏳ Waiting 15 seconds for Lambda to update...")
    time.sleep(15)
    
    try:
        # Test the health endpoint
        print("   🏥 Testing health endpoint...")
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
        print("\n   🧪 Testing script processing with AgentCore...")
        test_script = """
        FADE IN:
        
        EXT. CITY STREET - DAY
        
        A young professional SARAH walks confidently down a bustling city street. 
        She checks her smartphone while navigating through the crowd.
        
        SARAH stops at a coffee shop and orders her usual morning coffee.
        
        FADE OUT.
        """
        
        response = requests.post(
            "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod/api/generate-plan",
            json={"script_text": test_script},
            timeout=90  # Longer timeout for AgentCore processing
        )
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            checkpoints = data.get('checkpoints', [])
            
            print(f"   ✅ Script processed successfully!")
            print(f"   🎬 Project Title: {title}")
            print(f"   📋 Checkpoints: {len(checkpoints)}")
            print(f"   ⏱️ Duration: {data.get('total_duration_sec', 0)}s")
            
            if 'Fallback' not in title:
                print("   🎉 AgentCore is working properly!")
                return True
            else:
                print("   ⚠️ Still using fallback mode - AgentCore may need more time")
                return False
        else:
            print(f"   ❌ Script processing failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Set API Keys")
    print("=" * 50)
    
    success = set_environment_variables()
    
    if success:
        # Test the update
        test_success = test_after_update()
        
        print("\n" + "=" * 50)
        if test_success:
            print("🎉 API Keys Set Successfully!")
            print("🤖 AgentCore integration is now working!")
        else:
            print("⚠️ API keys set, but AgentCore may need more time to activate")
        
        print("\n📋 Next Steps:")
        print("1. Refresh your frontend: https://main.dukb992fk9a33.amplifyapp.com/")
        print("2. Click 'New Project' to start fresh")
        print("3. Try generating a new video plan with a movie script")
        print("4. You should now see proper project titles and AgentCore processing!")
        
    else:
        print("\n❌ Failed to set API keys")

if __name__ == "__main__":
    main()