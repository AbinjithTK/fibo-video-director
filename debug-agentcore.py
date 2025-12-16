#!/usr/bin/env python3
"""
Debug AgentCore integration
"""

import boto3
import json
from datetime import datetime

# Configuration
AGENTCORE_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU"

def test_agentcore_direct():
    """Test AgentCore integration directly."""
    print("🔧 Testing AgentCore integration...")
    
    try:
        # Try different client approaches
        print("   📡 Testing bedrock-agent-runtime client...")
        
        client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # Test script
        test_script = "A young woman walks through a city street."
        
        input_message = f"""Please analyze this movie script and create a FIBO video production plan:

Script:
{test_script}

Please provide a structured video production plan with checkpoints, visual style, and FIBO prompts for each scene."""
        
        print(f"   🤖 Calling AgentCore: {AGENTCORE_AGENT_ARN}")
        
        # Try the invoke_agent call
        response = client.invoke_agent(
            agentId=AGENTCORE_AGENT_ARN,
            agentAliasId='TSTALIASID',
            sessionId=f"debug_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            inputText=input_message
        )
        
        print("   ✅ AgentCore call successful!")
        print(f"   📄 Response keys: {list(response.keys())}")
        
        # Process response
        if 'completion' in response:
            completion = response['completion']
            print(f"   📝 Completion type: {type(completion)}")
            
            if hasattr(completion, 'read'):
                # It's a stream
                response_text = ""
                for event in completion:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            response_text += chunk['bytes'].decode('utf-8')
                
                print(f"   📄 Response length: {len(response_text)}")
                print(f"   📄 Response preview: {response_text[:200]}...")
                
                return True
            else:
                print(f"   📄 Direct completion: {completion}")
                return True
        else:
            print(f"   ⚠️ No completion in response: {response}")
            return False
            
    except Exception as e:
        print(f"   ❌ AgentCore test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bedrock_runtime():
    """Test if we can access Bedrock runtime at all."""
    print("\n🔧 Testing Bedrock runtime access...")
    
    try:
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Try to list available models (this should work if we have access)
        # Note: This might fail if we don't have permissions, but it tests connectivity
        print("   📡 Testing Bedrock runtime connectivity...")
        
        # Try a simple invoke with Claude (if available)
        response = client.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 100,
                "messages": [
                    {"role": "user", "content": "Hello, can you respond with 'AgentCore test successful'?"}
                ]
            })
        )
        
        result = json.loads(response['body'].read())
        print(f"   ✅ Bedrock runtime working: {result.get('content', [{}])[0].get('text', 'No text')}")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Bedrock runtime test: {e}")
        return False

def main():
    """Main debug function."""
    print("🎬 FIBO Video Director - AgentCore Debug")
    print("=" * 50)
    
    # Test AgentCore
    agentcore_success = test_agentcore_direct()
    
    # Test general Bedrock access
    bedrock_success = test_bedrock_runtime()
    
    print("\n" + "=" * 50)
    print("📊 Debug Results:")
    print(f"   AgentCore: {'✅ WORKING' if agentcore_success else '❌ FAILED'}")
    print(f"   Bedrock Runtime: {'✅ WORKING' if bedrock_success else '❌ FAILED'}")
    
    if not agentcore_success:
        print("\n🔧 Troubleshooting:")
        print("1. Check if AgentCore agent is still deployed")
        print("2. Verify IAM permissions for bedrock-agent-runtime")
        print("3. Check if the agent ARN is correct")
        print("4. Try redeploying the AgentCore agent")

if __name__ == "__main__":
    main()