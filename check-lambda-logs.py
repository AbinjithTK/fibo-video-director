#!/usr/bin/env python3
"""
Check Lambda CloudWatch logs to see why Gemini initialization is failing
"""

import boto3
import json
from datetime import datetime, timedelta

def get_lambda_logs():
    """Get recent Lambda logs from CloudWatch."""
    print("📋 Checking Lambda CloudWatch logs...")
    
    try:
        # Create CloudWatch Logs client
        logs_client = boto3.client('logs', region_name='us-east-1')
        
        # Log group name for Lambda function
        log_group = '/aws/lambda/fibo-video-director'
        
        # Get logs from last 10 minutes
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        # Convert to milliseconds since epoch
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)
        
        print(f"   🔍 Searching logs from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
        
        # Get log events
        response = logs_client.filter_log_events(
            logGroupName=log_group,
            startTime=start_time_ms,
            endTime=end_time_ms,
            limit=100
        )
        
        events = response.get('events', [])
        
        if not events:
            print("   ⚠️ No recent log events found")
            return False
        
        print(f"   📊 Found {len(events)} log events")
        print("\n" + "=" * 80)
        
        # Print relevant log events
        for event in events[-20:]:  # Show last 20 events
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            
            # Highlight important messages
            if any(keyword in message.lower() for keyword in ['error', 'failed', 'exception', 'traceback']):
                print(f"❌ {timestamp.strftime('%H:%M:%S')} | {message}")
            elif any(keyword in message.lower() for keyword in ['gemini', 'agentcore', 'initialized']):
                print(f"🤖 {timestamp.strftime('%H:%M:%S')} | {message}")
            elif 'START RequestId' in message or 'END RequestId' in message:
                print(f"🔄 {timestamp.strftime('%H:%M:%S')} | {message}")
            else:
                print(f"📝 {timestamp.strftime('%H:%M:%S')} | {message}")
        
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"❌ Failed to get logs: {e}")
        return False

def trigger_lambda_request():
    """Trigger a Lambda request to generate fresh logs."""
    print("\n🚀 Triggering Lambda request to generate logs...")
    
    try:
        import requests
        
        api_url = "https://q0ihhqx8d9.execute-api.us-east-1.amazonaws.com/prod"
        
        # Make a health check request
        print("   📡 Making health check request...")
        response = requests.get(f"{api_url}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check successful")
            print(f"   🤖 AgentCore Available: {data.get('agentcore_available')}")
            print(f"   🔑 Google API Configured: {data.get('google_api_configured')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
        
        # Make a script processing request
        print("   📝 Making script processing request...")
        test_script = "A simple test script for debugging."
        
        response = requests.post(
            f"{api_url}/api/generate-plan",
            json={"script_text": test_script},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Script processing successful")
            print(f"   🎬 Title: {data.get('project_title', 'Unknown')}")
        else:
            print(f"   ❌ Script processing failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to trigger request: {e}")
        return False

def main():
    """Main function."""
    print("🎬 FIBO Video Director - Lambda Logs Analysis")
    print("=" * 60)
    
    # Trigger fresh requests
    trigger_lambda_request()
    
    # Wait a moment for logs to appear
    print("\n⏳ Waiting 5 seconds for logs to appear...")
    import time
    time.sleep(5)
    
    # Get and analyze logs
    get_lambda_logs()

if __name__ == "__main__":
    main()