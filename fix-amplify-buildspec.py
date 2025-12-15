#!/usr/bin/env python3
"""
Fix Amplify buildspec with proper YAML formatting
"""

import boto3

# Configuration
AMPLIFY_APP_ID = "dukb992fk9a33"

def fix_buildspec():
    """Fix the Amplify buildspec with proper YAML formatting."""
    print("🔧 Fixing Amplify buildspec...")
    
    amplify_client = boto3.client('amplify', region_name='us-east-1')
    
    # Properly formatted buildspec without special characters
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
    print("🎬 FIBO Video Director - Fix Amplify Buildspec")
    print("=" * 50)
    
    success = fix_buildspec()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Buildspec Fixed!")
        print("📡 Frontend URL: https://main.dukb992fk9a33.amplifyapp.com/")
        print("\n📋 Next Steps:")
        print("1. Wait for deployment to complete (~5 minutes)")
        print("2. Test the frontend URL")
        print("3. Verify API integration")
    else:
        print("❌ Failed to fix buildspec")

if __name__ == "__main__":
    main()