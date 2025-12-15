#!/usr/bin/env python3
"""
Final fix for Amplify buildspec - remove redundant cd commands
"""

import boto3

# Configuration
AMPLIFY_APP_ID = "dukb992fk9a33"

def fix_buildspec_final():
    """Fix the Amplify buildspec by removing redundant cd commands."""
    print("🔧 Final fix for Amplify buildspec...")
    
    amplify_client = boto3.client('amplify', region_name='us-east-1')
    
    # Corrected buildspec - the build runs from root, so we need cd commands
    # But we need to be consistent about it
    buildspec = """version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
        - echo "Building FIBO Video Director Frontend"
        - echo "Backend URL will be set via environment variables"
    build:
      commands:
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
        # Update the app buildspec
        response = amplify_client.update_app(
            appId=AMPLIFY_APP_ID,
            buildSpec=buildspec
        )
        
        print("✅ Buildspec updated successfully")
        
        # Start a new deployment
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
        print(f"❌ Failed to fix buildspec: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Final Amplify Fix")
    print("=" * 50)
    
    success = fix_buildspec_final()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Final Buildspec Fix Applied!")
        print("📡 Frontend URL: https://main.dukb992fk9a33.amplifyapp.com/")
        print("\n📋 Next Steps:")
        print("1. Wait for deployment to complete (~5 minutes)")
        print("2. Test the frontend URL")
        print("3. Verify full integration")
    else:
        print("❌ Failed to apply final fix")

if __name__ == "__main__":
    main()