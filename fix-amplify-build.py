#!/usr/bin/env python3
"""
Fix Amplify build configuration for FIBO Video Director
"""

import boto3
import json

# Configuration
AMPLIFY_APP_ID = "dukb992fk9a33"

def fix_amplify_build():
    """Fix the Amplify build configuration."""
    print("🔧 Fixing Amplify build configuration...")
    
    amplify_client = boto3.client('amplify', region_name='us-east-1')
    
    # Correct build spec for React frontend in subdirectory
    correct_build_spec = """version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
        - echo "Building FIBO Video Director Frontend"
        - echo "Backend URL: $REACT_APP_API_URL"
    build:
      commands:
        - cd frontend
        - npm run build
        - echo "Build completed successfully"
  artifacts:
    baseDirectory: frontend/build
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
"""
    
    try:
        # Update the app build spec
        response = amplify_client.update_app(
            appId=AMPLIFY_APP_ID,
            buildSpec=correct_build_spec
        )
        
        print("✅ Build spec updated successfully")
        
        # Trigger a new deployment
        print("🚀 Starting new deployment...")
        job_response = amplify_client.start_job(
            appId=AMPLIFY_APP_ID,
            branchName='main',
            jobType='RELEASE'
        )
        
        job_id = job_response['jobSummary']['jobId']
        print(f"✅ Deployment started: Job ID {job_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix Amplify build: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Fix Amplify Build")
    print("=" * 50)
    
    success = fix_amplify_build()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Amplify Build Fixed!")
        print("📡 Frontend URL: https://main.dukb992fk9a33.amplifyapp.com/")
        print("\n📋 Next Steps:")
        print("1. Wait for deployment to complete (~5 minutes)")
        print("2. Test the frontend URL")
        print("3. Verify API integration")
    else:
        print("❌ Failed to fix Amplify build")

if __name__ == "__main__":
    main()