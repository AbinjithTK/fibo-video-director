#!/usr/bin/env python3
"""
Set Lambda environment variables for FIBO Video Director
"""

import boto3

# Configuration
LAMBDA_FUNCTION_NAME = "fibo-video-director"

def set_environment_variables():
    """Set Lambda environment variables."""
    print("🔧 Setting Lambda environment variables...")
    
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Set the environment variables
    # You can replace these with your actual API keys
    env_vars = {
        'GOOGLE_API_KEY': 'AIzaSyBKqJ8QJ8QJ8QJ8QJ8QJ8QJ8QJ8QJ8QJ8Q',  # Replace with your actual key
        'FAL_KEY': 'your-fal-key-here'  # Replace with your actual key
    }
    
    try:
        # Get current function configuration
        response = lambda_client.get_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME
        )
        
        # Update environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        current_env.update(env_vars)
        
        # Update the function
        lambda_client.update_function_configuration(
            FunctionName=LAMBDA_FUNCTION_NAME,
            Environment={'Variables': current_env}
        )
        
        print("✅ Environment variables updated successfully!")
        print("   GOOGLE_API_KEY: Set")
        print("   FAL_KEY: Set")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to update environment variables: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Set Lambda Environment Variables")
    print("=" * 60)
    print("⚠️  IMPORTANT: Edit this script to add your actual API keys!")
    print("   - GOOGLE_API_KEY: Get from https://aistudio.google.com/apikey")
    print("   - FAL_KEY: Get from https://fal.ai/dashboard")
    print()
    
    # For security, don't actually set placeholder keys
    print("❌ This script contains placeholder keys.")
    print("   Please edit set-lambda-env-vars.py with your actual API keys")
    print("   Or use the AWS Console to set them manually:")
    print("   1. Go to AWS Lambda Console")
    print("   2. Find function: fibo-video-director")
    print("   3. Go to Configuration → Environment variables")
    print("   4. Set GOOGLE_API_KEY and FAL_KEY")

if __name__ == "__main__":
    main()