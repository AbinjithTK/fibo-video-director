#!/bin/bash

# Deploy FIBO Video Director to AWS App Runner
# This script creates an App Runner service from your GitHub repository

echo "🚀 Deploying FIBO Video Director to AWS App Runner..."

# Configuration
SERVICE_NAME="fibo-video-director"
GITHUB_REPO="https://github.com/AbinjithTK/fibo-video-director"
BRANCH="main"
REGION="us-east-1"

# Create App Runner service
echo "📦 Creating App Runner service..."

aws apprunner create-service \
  --service-name "$SERVICE_NAME" \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "public.ecr.aws/aws-apprunner/hello-app-runner:latest",
      "ImageConfiguration": {
        "Port": "8000"
      },
      "ImageRepositoryType": "ECR_PUBLIC"
    },
    "CodeRepository": {
      "RepositoryUrl": "'$GITHUB_REPO'",
      "SourceCodeVersion": {
        "Type": "BRANCH",
        "Value": "'$BRANCH'"
      },
      "CodeConfiguration": {
        "ConfigurationSource": "REPOSITORY",
        "CodeConfigurationValues": {
          "Runtime": "PYTHON_3",
          "BuildCommand": "pip install -r requirements.txt",
          "StartCommand": "python start_server.py",
          "RuntimeEnvironmentVariables": {
            "PORT": "8000",
            "USE_AGENTCORE": "true"
          }
        }
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "0.25 vCPU",
    "Memory": "0.5 GB"
  }' \
  --region "$REGION"

echo "✅ App Runner service creation initiated!"
echo "🔗 Check status in AWS Console: https://console.aws.amazon.com/apprunner/home?region=$REGION"
echo ""
echo "📋 Next steps:"
echo "1. Wait for service to be 'Running' (5-10 minutes)"
echo "2. Get the service URL from the console"
echo "3. Set environment variables (GOOGLE_API_KEY, FAL_KEY) in App Runner console"
echo "4. Update your Amplify frontend with the App Runner URL"