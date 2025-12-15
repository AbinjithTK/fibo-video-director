# FIBO Video Director - AWS Deployment Guide

This guide covers deploying the FIBO Video Director to AWS with:
- **Frontend**: AWS Amplify (React app)
- **Backend**: ECS Fargate with Application Load Balancer
- **Storage**: S3 for frame caching

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured (`aws configure`)
3. Node.js 18+ and npm
4. Python 3.11+
5. Docker installed
6. GitHub account

## Quick Start

### 1. Push to GitHub

```bash
# Initialize git if not already
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - FIBO Video Director"

# Create GitHub repo and push
gh repo create fibo-video-director --public --source=. --push
# OR manually:
git remote add origin https://github.com/YOUR_USERNAME/fibo-video-director.git
git push -u origin main
```

### 2. Deploy Backend (CDK)

```bash
# Install CDK globally
npm install -g aws-cdk

# Navigate to infrastructure
cd infrastructure/cdk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy
cdk deploy
```

After deployment, note the outputs:
- `BackendUrl`: Your API endpoint
- `SecretsArn`: Where to store API keys

### 3. Configure API Keys

```bash
# Update secrets in AWS Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id fibo-video-director/api-keys \
  --secret-string '{"GOOGLE_API_KEY":"your-key","FAL_KEY":"your-key"}'
```

### 4. Deploy Frontend (Amplify)

#### Option A: Amplify Console (Recommended)

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify)
2. Click "New app" → "Host web app"
3. Connect your GitHub repository
4. Select the `main` branch
5. Configure build settings:
   - Build command: `npm run build`
   - Build output directory: `build`
   - Base directory: `frontend`
6. Add environment variable:
   - `REACT_APP_API_URL`: Your backend URL from CDK output
7. Deploy!

#### Option B: Amplify CLI

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize (in frontend directory)
cd frontend
amplify init

# Add hosting
amplify add hosting

# Publish
amplify publish
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AWS Amplify   │────▶│  ALB + Fargate   │────▶│   S3 Bucket     │
│   (Frontend)    │     │   (Backend API)  │     │ (Frame Cache)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │ Secrets Manager  │
                        │ (API Keys)       │
                        └──────────────────┘
```

## Environment Variables

### Backend (ECS)
Set in AWS Secrets Manager:
- `GOOGLE_API_KEY`: Google Gemini API key
- `FAL_KEY`: FAL.ai API key

Auto-configured by CDK:
- `FIBO_S3_BUCKET`: S3 bucket name
- `AWS_DEFAULT_REGION`: AWS region

### Frontend (Amplify)
Set in Amplify Console → Environment Variables:
- `REACT_APP_API_URL`: Backend API URL

## Costs Estimate

| Service | Estimated Monthly Cost |
|---------|----------------------|
| ECS Fargate (1 task) | ~$15-30 |
| ALB | ~$20 |
| S3 (10GB) | ~$0.25 |
| Amplify Hosting | ~$0-5 |
| Secrets Manager | ~$0.40 |
| **Total** | **~$35-55/month** |

## Scaling

The CDK stack includes auto-scaling:
- Min: 1 task
- Max: 4 tasks
- Scale at 70% CPU utilization

To adjust, modify `infrastructure/cdk/stacks/backend_stack.py`.

## Troubleshooting

### Backend not starting
```bash
# Check ECS logs
aws logs tail /ecs/fibo-video-director --follow
```

### API keys not working
```bash
# Verify secrets
aws secretsmanager get-secret-value --secret-id fibo-video-director/api-keys
```

### Frontend can't reach backend
1. Check CORS settings in `api_server.py`
2. Verify `REACT_APP_API_URL` in Amplify
3. Check ALB security group allows inbound traffic

## Cleanup

```bash
# Destroy CDK stack
cd infrastructure/cdk
cdk destroy

# Delete Amplify app (via console or CLI)
amplify delete
```

## AgentCore Deployment (Alternative Backend)

The FIBO Video Director is also deployed as an **AWS Bedrock AgentCore agent** for serverless execution:

### Agent Details
- **Agent ARN**: `arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU`
- **Model**: Gemini 2.5 Flash (via Google API)
- **Region**: us-east-1
- **Status**: ✅ Deployed and Ready

### Usage Examples

```bash
# Test the agent with a simple prompt
agentcore invoke '{"prompt": "Create a video plan for a cyberpunk scene", "api_key": "YOUR_GEMINI_API_KEY"}'

# Process a full movie script
agentcore invoke '{"script_text": "EXT. CYBERPUNK CITY - NIGHT\n\nRain falls on neon-lit streets...", "api_key": "YOUR_GEMINI_API_KEY"}'
```

### Response Format
The agent returns structured JSON with:
- Complete production plan with 8-second checkpoints
- FIBO structured prompts for start/end frames
- Visual style consistency parameters
- Video generation notes

### Integration with Frontend
To use AgentCore instead of ECS backend, update your frontend:

```javascript
// In your React app
const AGENTCORE_ENDPOINT = "arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU"

// Call AgentCore via AWS SDK
const response = await bedrockAgentCore.invoke({
  agentArn: AGENTCORE_ENDPOINT,
  payload: {
    prompt: "Your script here",
    api_key: process.env.REACT_APP_GEMINI_API_KEY
  }
});
```

### Monitoring & Logs
- **CloudWatch Logs**: `/aws/bedrock-agentcore/runtimes/src_main-PQhMz74UaU-DEFAULT`
- **GenAI Dashboard**: [AWS Console](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#gen-ai-observability/agent-core)
- **Status Check**: `agentcore status`

### Benefits of AgentCore
- ✅ **Serverless**: No ECS costs when not in use
- ✅ **Auto-scaling**: Handles traffic spikes automatically  
- ✅ **Managed**: No infrastructure to maintain
- ✅ **Observability**: Built-in monitoring and tracing

## CI/CD with GitHub Actions

The `.github/workflows/deploy.yml` workflow automates deployment.

Required GitHub Secrets:
- `AWS_ROLE_ARN`: IAM role ARN for OIDC authentication
- `AMPLIFY_APP_ID`: Amplify app ID (after initial setup)
- `AMPLIFY_DEPLOY_BUCKET`: S3 bucket for deployment artifacts

### Setting up OIDC for GitHub Actions

```bash
# Create OIDC provider (one-time)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com

# Create IAM role with trust policy for your repo
# See AWS docs for detailed policy
```
