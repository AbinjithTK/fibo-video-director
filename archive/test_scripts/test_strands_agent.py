#!/usr/bin/env python3
"""
Test Strands Agents with FIBO Video Director
"""

import os
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel

# Load environment variables from .env file
load_dotenv()

@tool
def create_video_segment(scene_description: str, duration_sec: int = 8) -> str:
    """Create a video segment description for FIBO generation.
    
    Args:
        scene_description: Description of what happens in this segment
        duration_sec: Duration of the segment in seconds (default 8)
    """
    return f"Video segment ({duration_sec}s): {scene_description}"

@tool
def analyze_script_pacing(script_text: str) -> str:
    """Analyze script pacing and recommend segment count.
    
    Args:
        script_text: The movie script to analyze
    """
    words = script_text.split()
    estimated_duration = len(words) * 0.5  # Rough estimate: 0.5 seconds per word
    segments_needed = max(1, int(estimated_duration / 8))  # 8-second segments
    
    return f"Script analysis: {len(words)} words, ~{estimated_duration:.1f}s duration, recommend {segments_needed} segments"

def test_strands_agent():
    """Test Strands agent with FIBO tools."""
    print("🧪 Testing Strands Agent with FIBO Tools")
    print("=" * 50)
    
    # Check if Google API key is available
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    try:
        # Create Gemini model
        model = GeminiModel(
            client_args={"api_key": api_key},
            model_id="gemini-2.5-flash",
            params={"temperature": 0.3}
        )
        
        # Create agent with FIBO tools
        agent = Agent(
            model=model,
            tools=[create_video_segment, analyze_script_pacing],
            system_prompt="""You are a FIBO Video Director Agent. You help create video production plans by:
1. Analyzing scripts for pacing and structure
2. Creating video segments with detailed descriptions
3. Providing professional cinematographic guidance

Use the available tools to analyze scripts and create video segments."""
        )
        
        print("✅ Strands Agent created successfully")
        
        # Test script analysis
        test_script = """
        FADE IN:
        
        EXT. CYBERPUNK CITY - NIGHT
        
        Rain falls on neon-lit streets. JACK walks through the crowd.
        
        JACK
        Time to hack the mainframe.
        
        He approaches a glowing terminal.
        """
        
        print("\n📝 Testing script analysis...")
        response = agent(f"Analyze this script and create video segments: {test_script}")
        print(f"Agent Response: {response}")
        
        print("\n✅ Strands Agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Strands agent: {e}")
        return False

if __name__ == "__main__":
    test_strands_agent()