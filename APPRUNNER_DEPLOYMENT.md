# 🚀 Deploy FIBO Backend to AWS App Runner

## Step-by-Step Deployment (5 minutes)

### 1. Go to AWS App Runner Console
- Open: https://console.aws.amazon.com/apprunner/home?region=us-east-1
- Click **"Create service"**

### 2. Configure Source
- **Source**: Repository
- **Repository type**: GitHub
- **Connect to GitHub**: Connect your GitHub account
- **Repository**: `AbinjithTK/fibo-video-director`
- **Branch**: `main`
- **Automatic deployments**: ✅ Enabled

### 3. Configure Build
- **Configuration file**: Use configuration file
- **Configuration file**: `apprunner.yaml` (already created)

### 4. Configure Service
- **Service name**: `fibo-video-director`
- **Virtual CPU**: 0.25 vCPU
- **Memory**: 0.5 GB

### 5. Set Environment Variables
Click **"Add environment variable"** for each:

```
GOOGLE_API_KEY = your_google_api_key_here
FAL_KEY = your_fal_key_here  
USE_AGENTCORE = true
AWS_DEFAULT_REGION = us-east-1
```

### 6. Create Service
- Click **"Create & deploy"**
- Wait 5-10 minutes for deployment

### 7. Get Your Backend URL
- Once deployed, copy the **Service URL** (looks like: `https://abc123.us-east-1.awsapprunner.com`)

### 8. Update Frontend
- Go to AWS Amplify Console
- Your app → Environment variables
- Set: `REACT_APP_API_URL = https://your-apprunner-url.com`
- Redeploy frontend

## ✅ That's it! Your backend is now running on AWS App Runner

### Benefits:
- ✅ Auto-scales from 0 to handle traffic
- ✅ Automatic deployments from GitHub
- ✅ No server management
- ✅ Pay only for what you use
- ✅ Built-in load balancing and SSL

### Costs:
- ~$5-15/month for light usage
- Scales automatically with traffic

### Monitoring:
- View logs in App Runner console
- CloudWatch metrics included
- Health checks automatic