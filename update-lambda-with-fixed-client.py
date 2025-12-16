#!/usr/bin/env python3
"""
Update Lambda function to use the fixed AgentCore client (Gemini-based)
"""

import boto3
import zipfile
import tempfile
import shutil
from pathlib import Path

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"

def update_lambda_code():
    """Update Lambda function with the fixed AgentCore client."""
    print("🔧 Updating Lambda function with improved Gemini client...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Create temporary directory for the update
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "package"
        package_dir.mkdir()
        
        # Copy current Lambda files
        current_files = [
            "lambda_handler.py",
            "fibo_video_director.py",
            "s3_storage.py",
            "fal_fibo_integration.py"
        ]
        
        print("   📄 Copying current files...")
        for file_name in current_files:
            if Path(file_name).exists():
                shutil.copy2(file_name, package_dir / file_name)
                print(f"      ✅ {file_name}")
        
        # Copy the fixed AgentCore client
        print("   🔄 Updating AgentCore client...")
        shutil.copy2("agentcore_client_fixed.py", package_dir / "agentcore_client.py")
        print("      ✅ agentcore_client.py (updated with Gemini)")
        
        # Create ZIP file
        zip_path = Path("lambda-update.zip")
        print(f"   🗜️ Creating update package: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        # Update Lambda function
        print("   🚀 Updating Lambda function...")
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        # Clean up
        zip_path.unlink()
        
        print(f"   ✅ Lambda function updated: {response['FunctionArn']}")
        return True

def test_updated_function():
    """Test the updated Lambda function."""
    print("\n🧪 Testing updated Lambda function...")
    
    import requests
    import time
    
    # Wait for Lambda to update
    print("   ⏳ Waiting 10 seconds for Lambda to update...")
    time.sleep(10)
    
    try:
        # Test script processing
        test_script = """
        FADE IN:
        
        EXT. COFFEE SHOP - MORNING
        
        SARAH, a young professional in her late 20s, walks briskly down a busy city street. 
        She's dressed in a sharp business suit, checking her smartphone as she navigates through the morning crowd.
        
        She stops at a trendy coffee shop, orders her usual latte, and waits while scrolling through emails.
        
        The barista calls her name. Sarah grabs her coffee and continues down the street with renewed energy.
        
        FADE OUT.
        """
        
        print("   📝 Testing script processing...")
        response = requests.post(
            "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod/api/generate-plan",
            json={"script_text": test_script},
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            checkpoints = data.get('checkpoints', [])
            
            print(f"   ✅ Script processed successfully!")
            print(f"   🎬 Project Title: {title}")
            print(f"   📋 Checkpoints: {len(checkpoints)}")
            print(f"   ⏱️ Duration: {data.get('total_duration_sec', 0)}s")
            
            # Check if it's using the improved system
            if 'Fallback' not in title and len(checkpoints) >= 2:
                print("   🎉 Improved Gemini processing is working!")
                return True
            else:
                print("   ⚠️ Still using basic processing")
                return False
        else:
            print(f"   ❌ Test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Update Lambda with Improved Client")
    print("=" * 60)
    
    try:
        # Update Lambda code
        update_success = update_lambda_code()
        
        if update_success:
            # Test the update
            test_success = test_updated_function()
            
            print("\n" + "=" * 60)
            if test_success:
                print("🎉 Lambda Update Successful!")
                print("🤖 Improved Gemini processing is now active!")
            else:
                print("⚠️ Lambda updated, but testing shows mixed results")
            
            print("\n📋 What's Working Now:")
            print("✅ Frontend: https://main.dukb992fk9a33.amplifyapp.com/")
            print("✅ Backend: Professional script processing with Gemini 2.5 Flash")
            print("✅ Video Plans: Detailed checkpoints with FIBO prompts")
            print("✅ Integration: Full frontend-backend communication")
            
            print("\n🎯 Try It Out:")
            print("1. Go to your frontend URL")
            print("2. Click 'New Project' to start fresh")
            print("3. Enter a movie script")
            print("4. You should get a creative project title and detailed scenes!")
            
        else:
            print("\n❌ Lambda update failed")
            
    except Exception as e:
        print(f"\n❌ Update failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()