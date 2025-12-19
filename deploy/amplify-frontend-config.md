# AWS Amplify Frontend Configuration

## 🔧 Configure Frontend for Production Backend

### Step 1: Update Amplify Environment Variables

1. **Go to AWS Amplify Console**
2. **Select your app**
3. **Go to "Environment variables" in the left sidebar**
4. **Add the following variables:**

```
REACT_APP_API_URL=https://your-apprunner-url.awsapprunner.com
GENERATE_SOURCEMAP=false
```

### Step 2: Update Build Settings (if needed)

In Amplify Console → Build settings, ensure your `amplify.yml` looks like this:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - cd frontend
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: frontend/build
    files:
      - '**/*'
  cache:
    paths:
      - frontend/node_modules/**/*
```

### Step 3: Configure Custom Headers (Optional)

For better security, add custom headers in Amplify:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-XSS-Protection: 1; mode=block
```

### Step 4: Set up Custom Domain (Optional)

1. **In Amplify Console → Domain management**
2. **Add your custom domain**
3. **Configure DNS settings**
4. **Wait for SSL certificate provisioning**

## 🔍 Testing the Connection

### Frontend Tests
1. Open browser developer tools
2. Go to your Amplify URL
3. Try generating a video plan
4. Check Network tab for API calls
5. Verify no CORS errors in Console

### API Tests
Test these endpoints directly:
- `https://your-backend-url.com/health` - Should return health status
- `https://your-backend-url.com/` - Should return API info
- `https://your-backend-url.com/docs` - API documentation (if enabled)

## 🚨 Common Issues & Solutions

### Issue: CORS Errors
**Solution**: Update backend CORS configuration with exact Amplify URL

### Issue: API calls failing
**Solution**: Check environment variable `REACT_APP_API_URL` is set correctly

### Issue: Build failures
**Solution**: Ensure all dependencies are in `package.json`

### Issue: Slow loading
**Solution**: Enable build caching and optimize bundle size

## 📊 Monitoring & Analytics

### Enable Amplify Monitoring
1. Go to Amplify Console → Monitoring
2. Enable performance monitoring
3. Set up custom metrics

### CloudWatch Integration
- Monitor API response times
- Track error rates
- Set up alerts for failures