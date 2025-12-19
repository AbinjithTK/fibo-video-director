# AWS App Runner Deployment Guide

## 🚀 Deploy FIBO Backend to AWS App Runner

### Step 1: Prepare Your Repository

1. **Ensure all files are committed to GitHub:**
   ```bash
   git add .
   git commit -m "Add production deployment files"
   git push origin main
   ```

### Step 2: Create AWS App Runner Service

1. **Go to AWS Console → App Runner**
2. **Click "Create service"**
3. **Configure Source:**
   - Source: Repository
   - Repository type: GitHub
   - Connect to GitHub (if not already connected)
   - Repository: `AbinjithTK/fibo-video-director`
   - Branch: `main`
   - Deployment trigger: Automatic

4. **Configure Build:**
   - Configuration file: Use configuration file
   - Configuration file location: `apprunner.yaml`

5. **Configure Service:**
   - Service name: `fibo-video-director-api`
   - Virtual CPU: 1 vCPU
   - Virtual memory: 2 GB
   - Environment variables:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     FAL_KEY=your_fal_api_key_here
     ENVIRONMENT=production
     FRONTEND_URL=https://your-amplify-url.amplifyapp.com
     ```

6. **Configure Security (Optional):**
   - Auto scaling: Min 1, Max 10 instances
   - Health check: `/health`

7. **Click "Create & Deploy"**

### Step 3: Get Your Backend URL

After deployment completes (5-10 minutes):
1. Copy the App Runner service URL (e.g., `https://abc123.us-east-1.awsapprunner.com`)
2. Test the API: `https://your-url.awsapprunner.com/health`

### Step 4: Update Frontend Configuration

1. **In AWS Amplify Console:**
   - Go to your app → Environment variables
   - Add: `REACT_APP_API_URL` = `https://your-apprunner-url.awsapprunner.com`

2. **Redeploy frontend:**
   - Amplify will automatically redeploy when you add environment variables

### Step 5: Test the Connection

1. Visit your Amplify frontend URL
2. Try generating a video plan
3. Check browser console for any CORS errors

## 🔧 Troubleshooting

### CORS Issues
If you get CORS errors, update `core/production_server.py`:
```python
ALLOWED_ORIGINS = [
    "https://your-actual-amplify-url.amplifyapp.com",
    # Add your exact Amplify URL here
]
```

### Environment Variables
Verify in App Runner console that all environment variables are set correctly.

### Health Check
Test the health endpoint: `https://your-url.awsapprunner.com/health`

## 💰 Cost Estimate

AWS App Runner pricing (us-east-1):
- **Build time**: $0.005 per build minute
- **Runtime**: $0.064 per vCPU hour + $0.007 per GB memory hour
- **Estimated monthly cost**: ~$15-30 for light usage

## 🔒 Security Best Practices

1. **Use AWS Secrets Manager** for API keys (advanced)
2. **Enable CloudWatch logs** for monitoring
3. **Set up custom domain** with SSL certificate
4. **Configure WAF** for additional security (optional)