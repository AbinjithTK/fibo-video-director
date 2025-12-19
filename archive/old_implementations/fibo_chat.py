#!/usr/bin/env python3
"""
Interactive FIBO Assistant Chat

Chat with your FIBO assistant agent interactively.
"""

import os
import json
from pathlib import Path
from strands import Agent, tool
from strands_tools import calculator, http_request

# Custom tools for FIBO workflow
@tool
def analyze_json_prompt(json_content: str) -> str:
    """Analyze a FIBO JSON structured prompt and provide insights."""
    try:
        data = json.loads(json_content)
        analysis = ["📋 JSON Prompt Analysis:"]
        
        if "short_description" in data:
            analysis.append(f"  • Description: {data['short_description'][:100]}...")
        if "objects" in data:
            analysis.append(f"  • Objects count: {len(data['objects'])}")
        if "background_setting" in data:
            analysis.append(f"  • Background: {data['background_setting']}")
        if "lighting" in data:
            analysis.append(f"  • Lighting: {data['lighting']}")
        
        total_keys = len(data.keys())
        analysis.append(f"  • Total elements: {total_keys}")
        
        prompt_text = json.dumps(data)
        word_count = len(prompt_text.split())
        analysis.append(f"  • Word count: {word_count}")
        
        if word_count > 500:
            analysis.append("  ✅ Good complexity for FIBO")
        else:
            analysis.append("  ⚠️  Consider adding more detail")
            
        return "\n".join(analysis)
        
    except json.JSONDecodeError:
        return "❌ Invalid JSON format"

@tool
def read_fibo_config() -> str:
    """Read the default FIBO JSON caption configuration."""
    config_path = Path("default_json_caption.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"📄 FIBO Default Config (first 500 chars):\n{content[:500]}..."
        except Exception as e:
            return f"❌ Error reading config: {e}"
    else:
        return "❌ default_json_caption.json not found"

def create_agent():
    """Create the FIBO assistant agent."""
    from strands.models.gemini import GeminiModel
    
    model = GeminiModel(
        client_args={"api_key": os.environ["GOOGLE_API_KEY"]},
        model_id="gemini-2.5-flash"
    )
    
    return Agent(
        model=model,
        tools=[analyze_json_prompt, read_fibo_config, calculator],
        system_prompt="""You are a FIBO AI assistant. FIBO is a JSON-native text-to-image model.

Help users with:
- Creating structured JSON prompts for FIBO
- Analyzing existing prompts
- Understanding FIBO's capabilities
- Optimizing prompts for better results

Keep responses concise and practical. Focus on actionable advice."""
    )

def main():
    """Interactive chat with FIBO assistant."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        return
    
    try:
        print("🤖 Creating FIBO Assistant...")
        agent = create_agent()
        print("✅ FIBO Assistant ready!")
        print("\n💬 Ask me anything about FIBO! (type 'quit' to exit)")
        print("Examples:")
        print("  • 'How do I create a JSON prompt for a sunset scene?'")
        print("  • 'Analyze my current FIBO config'")
        print("  • 'What are FIBO's best practices?'")
        
        while True:
            print("\n" + "="*50)
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
                
            try:
                print("🤖 Assistant: ", end="")
                response = agent(user_input)
                print(response)
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Setup error: {e}")

if __name__ == "__main__":
    main()