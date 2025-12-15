# FIBO Video Director - Lambda Deployment Guide

## 🎉 Deployment Complete!

Your FIBO Video Director backend has been successfully deployed to AWS Lambda with API Gateway.

### 📡 API Details

- **API URL**: `https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod`
- **Lambda Function**: `fibo-video-director`
- **Region**: `us-east-1`
- **AgentCore Integration**: ✅ Enabled

### 🔧 Required Configuration

#### 1. Set Lambda Environment Variables

You need to set your API keys in the Lambda function:

```bash
# Run the environment update script
python update-lambda-env.py
```

Or manually in AWS Console:
1. Go to AWS Lambda Console
2. Find function: `fibo-video-director`
3. Go to Configuration → Environment variables
4. Set:
   - `GOOGLE_API_KEY`: Your Google API key for Gemini
   - `FAL_KEY`: Your FAL API key (optional)

#### 2. Update Amplify Frontend

Update your Amplify app environment variable:

1. Go to AWS Amplify Console
2. Select your app: `fibo-video-director`
3. Go to App settings → Environment variables
4. Update `REACT_APP_API_URL` to:
   ```
   https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod
   ```
5. Redeploy the frontend

### 🧪 Testing the API

Test the health endpoint:
```bash
curl https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod/
```

Expected response:
```json
{
  "message": "FIBO Video Director API - Lambda",
  "status": "running",
  "active_mode": "agentcore",
  "agentcore_available": true,
  "agentcore_enabled": true,
  "fal_configured": true,
  "google_api_configured": true,
  "s3_available": true,
  "agentcore_arn": "arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU",
  "version": "1.0.0-lambda"
}
```

### 📋 Available Endpoints

- `GET /` - Health check
- `POST /api/generate-plan` - Generate video plan from script
- `GET /api/project/{project_id}` - Get project details
- `GET /api/checkpoint/{project_id}/{checkpoint_id}` - Get checkpoint details
- `POST /api/generate-frames` - Generate FIBO frames
- `GET /api/generation-status/{generation_id}` - Check generation status
- `GET /api/director-mode` - Get director mode status
- `POST /api/director-mode` - Set director mode
- `GET /api/cache-stats` - Get cache statistics

### 🔄 Architecture Flow

```
Frontend (Amplify) → API Gateway → Lambda → AgentCore → Gemini 2.5 Flash
                                        ↓
                                   FAL FIBO API
                                        ↓
                                   S3 Storage
```

### 🛠 Troubleshooting

#### Lambda Function Issues
- Check CloudWatch logs: `/aws/lambda/fibo-video-director`
- Verify environment variables are set
- Check IAM permissions

#### API Gateway Issues
- Verify CORS settings
- Check API Gateway logs
- Test individual endpoints

#### AgentCore Issues
- Verify AgentCore agent is deployed: `arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU`
- Check Bedrock permissions
- Monitor AgentCore logs

### 📊 Monitoring

- **CloudWatch Logs**: `/aws/lambda/fibo-video-director`
- **API Gateway Metrics**: Monitor in CloudWatch
- **Lambda Metrics**: Duration, errors, invocations
- **AgentCore Metrics**: Available in Bedrock console

### 🔐 Security

- API Gateway has CORS enabled for all origins
- Lambda function has minimal required permissions
- Environment variables are encrypted at rest
- AgentCore uses IAM roles for authentication

### 💰 Cost Optimization

- Lambda: Pay per request (15-minute timeout)
- API Gateway: Pay per API call
- AgentCore: Pay per agent invocation
- S3: Pay for storage and requests

### 🚀 Next Steps

1. ✅ Lambda function deployed
2. ✅ API Gateway configured
3. ⏳ Set environment variables
4. ⏳ Update Amplify frontend
5. ⏳ Test end-to-end functionality
6. ⏳ Monitor and optimize

### 📞 Support

If you encounter issues:
1. Check CloudWatch logs
2. Verify all environment variables
3. Test API endpoints individually
4. Check AgentCore agent status