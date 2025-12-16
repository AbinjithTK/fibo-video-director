#!/usr/bin/env python3
"""
Deploy Lambda function with all dependencies included
"""

import boto3
import zipfile
import os
import tempfile
import shutil
import subprocess
import sys
from pathlib import Path

def install_dependencies(target_dir):
    """Install Python dependencies to target directory."""
    print("📦 Installing Python dependencies...")
    
    # Create requirements for Lambda (minimal set)
    lambda_requirements = [
        "google-generativeai>=0.3.2",
        "boto3>=1.26.0",
        "requests>=2.31.0"
    ]
    
    # Write temporary requirements file
    req_file = target_dir / "requirements_lambda.txt"
    with open(req_file, 'w') as f:
        for req in lambda_requirements:
            f.write(f"{req}\n")
    
    # Install dependencies
    try:
        cmd = [
            sys.executable, "-m", "pip", "install",
            "-r", str(req_file),
            "-t", str(target_dir),
            "--no-deps",  # Don't install sub-dependencies to keep size small
            "--platform", "linux_x86_64",
            "--only-binary=:all:"
        ]
        
        print(f"   🔧 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Dependencies installed successfully")
            return True
        else:
            print(f"   ❌ Dependency installation failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to install dependencies: {e}")
        return False

def create_lambda_package_with_deps():
    """Create Lambda deployment package with all dependencies."""
    print("📦 Creating Lambda deployment package with dependencies...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "package"
        package_dir.mkdir()
        
        # Install dependencies first
        if not install_dependencies(package_dir):
            return None
        
        # Copy main application files
        files_to_copy = [
            "lambda_handler.py",
            "agentcore_client.py", 
            "fal_fibo_integration.py",
            "s3_storage.py"
        ]
        
        for file_name in files_to_copy:
            if os.path.exists(file_name):
                shutil.copy2(file_name, package_dir / file_name)
                print(f"   ✅ Copied {file_name}")
            else:
                print(f"   ⚠️ Missing {file_name}")
        
        # Create zip file
        zip_path = Path(temp_dir) / "lambda_package.zip"
        
        print("   📁 Creating deployment package...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    # Skip unnecessary files
                    if any(skip in str(file_path) for skip in ['.pyc', '__pycache__', '.dist-info']):
                        continue
                    
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        # Check package size
        package_size = zip_path.stat().st_size
        print(f"   📊 Package size: {package_size / 1024 / 1024:.2f} MB")
        
        if package_size > 50 * 1024 * 1024:  # 50MB limit for direct upload
            print(f"   ⚠️ Package too large for direct upload ({package_size / 1024 / 1024:.2f} MB)")
            return None
        
        return zip_path.read_bytes()

def update_lambda_function_with_deps():
    """Update the Lambda function with dependencies."""
    print("🚀 Updating Lambda function with dependencies...")
    
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Create deployment package
        zip_content = create_lambda_package_with_deps()
        
        if not zip_content:
            print("❌ Failed to create deployment package")
            return False
        
        # Update function code
        response = lambda_client.update_function_code(
            FunctionName='fibo-video-director',
            ZipFile=zip_content
        )
        
        print(f"✅ Lambda function updated successfully!")
        print(f"   📊 Code Size: {response.get('CodeSize', 0)} bytes")
        print(f"   🔄 Last Modified: {response.get('LastModified')}")
        
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

def test_lambda_with_deps():
    """Test the Lambda function with dependencies."""
    print("🧪 Testing Lambda function with dependencies...")
    
    try:
        import requests
        import json
        import time
        
        api_url = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
        
        # Wait for cold start
        print("   ⏳ Waiting 15 seconds for cold start...")
        time.sleep(15)
        
        # Test health check
        print("   🔍 Testing health check...")
        response = requests.get(f"{api_url}/", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check OK")
            print(f"   🤖 AgentCore Available: {data.get('agentcore_available')}")
            print(f"   🔑 Google API Configured: {data.get('google_api_configured')}")
            print(f"   🎯 Active Mode: {data.get('active_mode')}")
            
            if data.get('agentcore_available'):
                print("   🎉 SUCCESS: AgentCore is now available!")
            else:
                print("   ⚠️ AgentCore still not available")
                return False
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test script processing with real AI
        print("   📝 Testing AI script processing...")
        test_script = """
        FADE IN:
        
        EXT. ENCHANTED FOREST - DAWN
        
        A mystical forest awakens as morning light filters through ancient trees.
        A young wizard emerges from the shadows, staff glowing with magical energy.
        
        FADE OUT.
        """
        
        start_time = time.time()
        response = requests.post(
            f"{api_url}/api/generate-plan",
            json={"script_text": test_script},
            timeout=120  # Allow time for AI processing
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
            if 'Gemini' in agent_system and processing_time >= 3.0:
                print(f"   🎉 SUCCESS: Using real Gemini AI processing!")
                return True
            elif processing_time < 2.0:
                print(f"   ⚠️ WARNING: Processing too fast, may still be using fallback")
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
    print("🎬 FIBO Video Director - Deploy Lambda with Dependencies")
    print("=" * 70)
    
    # Update Lambda function with dependencies
    if update_lambda_function_with_deps():
        print("\n" + "=" * 70)
        
        # Test the updated function
        if test_lambda_with_deps():
            print("\n🎉 SUCCESS: Lambda function now has Gemini AI working!")
            print("   The function should now process scripts with real AI instead of fallback.")
        else:
            print("\n⚠️ WARNING: Lambda updated but AI processing may still have issues.")
            print("   Check CloudWatch logs for more details.")
    else:
        print("\n❌ FAILED: Could not update Lambda function with dependencies.")

if __name__ == "__main__":
    main()