#!/bin/bash

# Deploy FIBO Backend to AWS Lightsail Containers
# This is the simplest way to deploy to AWS

echo "🚀 Deploying FIBO Backend to AWS Lightsail..."

# Build and push container
aws lightsail create-container-service \
  --service-name fibo-backend \
  --power small \
  --scale 1

# Wait for service to be ready
echo "⏳ Waiting for container service to be ready..."
aws lightsail get-container-services --service-name fibo-backend

# Create deployment
cat > lightsail-deployment.json << EOF
{
  "containers": {
    "fibo-api": {
      "image": ":fibo-backend.latest",
      "command": ["python", "start_server.py"],
      "environment": {
        "PORT": "8000",
        "USE_AGENTCORE": "true"
      },
      "ports": {
        "8000": "HTTP"
      }
    }
  },
  "publicEndpoint": {
    "containerName": "fibo-api",
    "containerPort": 8000,
    "healthCheck": {
      "healthyThreshold": 2,
      "unhealthyThreshold": 2,
      "timeoutSeconds": 5,
      "intervalSeconds": 30,
      "path": "/",
      "successCodes": "200-499"
    }
  }
}
EOF

# Push container image
aws lightsail push-container-image \
  --service-name fibo-backend \
  --label fibo-backend \
  --image fibo-backend:latest

# Deploy
aws lightsail create-container-service-deployment \
  --service-name fibo-backend \
  --cli-input-json file://lightsail-deployment.json

echo "✅ Deployment initiated! Check AWS Lightsail console for status."