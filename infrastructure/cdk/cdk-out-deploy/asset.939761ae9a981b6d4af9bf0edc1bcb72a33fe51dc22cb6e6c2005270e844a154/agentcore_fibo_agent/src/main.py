#!/usr/bin/env python3
"""
FIBO Video Director Agent for Amazon Bedrock AgentCore

This agent processes movie scripts and generates FIBO-compatible
video production plans with structured JSON prompts for frame generation.
"""

import os
import json
from typing import Dict, Any

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models.gemini import GeminiModel


# =============================================================================
# TOOLS FOR FIBO VIDEO PRODUCTION
# =============================================================================

@tool
def analyze_script_structure(script_text: str) -> str:
    """Analyze script structure for pacing decisions.
    
    Args:
        script_text: The movie script to analyze
    """
    lines = [l.strip() for l in script_text.split('\n') if l.strip()]
    dialogue_count = sum(1 for l in lines if any(c.isupper() for c in l[:20]) and ':' not in l[:30])
    action_count = len(lines) - dialogue_count
    estimated_seconds = (dialogue_count * 4) + (action_count * 2)
    segments_needed = max(1, (estimated_seconds + 7) // 8)
    
    analysis = {
        "total_lines": len(lines),
        "dialogue_lines": dialogue_count,
        "action_lines": action_count,
        "estimated_duration_sec": estimated_seconds,
        "recommended_segments": segments_needed,
        "pacing_notes": "Dense dialogue" if dialogue_count > action_count else "Action-heavy"
    }
    return json.dumps(analysis, indent=2)


@tool
def split_into_segments(script_text: str, num_segments: int) -> str:
    """Split script into 8-second segments.
    
    Args:
        script_text: The movie script
        num_segments: Number of segments to create
    """
    lines = [l.strip() for l in script_text.split('\n') if l.strip()]
    if num_segments <= 0:
        num_segments = 1
    
    lines_per_segment = max(1, len(lines) // num_segments)
    segments = []
    
    for i in range(num_segments):
        start_idx = i * lines_per_segment
        end_idx = start_idx + lines_per_segment if i < num_segments - 1 else len(lines)
        segment_lines = lines[start_idx:end_idx]
        
        segments.append({
            "segment_id": i + 1,
            "start_time_sec": i * 8,
            "end_time_sec": (i + 1) * 8,
            "content": "\n".join(segment_lines),
            "is_continuation": i > 0
        })
    
    return json.dumps(segments, indent=2)


@tool
def define_visual_style(scene_context: str, mood: str) -> str:
    """Define consistent visual style for the production.
    
    Args:
        scene_context: Description of the scene setting
        mood: Emotional tone of the scene
    """
    context_lower = scene_context.lower()
    
    if "night" in context_lower or "dark" in context_lower:
        lighting = "Low-key lighting with dramatic shadows, rim lighting, neon accents"
    elif "day" in context_lower or "bright" in context_lower:
        lighting = "Natural daylight, soft diffused shadows, warm color temperature"
    elif "cyberpunk" in context_lower or "neon" in context_lower:
        lighting = "Volumetric fog, neon noir, high contrast, colored gels (cyan/magenta)"
    else:
        lighting = "Balanced three-point lighting, natural color temperature"
    
    if "warm" in mood.lower() or "happy" in mood.lower():
        palette = "Warm tones, golden highlights, saturated colors"
    elif "cold" in mood.lower() or "tense" in mood.lower():
        palette = "Cool tones, desaturated, teal and orange contrast"
    else:
        palette = "Natural, balanced color palette with cinematic grading"
    
    style = {
        "lighting_style": lighting,
        "color_palette": palette,
        "camera_style": "50mm lens, f/2.8, cinematic depth of field",
        "environment_theme": scene_context[:200],
        "artistic_direction": f"{mood} mood, photorealistic, high production value",
        "film_stock": "Digital cinema, slight grain, high dynamic range"
    }
    return json.dumps(style, indent=2)


@tool
def create_fibo_frame_prompt(
    frame_type: str,
    scene_description: str,
    visual_style: str,
    objects_description: str
) -> str:
    """Create detailed FIBO structured JSON prompt for a frame.
    
    Args:
        frame_type: Either 'start' or 'end'
        scene_description: What's happening in this frame
        visual_style: JSON string of visual style parameters
        objects_description: Description of objects/characters in frame
    """
    try:
        style = json.loads(visual_style) if isinstance(visual_style, str) else visual_style
    except json.JSONDecodeError:
        style = {"lighting_style": "Cinematic", "color_palette": "Natural"}
    
    fibo_prompt = {
        "short_description": f"{frame_type.title()} frame: {scene_description[:150]}",
        "objects": [
            {
                "description": objects_description[:200],
                "location": "Center frame, rule of thirds positioning",
                "relationship": "Primary subject of the scene",
                "relative_size": "Prominent, appropriate to shot type",
                "shape_and_color": "Natural, realistic appearance",
                "texture": "Photorealistic surface details, high resolution",
                "appearance_details": "Cinematic quality, detailed rendering",
                "pose": "Natural, contextually appropriate positioning",
                "expression": "Emotionally appropriate to scene context",
                "orientation": "Facing camera or contextually relevant direction"
            }
        ],
        "background_setting": scene_description,
        "lighting": style.get("lighting_style", "Cinematic three-point lighting"),
        "aesthetics": {
            "composition": "Balanced, rule of thirds, cinematic framing",
            "color_scheme": style.get("color_palette", "Natural, harmonious"),
            "mood_atmosphere": style.get("artistic_direction", "Cinematic mood")
        },
        "photographic_characteristics": {
            "depth_of_field": "Cinematic shallow depth, subject in focus",
            "camera_angle": "Eye-level, professional framing",
            "lens_focal_length": style.get("camera_style", "50mm equivalent")
        },
        "style_medium": "Photorealistic, cinematic, high production value"
    }
    return json.dumps(fibo_prompt, indent=2)


# =============================================================================
# FIBO DIRECTOR AGENT
# =============================================================================

FIBO_DIRECTOR_PROMPT = """You are the FIBO Video Director Agent - an AI specialist for converting movie scripts into FIBO-native video production plans.

## YOUR MISSION
Transform movie scripts into checkpoint-based video segments where each checkpoint generates consistent FIBO structured JSON prompts for frame generation.

## CORE PRINCIPLES
1. **8-Second Rule**: Break scripts into 8-second video segments (checkpoints)
2. **FIBO Consistency**: Create detailed structured JSON prompts that maintain visual consistency
3. **Checkpoint System**: Each segment is a selectable checkpoint for frame generation
4. **Style Consistency**: Establish and maintain visual style across all segments

## AVAILABLE TOOLS
- analyze_script_structure: Analyze script pacing and structure
- split_into_segments: Break script into 8-second segments
- define_visual_style: Create consistent visual parameters
- create_fibo_frame_prompt: Generate FIBO structured prompts

## WORKFLOW
1. Use analyze_script_structure to understand the script
2. Use split_into_segments to create checkpoints
3. Use define_visual_style to establish consistent visuals
4. Use create_fibo_frame_prompt for each segment's start and end frames

Always return a complete production plan with all checkpoints and FIBO prompts.

IMPORTANT: When processing script_text, use the tools systematically and return structured JSON output with complete FIBO prompts for each checkpoint."""


def create_fibo_agent(api_key: str):
    """Create the FIBO Director agent using Gemini."""
    model = GeminiModel(
        client_args={"api_key": api_key},
        model_id="gemini-2.5-flash",
        params={"temperature": 0.3}
    )
    
    return Agent(
        model=model,
        tools=[
            analyze_script_structure,
            split_into_segments,
            define_visual_style,
            create_fibo_frame_prompt
        ],
        system_prompt=FIBO_DIRECTOR_PROMPT
    )


# =============================================================================
# AGENTCORE APPLICATION
# =============================================================================

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
    """AgentCore entrypoint for FIBO Video Director.
    
    Args:
        payload: Request payload containing:
            - prompt: User message or script text
            - script_text: (optional) Movie script to process
            
    Returns:
        Response with production plan or agent response
    """
    try:
        # Get the prompt/script from payload
        prompt = payload.get("prompt", "")
        script_text = payload.get("script_text", "")
        
        # Get API key from environment or payload
        api_key = os.environ.get("GOOGLE_API_KEY") or payload.get("api_key")
        
        if not api_key:
            return {
                "status": "error",
                "message": "GOOGLE_API_KEY not configured. Please provide api_key in payload or set GOOGLE_API_KEY environment variable."
            }
        
        if not prompt and not script_text:
            return {
                "status": "error",
                "message": "No prompt or script_text provided"
            }
        
        # Create the agent
        agent = create_fibo_agent(api_key)
        
        # If script_text is provided, process it as a video plan
        if script_text:
            full_prompt = f"""Create a complete FIBO video production plan for this script:

{script_text}

Use the available tools to:
1. Analyze the script structure
2. Split into 8-second segments
3. Define visual style
4. Create FIBO prompts for each segment

Return a complete JSON production plan."""
        else:
            full_prompt = prompt
        
        # Run the agent
        response = agent(full_prompt)
        
        return {
            "status": "success",
            "response": str(response)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    # For local testing
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
