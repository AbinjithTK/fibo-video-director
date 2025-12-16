#!/usr/bin/env python3
"""
Optimize Lambda timeout and add better error handling
"""

import boto3

def update_lambda_configuration():
    """Update Lambda configuration for better performance."""
    print("Updating Lambda configuration...")
    
    try:
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        # Update function configuration
        response = lambda_client.update_function_configuration(
            FunctionName='fibo-video-director',
            Timeout=120,  # 2 minutes timeout
            MemorySize=1024,  # 1GB memory
            Environment={
                'Variables': {
                    'GOOGLE_API_KEY': 'AIzaSyBDPX59RP7OgVwPn91rRDagWnLwh9-OxPk',
                    'FAL_KEY': '6e7730ad-d8a1-4820-9a12-b0dd603d39de:a91d44688887ea0697c276bed95a63a3'
                }
            }
        )
        
        print(f"Lambda configuration updated:")
        print(f"   Timeout: {response.get('Timeout')} seconds")
        print(f"   Memory: {response.get('MemorySize')} MB")
        print(f"   Environment variables set")
        
        return True
        
    except Exception as e:
        print(f"Failed to update Lambda configuration: {e}")
        return False

def update_api_gateway_timeout():
    """Update API Gateway timeout."""
    print("Checking API Gateway configuration...")
    
    try:
        apigateway = boto3.client('apigateway', region_name='us-east-1')
        
        # List APIs to find our API
        apis = apigateway.get_rest_apis()
        
        for api in apis['items']:
            if 'fibo' in api['name'].lower():
                api_id = api['id']
                print(f"Found API: {api['name']} ({api_id})")
                
                # Get resources
                resources = apigateway.get_resources(restApiId=api_id)
                
                for resource in resources['items']:
                    if resource['path'] == '/api/generate-plan':
                        resource_id = resource['id']
                        
                        # Update integration timeout
                        try:
                            apigateway.update_integration(
                                restApiId=api_id,
                                resourceId=resource_id,
                                httpMethod='POST',
                                patchOps=[
                                    {
                                        'op': 'replace',
                                        'path': '/timeoutInMillis',
                                        'value': '120000'  # 2 minutes
                                    }
                                ]
                            )
                            print(f"   Updated integration timeout for /api/generate-plan")
                        except Exception as e:
                            print(f"   Could not update integration timeout: {e}")
                
                # Deploy the changes
                try:
                    apigateway.create_deployment(
                        restApiId=api_id,
                        stageName='prod'
                    )
                    print(f"   Deployed changes to prod stage")
                except Exception as e:
                    print(f"   Could not deploy changes: {e}")
                
                break
        
        return True
        
    except Exception as e:
        print(f"Failed to update API Gateway: {e}")
        return False

def test_optimized_lambda():
    """Test the optimized Lambda function."""
    print("Testing optimized Lambda function...")
    
    try:
        import requests
        import time
        
        api_url = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
        
        # Wait for configuration update
        print("   Waiting 10 seconds for configuration update...")
        time.sleep(10)
        
        # Test health check
        print("   Testing health check...")
        response = requests.get(f"{api_url}/", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health check OK")
            print(f"   FIBO Available: {data.get('fibo_available')}")
            print(f"   Google API Configured: {data.get('google_api_configured')}")
        else:
            print(f"   Health check failed: {response.status_code}")
            return False
        
        # Test script processing with shorter script
        print("   Testing script processing with shorter script...")
        test_script = """
        FADE IN:
        
        EXT. FOREST - DAY
        
        A wizard walks through a magical forest.
        He raises his staff and it glows.
        
        FADE OUT.
        """
        
        start_time = time.time()
        response = requests.post(
            f"{api_url}/api/generate-plan",
            json={"script_text": test_script},
            timeout=150  # 2.5 minutes timeout
        )
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('project_title', 'Unknown')
            metadata = data.get('metadata', {})
            agent_system = metadata.get('agent_system', 'Unknown')
            
            print(f"   Script processing successful!")
            print(f"   Processing time: {processing_time:.2f} seconds")
            print(f"   Project title: {title}")
            print(f"   Agent system: {agent_system}")
            
            # Check if it's using real AI processing
            if 'FIBO Video Director' in agent_system:
                print(f"   SUCCESS: Using real FIBO Video Director!")
                return True
            else:
                print(f"   WARNING: Using fallback mode")
                return False
        else:
            print(f"   Script processing failed: {response.status_code}")
            if response.status_code == 504:
                print("   Gateway timeout - Lambda may need more time")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Testing failed: {e}")
        return False

def main():
    """Main function."""
    print("FIBO Video Director - Optimize Lambda Performance")
    print("=" * 60)
    
    # Update Lambda configuration
    if update_lambda_configuration():
        print("\n" + "=" * 60)
        
        # Update API Gateway timeout
        update_api_gateway_timeout()
        
        print("\n" + "=" * 60)
        
        # Test the optimized function
        if test_optimized_lambda():
            print("\nSUCCESS: Lambda is now working with optimized configuration!")
        else:
            print("\nWARNING: Lambda may still have performance issues.")
            print("The function is deployed but may need further optimization.")
    else:
        print("\nFAILED: Could not update Lambda configuration.")

if __name__ == "__main__":
    main()