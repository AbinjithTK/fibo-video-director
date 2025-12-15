#!/usr/bin/env python3
"""
Complete the integration by updating Amplify and committing changes
"""

import boto3
import subprocess
import sys

# Configuration
API_URL = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
AMPLIFY_APP_ID = "dukb992fk9a33"  # From the Amplify URL

def update_amplify_environment():
    """Update Amplify environment variable."""
    print("🚀 Updating Amplify environment variable...")
    
    amplify_client = boto3.client('amplify', region_name='us-east-1')
    
    try:
        # Update environment variable
        response = amplify_client.update_app(
            appId=AMPLIFY_APP_ID,
            environmentVariables={
                'REACT_APP_API_URL': API_URL
            }
        )
        
        print(f"   ✅ Environment variable updated: REACT_APP_API_URL={API_URL}")
        
        # Trigger a new deployment
        print("   🔄 Triggering new deployment...")
        
        # Get the main branch
        branches = amplify_client.list_branches(appId=AMPLIFY_APP_ID)
        main_branch = None
        for branch in branches['branches']:
            if branch['branchName'] == 'main':
                main_branch = branch
                break
        
        if main_branch:
            # Start a new job
            job_response = amplify_client.start_job(
                appId=AMPLIFY_APP_ID,
                branchName='main',
                jobType='RELEASE'
            )
            
            job_id = job_response['jobSummary']['jobId']
            print(f"   ✅ Deployment started: Job ID {job_id}")
            
            return True
        else:
            print("   ⚠️ Main branch not found, manual deployment needed")
            return False
        
    except Exception as e:
        print(f"   ❌ Failed to update Amplify: {e}")
        return False

def commit_and_push_changes():
    """Commit and push changes to trigger Amplify deployment."""
    print("\n📝 Committing deployment changes...")
    
    try:
        # Add all new files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Commit changes
        commit_message = "Deploy Lambda backend with API Gateway integration"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to main branch
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("   ✅ Changes committed and pushed to GitHub")
        print("   🔄 This will trigger an Amplify deployment")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️ Git operation failed: {e}")
        print("   💡 You may need to commit and push manually")
        return False

def main():
    """Main integration function."""
    print("🎬 FIBO Video Director - Complete Integration")
    print("=" * 50)
    
    # Update Amplify environment
    amplify_success = update_amplify_environment()
    
    # Commit and push changes
    git_success = commit_and_push_changes()
    
    print("\n" + "=" * 50)
    print("🎉 Integration Complete!")
    print(f"📡 Lambda API: {API_URL}")
    print(f"🌐 Frontend: https://main.dukb992fk9a33.amplifyapp.com/")
    
    print("\n📋 Final Steps:")
    print("1. Set Lambda environment variables:")
    print("   python update-lambda-env.py")
    print("2. Wait for Amplify deployment to complete")
    print("3. Test the full application")
    
    print("\n🔧 Manual Steps (if needed):")
    if not amplify_success:
        print("- Update Amplify environment variable manually:")
        print(f"  REACT_APP_API_URL={API_URL}")
    
    if not git_success:
        print("- Commit and push changes manually:")
        print("  git add .")
        print("  git commit -m 'Deploy Lambda backend'")
        print("  git push origin main")
    
    print("\n🧪 Test Commands:")
    print("python test-lambda-api.py  # Test Lambda API")
    print("curl https://main.dukb992fk9a33.amplifyapp.com/  # Test frontend")

if __name__ == "__main__":
    main()