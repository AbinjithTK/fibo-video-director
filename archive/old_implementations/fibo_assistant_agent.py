#!/usr/bin/env python3
"""
FIBO Assistant Agent

An AI agent that helps with FIBO image generation workflows.
Uses Google Gemini (same as your FIBO project) and provides tools for:
- JSON prompt analysis and optimization
- File operations for FIBO workflows
- Image generation assistance
"""

import os
import json
from pathlib import Path
from strands import Agent, tool
# Import only Windows-compatible tools
from strands_tools import calculator, http_request

# Custom tools for FIBO workflow
@tool
def analyze_json_prompt(json_content: str) -> str:
    """Analyze a FIBO JSON structured prompt and provide insights.
    
    Args:
        json_content: JSON string containing the structured prompt
    """
    try:
        data = json.loads(json_content)
        
        analysis = []
        analysis.append("📋 JSON Prompt Analysis:")
        
        # Check main components
        if "subject" in data:
            analysis.append(f"  • Subject: {data['subject']}")
        if "style" in data:
            analysis.append(f"  • Style: {data['style']}")
        if "lighting" in data:
            analysis.append(f"  • Lighting: {data['lighting']}")
        if "composition" in data:
            analysis.append(f"  • Composition: {data['composition']}")
        if "camera" in data:
            analysis.append(f"  • Camera: {data['camera']}")
        
        # Count total elements
        total_keys = len(data.keys())
        analysis.append(f"  • Total elements: {total_keys}")
        
        # Estimate prompt complexity
        prompt_text = json.dumps(data)
        word_count = len(prompt_text.split())
        analysis.append(f"  • Estimated word count: {word_count}")
        
        if word_count > 500:
            analysis.append("  ✅ Good complexity for FIBO (500+ words)")
        else:
            analysis.append("  ⚠️  Consider adding more detail for better FIBO results")
            
        return "\n".join(analysis)
        
    except json.JSONDecodeError:
        return "❌ Invalid JSON format. Please provide valid JSON content."

@tool
def read_fibo_config() -> str:
    """Read the default FIBO JSON caption configuration.
    
    Returns the content of default_json_caption.json if it exists.
    """
    config_path = Path("default_json_caption.json")
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"📄 FIBO Default Config:\n{content}"
        except Exception as e:
            return f"❌ Error reading config: {e}"
    else:
        return "❌ default_json_caption.json not found in current directory"

@tool
def suggest_fibo_improvements(current_prompt: str) -> str:
    """Suggest improvements for a FIBO prompt based on best practices.
    
    Args:
        current_prompt: The current prompt text or JSON
    """
    suggestions = []
    suggestions.append("💡 FIBO Prompt Improvement Suggestions:")
    
    # Check if it's JSON or text
    try:
        json.loads(current_prompt)
        is_json = True
    except:
        is_json = False
    
    if not is_json:
        suggestions.append("  • Convert to structured JSON format for better control")
        suggestions.append("  • Add specific lighting details (golden hour, studio lighting, etc.)")
        suggestions.append("  • Include camera settings (focal length, aperture, etc.)")
        suggestions.append("  • Specify composition rules (rule of thirds, leading lines, etc.)")
    else:
        suggestions.append("  • JSON format detected ✅")
        data = json.loads(current_prompt)
        
        recommended_keys = ["subject", "style", "lighting", "composition", "camera", "color_palette", "mood", "environment"]
        missing_keys = [key for key in recommended_keys if key not in data]
        
        if missing_keys:
            suggestions.append(f"  • Consider adding: {', '.join(missing_keys)}")
        
        # Check for detail level
        total_text = json.dumps(data)
        if len(total_text.split()) < 300:
            suggestions.append("  • Add more descriptive details (aim for 300+ words)")
    
    suggestions.append("  • Use professional photography terms for better results")
    suggestions.append("  • Consider TeaCache for 3x faster generation")
    
    return "\n".join(suggestions)

@tool
def check_fibo_environment() -> str:
    """Check if FIBO environment is properly set up.
    
    Returns status of FIBO dependencies and configuration.
    """
    status = []
    status.append("🔍 FIBO Environment Check:")
    
    # Check for key files
    key_files = [
        "generate.py",
        "default_json_caption.json", 
        "pyproject.toml",
        "src/fibo_inference/",
        ".env"
    ]
    
    for file_path in key_files:
        if Path(file_path).exists():
            status.append(f"  ✅ {file_path}")
        else:
            status.append(f"  ❌ {file_path} (missing)")
    
    # Check environment variables
    env_vars = ["GOOGLE_API_KEY", "PYTHONPATH"]
    for var in env_vars:
        if os.environ.get(var):
            status.append(f"  ✅ {var} is set")
        else:
            status.append(f"  ⚠️  {var} not set")
    
    return "\n".join(status)

def main():
    """Create and test the FIBO assistant agent."""
    
    # Check if we have Google API key (same as FIBO uses)
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  No Google API key found!")
        print("FIBO uses Google Gemini API. To run this agent:")
        print("  1. Get your API key from: https://aistudio.google.com/apikey")
        print("  2. Set the environment variable:")
        print("     set GOOGLE_API_KEY=your_key_here")
        print("  3. Run: python fibo_assistant_agent.py")
        print("\n💡 This is the same API key your FIBO project uses!")
        return
    
    try:
        # Use Google Gemini (same as FIBO)
        from strands.models.gemini import GeminiModel
        
        model = GeminiModel(
            client_args={"api_key": os.environ["GOOGLE_API_KEY"]},
            model_id="gemini-2.5-flash",  # Same model FIBO uses
            temperature=0.3
        )
        print("🤖 Using Google Gemini 2.5 Flash (same as FIBO)")
        
        agent = Agent(
            model=model,
            tools=[
                analyze_json_prompt,
                read_fibo_config, 
                suggest_fibo_improvements,
                check_fibo_environment,
                calculator,
                http_request
            ],
            system_prompt="""You are a FIBO AI assistant specialized in helping with image generation workflows.

FIBO is a JSON-native text-to-image model that uses structured prompts with detailed descriptions.
You help users:
- Analyze and improve JSON structured prompts
- Understand FIBO's capabilities and best practices  
- Optimize prompts for better image generation results
- Troubleshoot FIBO setup and configuration

Key FIBO features:
- Uses structured JSON prompts (not simple text)
- Supports Generate, Refine, and Inspire modes
- Works with Gemini VLM for prompt expansion
- TeaCache for 3x faster inference
- Professional control over lighting, composition, camera settings

Always provide practical, actionable advice for FIBO workflows."""
        )
        
        print("✅ FIBO Assistant Agent created successfully!")
        print("\n" + "="*60)
        print("🚀 TESTING THE FIBO ASSISTANT")
        print("="*60)
        
        # Test 1: Environment check
        print("\n🔍 Test 1: Checking FIBO environment")
        response = agent("Check if my FIBO environment is set up correctly")
        print(f"Agent: {response}")
        
        # Test 2: Read default config
        print("\n📄 Test 2: Reading FIBO configuration")
        response = agent("Show me the default FIBO JSON configuration")
        print(f"Agent: {response}")
        
        # Test 3: Prompt improvement suggestions
        print("\n💡 Test 3: Prompt improvement suggestions")
        response = agent("I want to generate an image of a cat. How should I structure this for FIBO?")
        print(f"Agent: {response}")
        
        # Test 4: JSON analysis
        print("\n📋 Test 4: JSON prompt analysis")
        sample_json = '{"subject": "a majestic cat", "style": "photorealistic", "lighting": "golden hour"}'
        response = agent(f"Analyze this JSON prompt: {sample_json}")
        print(f"Agent: {response}")
        
        print("\n" + "="*60)
        print("✅ FIBO Assistant is ready!")
        print("💬 Try asking questions like:")
        print("   • 'How do I improve this prompt for FIBO?'")
        print("   • 'What's the best way to structure lighting in JSON?'")
        print("   • 'Analyze my JSON prompt and suggest improvements'")
        print("   • 'Check my FIBO environment setup'")
        
    except ImportError as e:
        print("❌ Gemini provider not installed.")
        print("Run: pip install 'strands-agents[gemini]'")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your GOOGLE_API_KEY is valid and you have internet connection.")

if __name__ == "__main__":
    main()