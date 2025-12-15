#!/usr/bin/env python3
"""
Set up API Gateway for the deployed Lambda function
"""

import boto3
from datetime import datetime

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"
API_GATEWAY_NAME = "fibo-video-director-api"

def setup_api_gateway():
    """Set up API Gateway for Lambda function."""
    print("🌐 Setting up API Gateway...")
    
    apigateway = boto3.client('apigateway', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    sts_client = boto3.client('sts')
    
    # Get account ID and function ARN
    account_id = sts_client.get_caller_identity()['Account']
    function_arn = f"arn:aws:lambda:us-east-1:{account_id}:function:{LAMBDA_FUNCTION_NAME}"
    
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
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function."""
    print("🎬 FIBO Video Director - API Gateway Setup")
    print("=" * 50)
    
    api_url = setup_api_gateway()
    
    if api_url:
        print("\n" + "=" * 50)
        print("🎉 API Gateway Setup Complete!")
        print(f"📡 API URL: {api_url}")
        print("\n📋 Next Steps:")
        print(f"1. Update your Amplify frontend environment variable:")
        print(f"   REACT_APP_API_URL={api_url}")
        print("2. Test the API endpoints")
        print("3. Set environment variables in Lambda console:")
        print("   - GOOGLE_API_KEY: Your Google API key")
        print("   - FAL_KEY: Your FAL API key")
    else:
        print("❌ API Gateway setup failed")

if __name__ == "__main__":
    main()