#!/usr/bin/env python3
"""
FIBO Video Director System

Specialized AI Director for FIBO-only video generation pipeline.
Converts movie scripts into checkpoint-based video segments with 
consistent FIBO structured JSON prompts for frame generation.
"""

import os
import json
from typing import Dict, List, Any
from strands import Agent
from strands.models.gemini import GeminiModel

# System prompt optimized for FIBO video generation
FIBO_DIRECTOR_PROMPT = """You are the **FIBO Video Director** - an AI specialist for converting movie scripts into FIBO-native video production plans.

## YOUR MISSION
Transform movie scripts into checkpoint-based video segments where each checkpoint generates consistent FIBO structured JSON prompts for frame generation.

## CORE PRINCIPLES
1. **8-Second Rule**: Break scripts into 8-second video segments (checkpoints)
2. **FIBO Consistency**: Create detailed structured JSON prompts that maintain visual consistency
3. **Checkpoint System**: Each segment is a selectable checkpoint for frame generation
4. **Style Consistency**: Establish and maintain visual style across all segments

## WORKFLOW
1. **Script Analysis**: Break script into logical 8-second segments
2. **Style Creation**: Define consistent visual style for the entire production
3. **Checkpoint Generation**: Create detailed FIBO prompts for each segment
4. **Frame Specifications**: Generate start_frame and end_frame structured JSON prompts

## OUTPUT FORMAT
Return ONLY this JSON structure:

{
  "project_title": "String",
  "total_duration_sec": 0,
  "visual_style": {
    "lighting_style": "Consistent lighting approach for all segments",
    "color_palette": "Color scheme that maintains throughout",
    "camera_style": "Camera and lens specifications",
    "environment_theme": "Overall environmental consistency",
    "artistic_direction": "Visual aesthetic and mood"
  },
  "checkpoints": [
    {
      "checkpoint_id": 1,
      "start_time_sec": 0,
      "end_time_sec": 8,
      "duration_sec": 8,
      "scene_description": "What happens in this 8-second segment",
      "visual_consistency_notes": "How this maintains the overall style",
      "fibo_start_frame": {
        "short_description": "Detailed description of opening frame",
        "objects": [
          {
            "description": "Detailed object description",
            "location": "Position in frame",
            "relationship": "Relationship to other objects",
            "relative_size": "Size within frame",
            "shape_and_color": "Visual characteristics",
            "texture": "Surface texture details",
            "appearance_details": "Specific visual features",
            "pose": "Object positioning/posture",
            "expression": "Facial expression if applicable",
            "orientation": "Direction facing"
          }
        ],
        "background_setting": "Detailed background description",
        "lighting": "Specific lighting setup",
        "aesthetics": {
          "composition": "Frame composition rules",
          "color_scheme": "Color palette for this frame",
          "mood_atmosphere": "Emotional tone"
        },
        "photographic_characteristics": {
          "depth_of_field": "Focus characteristics",
          "camera_angle": "Camera positioning",
          "lens_focal_length": "Lens specifications"
        },
        "style_medium": "Visual style approach"
      },
      "fibo_end_frame": {
        "short_description": "Detailed description of closing frame",
        "objects": [
          {
            "description": "How objects have changed from start",
            "location": "New position in frame",
            "relationship": "Updated relationships",
            "relative_size": "Size changes if any",
            "shape_and_color": "Visual characteristics",
            "texture": "Surface texture details", 
            "appearance_details": "Specific visual features",
            "pose": "Final positioning/posture",
            "expression": "Final facial expression if applicable",
            "orientation": "Final direction facing"
          }
        ],
        "background_setting": "Background at segment end",
        "lighting": "Lighting at segment end",
        "aesthetics": {
          "composition": "Final frame composition",
          "color_scheme": "Maintained color palette",
          "mood_atmosphere": "Emotional progression"
        },
        "photographic_characteristics": {
          "depth_of_field": "Final focus characteristics",
          "camera_angle": "Final camera positioning", 
          "lens_focal_length": "Consistent lens specs"
        },
        "style_medium": "Consistent visual style"
      },
      "video_generation_notes": "Description of movement/transition between frames for reference"
    }
  ]
}

## FIBO STRUCTURED JSON REQUIREMENTS
- Use detailed object descriptions with all required fields
- Maintain consistent lighting and color schemes across segments
- Ensure visual continuity between checkpoints
- Create production-ready structured prompts for FIBO generation
- Focus on photorealistic, cinematic quality descriptions"""

class FIBOVideoDirector:
    """FIBO-specialized video director for checkpoint-based generation."""
    
    def __init__(self, api_key: str):
        """Initialize the FIBO video director."""
        self.api_key = api_key
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the FIBO director agent."""
        model = GeminiModel(
            client_args={"api_key": self.api_key},
            model_id="gemini-2.5-flash",
            params={"temperature": 0.3}
        )
        
        return Agent(
            model=model,
            system_prompt=FIBO_DIRECTOR_PROMPT
        )
    
    def create_video_plan(self, script_text: str) -> dict:
        """Create a complete FIBO video production plan with checkpoints.
        
        Args:
            script_text: The movie script to process
            
        Returns:
            Dictionary containing checkpoints and FIBO structured prompts
        """
        try:
            prompt = f"Create a FIBO video production plan for this script:\n\n{script_text}"
            response = self.agent(prompt)
            
            # Convert response to string and parse JSON
            response_text = str(response)
            
            # Extract JSON from response
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return self._create_fallback_plan(script_text)
                
        except Exception as e:
            print(f"Error creating video plan: {e}")
            return self._create_fallback_plan(script_text)
    
    def _create_fallback_plan(self, script_text: str) -> dict:
        """Create a basic fallback plan."""
        return {
            "project_title": "FIBO Generated Video",
            "total_duration_sec": 8,
            "visual_style": {
                "lighting_style": "Cinematic three-point lighting",
                "color_palette": "Natural, balanced colors",
                "camera_style": "50mm lens, f/2.8, professional cinematography",
                "environment_theme": "Realistic, detailed environments",
                "artistic_direction": "Photorealistic, high-quality production"
            },
            "checkpoints": [
                {
                    "checkpoint_id": 1,
                    "start_time_sec": 0,
                    "end_time_sec": 8,
                    "duration_sec": 8,
                    "scene_description": "Single scene from script",
                    "visual_consistency_notes": "Maintains established visual style",
                    "fibo_start_frame": self._create_basic_fibo_prompt("Opening frame", script_text[:200]),
                    "fibo_end_frame": self._create_basic_fibo_prompt("Closing frame", script_text[:200]),
                    "video_generation_notes": "Smooth transition with natural movement"
                }
            ]
        }
    
    def _create_basic_fibo_prompt(self, frame_type: str, context: str) -> dict:
        """Create a basic FIBO structured prompt."""
        return {
            "short_description": f"{frame_type}: {context}",
            "objects": [
                {
                    "description": "Main subject from script context",
                    "location": "Center frame",
                    "relationship": "Primary focus of scene",
                    "relative_size": "Prominent in frame",
                    "shape_and_color": "Natural, realistic appearance",
                    "texture": "Photorealistic surface details",
                    "appearance_details": "High-quality, detailed rendering",
                    "pose": "Natural, contextually appropriate",
                    "expression": "Contextually appropriate emotion",
                    "orientation": "Facing camera or contextually relevant direction"
                }
            ],
            "background_setting": "Detailed environment from script context",
            "lighting": "Professional, cinematic lighting setup",
            "aesthetics": {
                "composition": "Balanced, rule of thirds composition",
                "color_scheme": "Natural, harmonious color palette",
                "mood_atmosphere": "Appropriate to script context"
            },
            "photographic_characteristics": {
                "depth_of_field": "Appropriate focus for scene",
                "camera_angle": "Eye-level, professional framing",
                "lens_focal_length": "50mm equivalent, natural perspective"
            },
            "style_medium": "Photorealistic, cinematic"
        }
    
    def get_checkpoint_summary(self, video_plan: dict) -> str:
        """Get a summary of all checkpoints for selection."""
        if not video_plan or "checkpoints" not in video_plan:
            return "No checkpoints available"
        
        summary = []
        summary.append(f"🎬 {video_plan.get('project_title', 'Video Project')}")
        summary.append(f"📊 Total Duration: {video_plan.get('total_duration_sec', 0)} seconds")
        summary.append(f"🎯 Checkpoints: {len(video_plan['checkpoints'])}")
        summary.append("\n📋 CHECKPOINT OVERVIEW:")
        
        for checkpoint in video_plan["checkpoints"]:
            summary.append(f"  ✓ Checkpoint {checkpoint['checkpoint_id']}: {checkpoint['start_time_sec']}-{checkpoint['end_time_sec']}s")
            summary.append(f"    Scene: {checkpoint['scene_description'][:80]}...")
        
        summary.append(f"\n🎨 Visual Style: {video_plan.get('visual_style', {}).get('artistic_direction', 'Standard')}")
        
        return "\n".join(summary)
    
    def export_checkpoint_fibo_prompts(self, video_plan: dict, checkpoint_id: int) -> dict:
        """Export FIBO structured prompts for a specific checkpoint.
        
        Args:
            video_plan: The complete video plan
            checkpoint_id: ID of checkpoint to export
            
        Returns:
            Dictionary with start and end frame FIBO prompts
        """
        if not video_plan or "checkpoints" not in video_plan:
            return {"error": "No video plan available"}
        
        # Find the requested checkpoint
        checkpoint = None
        for cp in video_plan["checkpoints"]:
            if cp["checkpoint_id"] == checkpoint_id:
                checkpoint = cp
                break
        
        if not checkpoint:
            return {"error": f"Checkpoint {checkpoint_id} not found"}
        
        return {
            "checkpoint_id": checkpoint_id,
            "scene_description": checkpoint["scene_description"],
            "duration_sec": checkpoint["duration_sec"],
            "visual_style": video_plan.get("visual_style", {}),
            "fibo_start_frame": checkpoint["fibo_start_frame"],
            "fibo_end_frame": checkpoint["fibo_end_frame"],
            "video_generation_notes": checkpoint["video_generation_notes"]
        }

def main():
    """Demo the FIBO Video Director system."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Set your Google API key: set GOOGLE_API_KEY=your_key")
        return
    
    # Initialize the FIBO video director
    director = FIBOVideoDirector(os.environ["GOOGLE_API_KEY"])
    
    # Sample cyberpunk script for testing
    sample_script = """
    FADE IN:
    
    EXT. CYBERPUNK CITY - NIGHT
    
    Rain falls on neon-lit streets. Holographic advertisements flicker on towering buildings.
    
    JACK (30s, cybernetic arm, leather jacket) walks through the crowded street, dodging flying cars overhead. His augmented reality display shows incoming messages.
    
    JACK
    (to his AI assistant)
    Show me the route to the data center.
    
    A holographic path appears in his vision, leading through dark alleys.
    
    Jack turns into a narrow alley where ZARA (20s, punk hacker, glowing tattoos) waits by a hidden door.
    
    ZARA
    You're late. The security window closes in five minutes.
    
    JACK
    Traffic was hell. Flying cars everywhere.
    
    Zara activates a device that makes the door shimmer and become transparent.
    
    ZARA
    After you, corporate spy.
    
    Jack smirks and steps through the shimmering portal.
    
    INT. DATA CENTER - CONTINUOUS
    
    A vast room filled with glowing servers and holographic data streams. The air hums with electricity.
    
    JACK
    (amazed)
    This is it. The neural network core.
    
    Zara's tattoos pulse brighter as she interfaces with the system.
    
    ZARA
    I'm in. Downloading the consciousness files now.
    
    Suddenly, alarms blare. Red lights flash throughout the facility.
    
    JACK
    (urgent)
    We've been detected! How much longer?
    
    ZARA
    (focused, tattoos blazing)
    Thirty seconds! Keep them off me!
    
    Jack draws a plasma weapon as security drones swarm toward them.
    
    FADE OUT.
    """
    
    try:
        print("🎬 FIBO Video Director System")
        print("="*60)
        print("Processing cyberpunk script for FIBO video generation...")
        
        # Create the video plan with checkpoints
        video_plan = director.create_video_plan(sample_script)
        
        # Show checkpoint summary
        print("\n📋 VIDEO PLAN CREATED:")
        print("="*60)
        summary = director.get_checkpoint_summary(video_plan)
        print(summary)
        
        # Save the complete plan
        with open("fibo_video_plan.json", "w") as f:
            json.dump(video_plan, f, indent=2)
        print(f"\n💾 Complete video plan saved to: fibo_video_plan.json")
        
        # Demo: Export specific checkpoint for FIBO generation
        if video_plan.get("checkpoints"):
            checkpoint_id = 1
            print(f"\n🎯 EXPORTING CHECKPOINT {checkpoint_id} FOR FIBO GENERATION:")
            print("="*60)
            
            checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, checkpoint_id)
            
            # Save checkpoint-specific FIBO prompts
            with open(f"checkpoint_{checkpoint_id}_fibo_prompts.json", "w") as f:
                json.dump(checkpoint_data, f, indent=2)
            
            print(f"✅ Checkpoint {checkpoint_id} FIBO prompts exported")
            print(f"📄 Start Frame: {checkpoint_data['fibo_start_frame']['short_description'][:100]}...")
            print(f"📄 End Frame: {checkpoint_data['fibo_end_frame']['short_description'][:100]}...")
            print(f"💾 Saved to: checkpoint_{checkpoint_id}_fibo_prompts.json")
        
        print("\n🎥 WORKFLOW SUMMARY:")
        print("="*60)
        print("1. ✅ Script analyzed and broken into 8-second checkpoints")
        print("2. ✅ Consistent visual style established across all segments")
        print("3. ✅ FIBO structured JSON prompts created for each checkpoint")
        print("4. ✅ Checkpoints ready for selective frame generation")
        print("\n💡 Next Steps:")
        print("  • Select checkpoints for frame generation")
        print("  • Use FIBO structured prompts for consistent frames")
        print("  • Generate start and end frames for each segment")
        print("  • Combine frames into complete video sequence")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()