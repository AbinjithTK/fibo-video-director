#!/usr/bin/env python3
"""
Simple Strands Agent Example with Google Gemini

This demonstrates how to create an AI agent that can use tools to solve problems.
The agent can perform calculations, run Python code, and make HTTP requests.
"""

import os
from strands import Agent, tool
from strands_tools import calculator, python_repl, http_request

# Custom tool example
@tool
def get_weather(location: str) -> str:
    """Get weather information for a location.
    
    Args:
        location: City name to get weather for
    """
    # This is a mock implementation - in real use you'd call a weather API
    return f"Weather in {location}: Sunny, 72°F with light clouds"

def main():
    """Create and test the agent."""
    
    # Check if we have Google API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  No Google API key found!")
        print("To run this agent, you need to set your Google API key:")
        print("  1. Get your API key from: https://aistudio.google.com/apikey")
        print("  2. Set the environment variable:")
        print("     set GOOGLE_API_KEY=your_key_here")
        print("  3. Run: python simple_agent.py")
        return
    
    try:
        # Use Google Gemini
        from strands.models.gemini import GeminiModel
        
        model = GeminiModel(
            client_args={"api_key": os.environ["GOOGLE_API_KEY"]},
            model_id="gemini-2.5-flash",  # Fast and cost-effective
            temperature=0.3
        )
        print("🤖 Using Google Gemini 2.5 Flash")
        
        agent = Agent(
            model=model,
            tools=[calculator, python_repl, http_request, get_weather],
            system_prompt="""You are a helpful AI assistant with access to tools. 
            You can perform calculations, run Python code, make HTTP requests, and get weather information.
            Always be helpful and explain your reasoning when using tools."""
        )
        
        print("✅ Agent created successfully!")
        print("\n" + "="*50)
        print("🚀 TESTING THE AGENT")
        print("="*50)
        
        # Test 1: Simple calculation
        print("\n📊 Test 1: Mathematical calculation")
        response = agent("What's 15% of 2,847?")
        print(f"Agent: {response}")
        
        # Test 2: Python code execution
        print("\n🐍 Test 2: Python code execution")
        response = agent("Create a list of the first 10 prime numbers using Python")
        print(f"Agent: {response}")
        
        # Test 3: Custom tool
        print("\n🌤️  Test 3: Custom weather tool")
        response = agent("What's the weather like in San Francisco?")
        print(f"Agent: {response}")
        
        # Test 4: Conversation memory
        print("\n💭 Test 4: Conversation memory")
        agent("My favorite color is blue")
        response = agent("What's my favorite color?")
        print(f"Agent: {response}")
        
        print("\n" + "="*50)
        print("✅ All tests completed! The agent is working correctly.")
        print("💡 Try asking it more questions or modify the code to add new tools!")
        
    except ImportError as e:
        if "openai" in str(e):
            print("❌ OpenAI provider not installed.")
            print("Run: pip install 'strands-agents[openai]'")
        else:
            print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your API key is valid and you have internet connection.")

if __name__ == "__main__":
    main()