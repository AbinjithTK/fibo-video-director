#!/usr/bin/env python3
"""
Deploy FIBO Video Director to AWS Lambda

This script creates a Lambda deployment package and deploys it with API Gateway.
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
import subprocess
from pathlib import Path
import boto3
from datetime import datetime

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"
LAMBDA_RUNTIME = "python3.11"
LAMBDA_TIMEOUT = 900  # 15 minutes
LAMBDA_MEMORY = 1024  # MB
API_GATEWAY_NAME = "fibo-video-director-api"

def create_deployment_package():
    """Create Lambda deployment package."""
    print("📦 Creating Lambda deployment package...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "package"
        package_dir.mkdir()
        
        # Copy core files
        core_files = [
            "lambda_handler.py",
            "agentcore_client.py", 
            "fibo_video_director.py",
            "s3_storage.py",
            "fal_fibo_integration.py"
        ]
        
        print("   📄 Copying core files...")
        for file_name in core_files:
            if Path(file_name).exists():
                shutil.copy2(file_name, package_dir / file_name)
                print(f"      ✅ {file_name}")
            else:
                print(f"      ⚠️ {file_name} not found, skipping")
        
        # Install dependencies
        print("   📚 Installing dependencies...")
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "-r", str(requirements_file),
                "-t", str(package_dir),
                "--no-deps"  # Avoid conflicts
            ], check=True)
            print("      ✅ Dependencies installed")
        
        # Create ZIP file
        zip_path = Path("lambda-deployment.zip")
        print(f"   🗜️ Creating ZIP: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)
        
        print(f"   ✅ Package created: {zip_path} ({zip_path.stat().st_size / 1024 / 1024:.1f} MB)")
        return zip_path

def deploy_lambda_function(zip_path: Path):
    """Deploy Lambda function."""
    print("🚀 Deploying Lambda function...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Read ZIP file
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Try to update existing function
        print(f"   🔄 Updating function: {LAMBDA_FUNCTION_NAME}")
        response = lambda_client.update_function_code(
            FunctionName=LAMBDA_FUNCTION_NAME,
            ZipFile=zip_content
        )
        print(f"   ✅ Function updated: {response['FunctionArn']}")
        
    except lambda_client.exceptions.ResourceNotFoundException:
        # Create new function
        print(f"   🆕 Creating function: {LAMBDA_FUNCTION_NAME}")
        
        # Create execution role if it doesn't exist
        iam_client = boto3.client('iam')
        role_name = f"{LAMBDA_FUNCTION_NAME}-role"
        
        try:
            role_response = iam_client.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"   ✅ Using existing role: {role_arn}")
        except iam_client.exceptions.NoSuchEntityException:
            print(f"   🔐 Creating IAM role: {role_name}")
            
            # Create role
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            role_response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Execution role for {LAMBDA_FUNCTION_NAME}"
            )
            role_arn = role_response['Role']['Arn']
            
            # Attach policies
            policies = [
                "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                "arn:aws:iam::aws:policy/AmazonBedrockFullAccess",
                "arn:aws:iam::aws:policy/AmazonS3FullAccess"
            ]
            
            for policy_arn in policies:
                iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
            
            print(f"   ✅ Role created: {role_arn}")
            
            # Wait for role to propagate
            import time
            print("   ⏳ Waiting for role to propagate...")
            time.sleep(10)
        
        # Create Lambda function
        response = lambda_client.create_function(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Runtime=LAMBDA_RUNTIME,
            Role=role_arn,
            Handler="lambda_handler.lambda_handler",
            Code={'ZipFile': zip_content},
            Description="FIBO Video Director API",
            Timeout=LAMBDA_TIMEOUT,
            MemorySize=LAMBDA_MEMORY,
            Environment={
                'Variables': {
                    'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY', 'PLACEHOLDER_SET_IN_CONSOLE'),
                    'FAL_KEY': os.environ.get('FAL_KEY', 'PLACEHOLDER_SET_IN_CONSOLE')
                }
            }
        )
        print(f"   ✅ Function created: {response['FunctionArn']}")
    
    return response['FunctionArn']

def setup_api_gateway(function_arn: str):
    """Set up API Gateway for Lambda function."""
    print("🌐 Setting up API Gateway...")
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        # Create REST API
        print(f"   🔗 Creating API: {API_GATEWAY_NAME}")
        api_response = apigateway.create_rest_api(
            name=API_GATEWAY_NAME,
            description="FIBO Video Director API Gateway",
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api_response['id']
        print(f"   ✅ API created: {api_id}")
        
        # Get root resource
        resources = apigateway.get_resources(restApiId=api_id)
        root_id = next(r['id'] for r in resources['items'] if r['path'] == '/')
        
        # Create proxy resource
        proxy_resource = apigateway.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='{proxy+}'
        )
        proxy_resource_id = proxy_resource['id']
        
        # Create ANY method for proxy
        apigateway.put_method(
            restApiId=api_id,
            resourceId=proxy_resource_id,
            httpMethod='ANY',
            authorizationType='NONE'
        )
        
        # Create root ANY method
        apigateway.put_method(
            restApiId=api_id,
            resourceId=root_id,
            httpMethod='ANY',
            authorizationType='NONE'
        )
        
        # Set up Lambda integration for proxy
        integration_uri = f"arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{function_arn}/invocations"
        
        for resource_id in [root_id, proxy_resource_id]:
            apigateway.put_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=integration_uri
            )
        
        # Add Lambda permission for API Gateway
        try:
            # Get account ID
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            
            lambda_client.add_permission(
                FunctionName=LAMBDA_FUNCTION_NAME,
                StatementId=f"apigateway-{api_id}",
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:us-east-1:{account_id}:{api_id}/*/*"
            )
            print("   ✅ Lambda permission added")
        except lambda_client.exceptions.ResourceConflictException:
            print("   ✅ Lambda permission already exists")
        
        # Deploy API
        deployment = apigateway.create_deployment(
            restApiId=api_id,
            stageName='prod',
            description=f"Deployment at {datetime.now().isoformat()}"
        )
        
        api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
        print(f"   ✅ API deployed: {api_url}")
        
        return api_url
        
    except Exception as e:
        print(f"   ❌ API Gateway setup failed: {e}")
        return None

def main():
    """Main deployment function."""
    print("🎬 FIBO Video Director - Lambda Deployment")
    print("=" * 50)
    
    # Check environment variables (optional for deployment)
    google_api_key = os.environ.get('GOOGLE_API_KEY', '')
    fal_key = os.environ.get('FAL_KEY', '')
    
    if not google_api_key:
        print("⚠️ GOOGLE_API_KEY not set locally - you'll need to set it in Lambda environment")
    else:
        print("✅ GOOGLE_API_KEY found locally")
    
    if not fal_key:
        print("⚠️ FAL_KEY not set locally - you'll need to set it in Lambda environment")
    else:
        print("✅ FAL_KEY found locally")
    
    # Check AWS credentials
    try:
        boto3.client('sts').get_caller_identity()
        print("✅ AWS credentials configured")
    except Exception as e:
        print(f"❌ AWS credentials not configured: {e}")
        sys.exit(1)
    
    try:
        # Create deployment package
        zip_path = create_deployment_package()
        
        # Deploy Lambda function
        function_arn = deploy_lambda_function(zip_path)
        
        # Set up API Gateway
        api_url = setup_api_gateway(function_arn)
        
        # Clean up
        zip_path.unlink()
        print("   🧹 Cleaned up deployment package")
        
        print("\n" + "=" * 50)
        print("🎉 Deployment Complete!")
        print(f"📡 API URL: {api_url}")
        print(f"🔧 Lambda Function: {LAMBDA_FUNCTION_NAME}")
        print("\n📋 Next Steps:")
        print(f"1. Update your Amplify frontend environment variable:")
        print(f"   REACT_APP_API_URL={api_url}")
        print("2. Test the API endpoints")
        print("3. Monitor CloudWatch logs for any issues")
        
        return api_url
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()