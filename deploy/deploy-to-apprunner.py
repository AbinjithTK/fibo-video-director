#!/usr/bin/env python3
"""
AWS App Runner Deployment Script for FIBO Video Director
Automates the deployment process and configuration
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if we're in the right directory
    if not Path("apprunner.yaml").exists():
        print("❌ apprunner.yaml not found. Please run from project root.")
        return False
    
    # Check if git is configured
    git_status = run_command("git status", "Checking git status")
    if git_status is None:
        print("❌ Git repository not found or not configured")
        return False
    
    # Check if AWS CLI is installed
    aws_check = run_command("aws --version", "Checking AWS CLI")
    if aws_check is None:
        print("❌ AWS CLI not installed. Please install AWS CLI first.")
        return False
    
    print("✅ All prerequisites met")
    return True

def prepare_deployment():
    """Prepare files for deployment."""
    print("📦 Preparing deployment files...")
    
    # Ensure all files are committed
    run_command("git add .", "Adding files to git")
    
    # Check if there are uncommitted changes
    status = run_command("git status --porcelain", "Checking git status")
    if status and status.strip():
        commit_msg = "Deploy: Production configuration for AWS App Runner"
        run_command(f'git commit -m "{commit_msg}"', "Committing changes")
    
    # Push to GitHub
    run_command("git push origin main", "Pushing to GitHub")
    
    print("✅ Deployment files prepared")

def get_deployment_info():
    """Get deployment configuration from user."""
    print("\n🔧 Deployment Configuration")
    print("=" * 50)
    
    config = {}
    
    # Get API keys
    config['google_api_key'] = input("Enter Google API Key: ").strip()
    config['fal_api_key'] = input("Enter FAL API Key: ").strip()
    
    # Get Amplify URL
    config['amplify_url'] = input("Enter your Amplify frontend URL: ").strip()
    
    # Service configuration
    config['service_name'] = input("Enter App Runner service name [fibo-video-director-api]: ").strip() or "fibo-video-director-api"
    config['region'] = input("Enter AWS region [us-east-1]: ").strip() or "us-east-1"
    
    return config

def create_apprunner_service(config):
    """Create AWS App Runner service using AWS CLI."""
    print(f"🚀 Creating App Runner service: {config['service_name']}")
    
    # Create service configuration
    service_config = {
        "ServiceName": config['service_name'],
        "SourceConfiguration": {
            "ImageRepository": {
                "ImageIdentifier": "public.ecr.aws/docker/library/python:3.10",
                "ImageConfiguration": {
                    "Port": "8000",
                    "RuntimeEnvironmentVariables": {
                        "GOOGLE_API_KEY": config['google_api_key'],
                        "FAL_KEY": config['fal_api_key'],
                        "ENVIRONMENT": "production",
                        "FRONTEND_URL": config['amplify_url'],
                        "PORT": "8000"
                    }
                },
                "ImageRepositoryType": "ECR_PUBLIC"
            },
            "AutoDeploymentsEnabled": True
        },
        "InstanceConfiguration": {
            "Cpu": "1 vCPU",
            "Memory": "2 GB"
        },
        "HealthCheckConfiguration": {
            "Protocol": "HTTP",
            "Path": "/health",
            "Interval": 10,
            "Timeout": 5,
            "HealthyThreshold": 1,
            "UnhealthyThreshold": 5
        }
    }
    
    # Save config to file
    config_file = "apprunner-config.json"
    with open(config_file, 'w') as f:
        json.dump(service_config, f, indent=2)
    
    # Create service
    create_cmd = f"aws apprunner create-service --cli-input-json file://{config_file} --region {config['region']}"
    result = run_command(create_cmd, "Creating App Runner service")
    
    # Clean up config file
    os.remove(config_file)
    
    if result:
        print("✅ App Runner service created successfully!")
        return True
    else:
        print("❌ Failed to create App Runner service")
        return False

def display_next_steps(config):
    """Display next steps for the user."""
    print("\n🎉 Deployment Initiated!")
    print("=" * 50)
    print(f"Service Name: {config['service_name']}")
    print(f"Region: {config['region']}")
    print("\n📋 Next Steps:")
    print("1. Go to AWS Console → App Runner")
    print(f"2. Find your service: {config['service_name']}")
    print("3. Wait for deployment to complete (5-10 minutes)")
    print("4. Copy the service URL when ready")
    print("5. Update Amplify environment variables:")
    print(f"   - REACT_APP_API_URL = <your-apprunner-url>")
    print("\n🔗 Useful Links:")
    print(f"- AWS Console: https://console.aws.amazon.com/apprunner/home?region={config['region']}")
    print(f"- Amplify Console: https://console.aws.amazon.com/amplify/")
    
def main():
    """Main deployment function."""
    print("🚀 FIBO Video Director - AWS App Runner Deployment")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    # Prepare deployment
    prepare_deployment()
    
    # Get configuration
    config = get_deployment_info()
    
    # Create service
    if create_apprunner_service(config):
        display_next_steps(config)
    else:
        print("❌ Deployment failed. Please check AWS CLI configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()