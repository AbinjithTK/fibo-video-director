# 🚀 Manual AWS App Runner Deployment Guide

## Step-by-Step Deployment Process

### 1. Prepare Your Repository

First, ensure all changes are committed and pushed:

```bash
git add .
git commit -m "Production deployment configuration"
git push origin main
```

### 2. Create AWS App Runner Service

1. **Open AWS Console** → Search for "App Runner" → Click "Create service"

2. **Source Configuration:**
   - **Source**: Repository
   - **Repository type**: GitHub
   - **Connect to GitHub** (if not already connected)
   - **Repository**: `AbinjithTK/fibo-video-director`
   - **Branch**: `main`
   - **Deployment trigger**: Automatic

3. **Build Configuration:**
   - **Configuration file**: Use configuration file
   - **Configuration file location**: `apprunner.yaml`

4. **Service Configuration:**
   - **Service name**: `fibo-video-director-api`
   - **Virtual CPU**: 1 vCPU
   - **Virtual memory**: 2 GB

5. **Environment Variables** (Click "Add environment variable"):
   ```
   GOOGLE_API_KEY = AIzaSyD_kpeBY3zqKeIl9PRxIVGXCDvFvZtEhnE
   FAL_KEY = 1c62bdff-3766-4b6d-9391-f78aeddc1a20:356a8fc1a9e013fb76ac965ff5bb3a3e
   ENVIRONMENT = production
   FRONTEND_URL = https://main.d2x8j9k4l5m3n7.amplifyapp.com
   PORT = 8000
   ```

6. **Security (Optional):**
   - **Auto scaling**: Min 1, Max 10 instances
   - **Health check**: `/health`

7. **Click "Create & Deploy"**

### 3. Wait for Deployment

- Deployment takes 5-10 minutes
- You'll see the build logs in real-time
- Service URL will be available once deployment completes

### 4. Test Your Backend

Once deployed, test these endpoints:

```bash
# Health check
curl https://your-service-url.awsapprunner.com/health

# API info
curl https://your-service-url.awsapprunner.com/

# Director mode
curl https://your-service-url.awsapprunner.com/api/director-mode
```

### 5. Update Frontend Configuration

1. **Copy your App Runner service URL** (e.g., `https://abc123.us-east-1.awsapprunner.com`)

2. **Go to AWS Amplify Console:**
   - Find your app
   - Go to "Environment variables"
   - Add: `REACT_APP_API_URL` = `https://your-apprunner-url.awsapprunner.com`

3. **Amplify will automatically redeploy** your frontend with the new environment variable

### 6. Update CORS Configuration

If you get CORS errors, update the backend:

1. **Edit `core/production_server.py`:**
   ```python
   ALLOWED_ORIGINS = [
       "https://main.d2x8j9k4l5m3n7.amplifyapp.com",  # Your actual Amplify URL
       "http://localhost:3000",  # Keep for local dev
   ]
   ```

2. **Commit and push:**
   ```bash
   git add core/production_server.py
   git commit -m "Update CORS for production"
   git push origin main
   ```

3. **App Runner will automatically redeploy** (takes 2-3 minutes)

### 7. Test Full Integration

1. **Visit your Amplify frontend URL**
2. **Try generating a video plan**
3. **Check browser console** for any errors
4. **Verify API calls** in Network tab

## 🎯 Expected Results

### Backend (App Runner)
- **URL**: `https://abc123.us-east-1.awsapprunner.com`
- **Health**: Returns `{"status": "healthy"}`
- **Cost**: ~$15-30/month

### Frontend (Amplify)
- **URL**: Your existing Amplify URL
- **API Calls**: Successfully connecting to backend
- **Features**: All functionality working

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures
```
Error: Could not find requirements.txt
```
**Solution**: Ensure `requirements.txt` is in the root directory

#### 2. CORS Errors
```
Access to fetch blocked by CORS policy
```
**Solution**: Update `ALLOWED_ORIGINS` in `core/production_server.py`

#### 3. Environment Variables Not Working
```
KeyError: 'GOOGLE_API_KEY'
```
**Solution**: Double-check environment variables in App Runner console

#### 4. Health Check Failing
```
Health check failed
```
**Solution**: Check App Runner logs for Python errors

### Debug Commands

```bash
# Test backend health
curl https://your-backend-url.awsapprunner.com/health

# Test API endpoint
curl https://your-backend-url.awsapprunner.com/api/director-mode

# Check frontend environment (in browser console)
console.log(process.env.REACT_APP_API_URL)
```

## 📊 Monitoring

### AWS CloudWatch
- **Logs**: Automatic logging enabled
- **Metrics**: CPU, memory, request count
- **Alarms**: Set up for high error rates

### App Runner Console
- **Service overview**: Health, deployments, logs
- **Metrics**: Request volume, response times
- **Logs**: Real-time application logs

## 🎉 Success Checklist

- ✅ Backend deployed and healthy
- ✅ Frontend connecting to backend  
- ✅ All features working in production
- ✅ No CORS errors
- ✅ Images generating and downloadable
- ✅ Video prompts working correctly

## 💰 Cost Optimization

### Current Setup
- **1 vCPU, 2 GB RAM**: ~$15-30/month
- **Auto-scaling**: Scales to 0 when not used
- **Pay per use**: Only pay for active time

### Optimization Tips
1. **Use smaller instance** if performance is adequate
2. **Set up CloudWatch alarms** for cost monitoring
3. **Consider reserved capacity** for consistent usage
4. **Monitor and optimize** API response times

---

**🎬 Your FIBO Video Director is now production-ready!**