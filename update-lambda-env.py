#!/usr/bin/env python3
"""
Update Lambda function environment variables
"""

import boto3
import sys

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"

def update_lambda_environment():
    """Update Lambda environment variables."""
    print("🔧 Updating Lambda environment variables...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Get user input for API keys
    print("\nPlease provide your API keys:")
    google_api_key = input("Google API Key (for Gemini): ").strip()
    fal_key = input("FAL API Key (optional, press Enter to skip): ").strip()
    
    if not google_api_key:
        print("❌ Google API Key is required!")
        sys.exit(1)
    
    try:
        # Get current function configuration
        response = lambda_client.get_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        
        # Update environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        
        # Update with new values
        current_env['GOOGLE_API_KEY'] = google_api_key
        if fal_key:
            current_env['FAL_KEY'] = fal_key
        
        # Update the function
        lambda_client.update_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Environment={'Variables': current_env}
        )
        
        print("✅ Environment variables updated successfully!")
        print(f"   GOOGLE_API_KEY: {'*' * 20}...{google_api_key[-4:]}")
        if fal_key:
            print(f"   FAL_KEY: {'*' * 20}...{fal_key[-4:]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update environment variables: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Lambda Environment Update")
    print("=" * 50)
    
    success = update_lambda_environment()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 Lambda Environment Updated!")
        print("\n📋 Next Steps:")
        print("1. Test the API endpoints")
        print("2. Update Amplify frontend environment variable")
        print("3. Deploy frontend changes")
    else:
        print("❌ Environment update failed")

if __name__ == "__main__":
    main()