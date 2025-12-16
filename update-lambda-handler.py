#!/usr/bin/env python3
"""
Update Lambda function with fixed handler that properly initializes Gemini
"""

import boto3
import zipfile
import os
import tempfile
import shutil
from pathlib import Path

def create_lambda_package():
    """Create Lambda deployment package with fixed handler."""
    print("📦 Creating Lambda deployment package...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "package"
        package_dir.mkdir()
        
        # Copy main files
        files_to_copy = [
            "lambda_handler.py",
            "agentcore_client.py", 
            "fal_fibo_integration.py",
            "s3_storage.py",
            "requirements.txt"
        ]
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, package_dir / file_name)
                print(f"   ✅ Copied {file_name}")
            else:
                print(f"   ⚠️ Missing {file_name}")
        
        # Create zip file
        zip_path = Path(temp_dir) / "lambda_package.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
                    print(f"   📁 Added {arcname} to package")
        
        return zip_path.read_bytes()

def update_lambda_function():
    """Update the Lambda function with new code."""
    print("🚀 Updating Lambda function...")
    
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create deployment package
        zip_content = create_lambda_package()
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='fibo-video-director',
            ZipFile=zip_content
        )
        
        print(f"✅ Lambda function updated successfully!")
        print(f"   📊 Code Size: {response.get('CodeSize', 0)} bytes")
        print(f"   🔄 Last Modified: {response.get('LastModified')}")
        print(f"   ⚡ Runtime: {response.get('Runtime')}")
        
        # Wait for update to complete
        print("⏳ Waiting for update to complete...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName='fibo-video-director')
        
        print("✅ Lambda function update completed!")
        return True
        
    except Exception as e:
        print(f"❌ Lambda update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_updated_function():
    """Test the updated Lambda function."""
    print("🧪 Testing updated Lambda function...")
    
    try:
        import requests
        import json
        import time
        
        api_url = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
        
        # Test health check
        print("   🔍 Testing health check...")
        response = requests.get(f"{api_url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check OK")
            print(f"   🤖 AgentCore Available: {data.get('agentcore_available')}")
            print(f"   🔑 Google API Configured: {data.get('google_api_configured')}")
            print(f"   🎯 Active Mode: {data.get('active_mode')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test script processing
        print("   📝 Testing script processing...")
        test_script = """
        FADE IN:
        
        EXT. MOUNTAIN PEAK - SUNRISE
        
        A lone hiker reaches the summit as the sun rises over the horizon.
        The golden light illuminates the vast landscape below.
        
        FADE OUT.
        """
        
        start_time = time.time()
        response = requests.post(
            f"{api_url}/api/generate-plan",
            json={"script_text": test_script},
            timeout=120
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            metadata = data.get('metadata', {})
            agent_system = metadata.get('agent_system', 'Unknown')
            
            print(f"   ✅ Script processing successful!")
            print(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
            print(f"   🎬 Project title: {title}")
            print(f"   🤖 Agent system: {agent_system}")
            
            # Check if it's using real AI processing
            if processing_time >= 3.0 and 'Gemini' in agent_system:
                print(f"   🎉 SUCCESS: Using real Gemini AI processing!")
                return True
            elif processing_time < 2.0:
                print(f"   ⚠️ WARNING: Processing too fast, may be using fallback")
                return False
            else:
                print(f"   ⚠️ WARNING: Agent system is '{agent_system}', expected 'Gemini FIBO Director'")
                return False
        else:
            print(f"   ❌ Script processing failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Testing failed: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Update Lambda Handler")
    print("=" * 60)
    
    # Update Lambda function
    if update_lambda_function():
        print("\n" + "=" * 60)
        
        # Wait a moment for deployment
        print("⏳ Waiting 10 seconds for deployment to stabilize...")
        import time
        time.sleep(10)
        
        # Test the updated function
        if test_updated_function():
            print("\n🎉 SUCCESS: Lambda function updated and working correctly!")
            print("   The function is now using Gemini AI for real script processing.")
        else:
            print("\n⚠️ WARNING: Lambda updated but may still have issues.")
            print("   Check CloudWatch logs for more details.")
    else:
        print("\n❌ FAILED: Could not update Lambda function.")

if __name__ == "__main__":
    main()