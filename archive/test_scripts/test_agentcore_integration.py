#!/usr/bin/env python3
"""
Test script for AgentCore integration
"""

import os
import asyncio
from agentcore_client import create_agentcore_client

async def test_agentcore():
    """Test the AgentCore client integration."""
    
    # Set up environment
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set")
        return
    
    try:
        # Create client
        print("🤖 Creating AgentCore client...")
        client = create_agentcore_client()
        
        # Test script
        test_script = """
        EXT. CYBERPUNK CITY - NIGHT
        
        Rain falls on neon-lit streets. JACK walks through the crowded street.
        
        JACK
        (to his AI assistant)
        Show me the route to the data center.
        
        A holographic path appears in his vision.
        """
        
        print("📝 Processing test script...")
        result = await client.process_script(test_script)
        
        print("✅ AgentCore processing completed!")
        print(f"Project Title: {result.get('project_title', 'N/A')}")
        print(f"Checkpoints: {len(result.get('checkpoints', []))}")
        print(f"Duration: {result.get('total_duration_sec', 0)} seconds")
        
        return result
        
    except Exception as e:
        print(f"❌ AgentCore test failed: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_agentcore())