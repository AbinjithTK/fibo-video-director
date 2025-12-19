#!/usr/bin/env python3
"""
AI Director & Cinematography Orchestrator
Multi-Agent System for FIBO Video Production

This system coordinates three specialized agents:
- Editor Agent: Handles pacing, timing, and scene splitting
- Cinematographer Agent: Defines static world state for FIBO consistency  
- Action Director Agent: Creates specific prompts for frames and motion
"""

import os
import json
from typing import Dict, List, Any
from strands import Agent, tool
from strands.models.gemini import GeminiModel


class AIDirectorSystem:
    """Multi-agent system for converting scripts to FIBO production plans."""
    
    def __init__(self, api_key: str):
        """Initialize the three-agent system."""
        self.api_key = api_key
        self.editor_agent = None
        self.cinematographer_agent = None
        self.action_director_agent = None
        self._setup_agents()
    
    def _create_model(self, temperature: float = 0.3):
        """Create a Gemini model instance."""
        return GeminiModel(
            client_args={"api_key": self.api_key},
            model_id="gemini-2.5-flash",
            params={"temperature": temperature}
        )
    
    def _setup_agents(self):
        """Initialize all three specialized agents."""
        # Editor Agent - Handles pacing and scene splitting
        self.editor_agent = Agent(
            model=self._create_model(0.2),  # Low temperature for consistent pacing
            tools=[self._analyze_script_pacing, self._split_long_scenes],
            system_prompt="""You are THE EDITOR AGENT in a multi-agent film production system.

Your responsibilities:
- Analyze script dialogue and action density
- Apply the "Rule of 8": Split any action longer than 8 seconds into sequential shots
- Determine continuity between shots (is_continuation flag)
- Ensure proper pacing for AI video generation

CRITICAL RULES:
- Max shot duration: 8 seconds
- If Shot B follows Shot A continuously, set is_continuation: true
- If new camera angle or scene, set is_continuation: false
- Focus on visual storytelling rhythm"""
        )
        
        # Cinematographer Agent - Defines visual consistency
        self.cinematographer_agent = Agent(
            model=self._create_model(0.1),  # Very low temperature for consistency
            tools=[self._define_lighting, self._set_camera_specs, self._create_environment],
            system_prompt="""You are THE CINEMATOGRAPHER AGENT in a multi-agent film production system.

Your responsibilities:
- Define STATIC VISUAL PARAMETERS that must remain identical across frames
- Prevent "AI flickering" by maintaining consistent world state
- Extract lighting, palette, lens/camera, and environment settings
- Ensure FIBO can maintain visual coherence

CRITICAL FOCUS:
- Lighting: Volumetric fog, Neon Noir, High Contrast, Golden Hour, etc.
- Palette: Teal and Orange, Desaturated, Vivid, etc.
- Lens/Camera: 35mm Anamorphic, f/1.8, ISO 800, etc.
- Environment: Cyberpunk alleyway, wet pavement, etc.

These parameters MUST stay fixed within a scene for FIBO consistency."""
        )
        
        # Action Director Agent - Creates specific prompts
        self.action_director_agent = Agent(
            model=self._create_model(0.4),  # Higher temperature for creative prompts
            tools=[self._create_start_frame, self._create_end_frame, self._create_motion_bridge],
            system_prompt="""You are THE ACTION DIRECTOR AGENT in a multi-agent film production system.

Your responsibilities:
- Generate three distinct prompts for every shot:
  1. start_frame_prompt: Visual state at T=0
  2. end_frame_prompt: Visual state at T=8  
  3. video_generation_prompt: Motion description for Veo/Luma

CRITICAL RULES:
- If is_continuation=true, start_frame MUST match previous shot's end_frame exactly
- Use cinematic verbs for motion: "Slow dolly in", "Rack focus", "Character walks towards camera"
- Image prompts need NOUNS (objects, lighting, composition)
- Video prompts need VERBS (movement, transitions, camera motion)
- Be specific about FIBO's structured JSON requirements"""
        )
    
    # Tool definitions for Editor Agent
    @tool
    def _analyze_script_pacing(self, script_text: str) -> str:
        """Analyze script pacing and determine shot breakdown.
        
        Args:
            script_text: The movie script text to analyze
        """
        lines = script_text.split('\n')
        analysis = []
        
        # Count dialogue vs action lines
        dialogue_lines = sum(1 for line in lines if ':' in line and not line.strip().startswith('('))
        action_lines = len(lines) - dialogue_lines
        
        analysis.append(f"📊 Script Analysis:")
        analysis.append(f"  • Total lines: {len(lines)}")
        analysis.append(f"  • Dialogue lines: {dialogue_lines}")
        analysis.append(f"  • Action lines: {action_lines}")
        
        # Estimate timing (rough heuristic)
        estimated_seconds = (dialogue_lines * 3) + (action_lines * 2)
        shots_needed = max(1, estimated_seconds // 8)
        
        analysis.append(f"  • Estimated duration: {estimated_seconds} seconds")
        analysis.append(f"  • Shots needed (8s max): {shots_needed}")
        
        return "\n".join(analysis)
    
    @tool
    def _split_long_scenes(self, scene_description: str, max_duration: int = 8) -> str:
        """Split scenes longer than max_duration into sequential shots.
        
        Args:
            scene_description: Description of the scene
            max_duration: Maximum duration per shot in seconds
        """
        # Simple heuristic: if description is very long, suggest splits
        words = scene_description.split()
        
        if len(words) > 50:  # Rough threshold for 8+ second scenes
            return f"🎬 Scene Split Recommendation:\nScene appears complex ({len(words)} words). Consider splitting into 2-3 shots with continuity flags."
        else:
            return f"✅ Scene length appropriate for single {max_duration}s shot."
    
    # Tool definitions for Cinematographer Agent
    @tool
    def _define_lighting(self, scene_context: str) -> str:
        """Define lighting setup for scene consistency.
        
        Args:
            scene_context: Context about the scene setting and mood
        """
        lighting_options = {
            "interior": "Soft window light, warm practical lamps, rim lighting",
            "exterior_day": "Natural daylight, soft shadows, golden hour warmth",
            "exterior_night": "Moonlight, street lamps, neon reflections, high contrast",
            "cyberpunk": "Volumetric fog, neon noir, high contrast, colored gels",
            "dramatic": "Hard key light, deep shadows, chiaroscuro lighting"
        }
        
        # Simple keyword matching for demo
        context_lower = scene_context.lower()
        for key, lighting in lighting_options.items():
            if key in context_lower:
                return f"💡 Lighting Setup: {lighting}"
        
        return "💡 Lighting Setup: Balanced three-point lighting, natural color temperature"
    
    @tool
    def _set_camera_specs(self, shot_type: str) -> str:
        """Define camera specifications for the shot.
        
        Args:
            shot_type: Type of shot (wide, medium, close-up, etc.)
        """
        camera_specs = {
            "wide": "35mm lens, f/2.8, deep focus, stable tripod",
            "medium": "50mm lens, f/1.8, slight bokeh, handheld stability",
            "close": "85mm lens, f/1.4, shallow depth of field, precise focus",
            "action": "24mm lens, f/4, high shutter speed, gimbal stabilization"
        }
        
        shot_lower = shot_type.lower()
        for key, specs in camera_specs.items():
            if key in shot_lower:
                return f"📷 Camera Specs: {specs}"
        
        return "📷 Camera Specs: 50mm lens, f/2.8, balanced depth of field"
    
    @tool
    def _create_environment(self, location_description: str) -> str:
        """Create consistent environment description for FIBO.
        
        Args:
            location_description: Description of the scene location
        """
        return f"🌍 Environment: {location_description}, consistent lighting and materials, photorealistic textures"
    
    # Tool definitions for Action Director Agent
    @tool
    def _create_start_frame(self, scene_setup: str, is_continuation: bool = False) -> str:
        """Create detailed start frame prompt for FIBO.
        
        Args:
            scene_setup: Initial scene description
            is_continuation: Whether this continues from previous shot
        """
        if is_continuation:
            return f"🎬 Start Frame (Continuation): Matches previous end frame exactly. {scene_setup}"
        else:
            return f"🎬 Start Frame (New): {scene_setup}, establishing composition, initial character positions"
    
    @tool
    def _create_end_frame(self, scene_setup: str, action_description: str) -> str:
        """Create detailed end frame prompt for FIBO.
        
        Args:
            scene_setup: Scene context
            action_description: What happens during the shot
        """
        return f"🎬 End Frame: {scene_setup} after {action_description}, final character positions, completed action"
    
    @tool
    def _create_motion_bridge(self, camera_movement: str, character_action: str) -> str:
        """Create motion description for video generation.
        
        Args:
            camera_movement: How the camera moves
            character_action: What characters do
        """
        return f"🎥 Motion Bridge: {camera_movement} while {character_action}, smooth cinematic transition"
    
    def process_script(self, script_text: str) -> Dict[str, Any]:
        """Process a movie script through the multi-agent system.
        
        Args:
            script_text: The input movie script
            
        Returns:
            JSON production plan for FIBO video pipeline
        """
        print("🎬 AI Director System Processing Script...")
        
        # Step 1: Editor analyzes pacing
        print("📝 Editor Agent: Analyzing script pacing...")
        pacing_analysis = self.editor_agent(f"Analyze the pacing of this script and determine shot breakdown: {script_text}")
        
        # Step 2: Cinematographer defines visual style
        print("🎥 Cinematographer Agent: Defining visual consistency...")
        visual_style = self.cinematographer_agent(f"Define the lighting, camera, and environment for this scene: {script_text}")
        
        # Step 3: Action Director creates prompts
        print("🎬 Action Director Agent: Creating frame prompts...")
        frame_prompts = self.action_director_agent(f"Create start frame, end frame, and motion bridge prompts for: {script_text}")
        
        # Combine results into production plan
        production_plan = {
            "project_title": "AI Generated Film",
            "pacing_analysis": pacing_analysis,
            "visual_style": visual_style,
            "frame_prompts": frame_prompts,
            "shots": [
                {
                    "shot_id": 1,
                    "duration_sec": 8,
                    "is_continuation": False,
                    "pacing_reasoning": "Establishing shot based on script analysis",
                    "fibo_parameters": {
                        "static_world_state": {
                            "lighting": "Natural daylight, soft shadows",
                            "environment": "Extracted from script context",
                            "film_style": "Cinematic, photorealistic",
                            "aspect_ratio": "16:9"
                        },
                        "camera_angle": "Wide Shot",
                        "camera_movement": "Static"
                    },
                    "generation_prompts": {
                        "start_frame_image": "Generated by Action Director Agent",
                        "end_frame_image": "Generated by Action Director Agent", 
                        "video_motion_bridge": "Generated by Action Director Agent"
                    }
                }
            ]
        }
        
        return production_plan

def main():
    """Demo the AI Director System."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Set your Google API key: set GOOGLE_API_KEY=your_key")
        return
    
    # Initialize the multi-agent system
    director_system = AIDirectorSystem(os.environ["GOOGLE_API_KEY"])
    
    # Sample movie script
    sample_script = """
    FADE IN:
    
    EXT. CYBERPUNK ALLEY - NIGHT
    
    Rain falls on neon-lit pavement. Steam rises from manholes.
    
    JACK (30s, leather jacket, cybernetic arm) walks slowly down the alley, 
    his footsteps echoing. He stops at a red door marked with strange symbols.
    
    JACK
    (whispering to his comm device)
    I found it. The entrance to the underground.
    
    He reaches for the door handle. The symbols begin to glow.
    
    JACK
    (surprised)
    What the hell?
    
    The door slides open with a mechanical hiss, revealing a bright corridor beyond.
    
    FADE OUT.
    """
    
    try:
        print("🎬 Starting AI Director Multi-Agent System...")
        print("="*60)
        
        # Process the script
        production_plan = director_system.process_script(sample_script)
        
        print("\n📋 PRODUCTION PLAN GENERATED:")
        print("="*60)
        print(json.dumps(production_plan, indent=2))
        
        print("\n✅ Multi-Agent Processing Complete!")
        print("\n💡 This production plan can now be used with:")
        print("  • FIBO for keyframe generation")
        print("  • Veo/Luma for video generation")
        print("  • Automated video pipeline")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()