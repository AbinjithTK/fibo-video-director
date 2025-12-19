#!/usr/bin/env python3
"""
Advanced AI Director Agent

Single agent that implements the full AI Director & Cinematography Orchestrator
system prompt to generate production-ready JSON for FIBO video pipelines.
"""

import os
import json
from strands import Agent
from strands.models.gemini import GeminiModel

# The complete system prompt from your specification
DIRECTOR_SYSTEM_PROMPT = """You are the **AI Director & Cinematography Orchestrator**. Your goal is to take a raw movie script and convert it into a **JSON-Native Production Plan** for an AI Video Pipeline (using Bria FIBO for Keyframes and Veo for Video Generation). You are acting as a Multi-Agent System comprising an Editor, a Cinematographer, and an Action Director.

### ⚙️ GLOBAL CONSTRAINTS
1. **Max Duration:** No single shot can exceed 8 seconds.
2. **Consistency:** You must separate "Static Parameters" (which stay fixed for a scene) from "Dynamic Parameters" (movement).
3. **Format:** Output strictly valid JSON.

---

### 🕵️ AGENT 1: THE EDITOR (Pacing & Splitting)
- Analyze the script's dialogue and action density.
- **Rule of 8:** If an action takes longer than 8 seconds to visually tell, SPLIT it into sequential shots (Shot A -> Shot B).
- **Continuity Flag:**
  - If Shot B immediately follows Shot A in the same continuous take, set `"is_continuation": true`.
  - If it is a new camera angle or new scene, set `"is_continuation": false`.

### 🎥 AGENT 2: THE CINEMATOGRAPHER (FIBO Static Parameters)
- Define the **Visual Look** that MUST remain identical across all frames in a scene to prevent "AI flickering."
- Extract these into a `static_params` object:
  - **Lighting:** (e.g., "Volumetric fog, Neon Noir, High Contrast, Golden Hour")
  - **Palette:** (e.g., "Teal and Orange, Desaturated, Vivid")
  - **Lens/Camera:** (e.g., "35mm Anamorphic, f/1.8, ISO 800")
  - **Environment:** (e.g., "Cyberpunk alleyway, wet pavement")

### 🎬 AGENT 3: THE ACTION DIRECTOR (Prompt Engineering)
You must generate three distinct prompts for every shot:
1. **`start_frame_prompt`**: The visual state at T=0. (If `is_continuation` is true, this MUST describe the exact state of the previous shot's end).
2. **`end_frame_prompt`**: The visual state at T=8. How has the subject moved?
3. **`video_generation_prompt`**: A prompt specifically for Veo/Luma. Describes the *motion* between the two frames. Use cinematic verbs (e.g., "Slow dolly in," "Rack focus," "Character walks towards camera").

---

### 📝 OUTPUT JSON SCHEMA
Return ONLY this JSON structure (no markdown text):

{
  "project_title": "String",
  "shots": [
    {
      "shot_id": 1,
      "duration_sec": 8,
      "is_continuation": false,
      "pacing_reasoning": "Establishing shot, slow movement.",
      "fibo_parameters": {
        "static_world_state": {
          "lighting": "String (e.g., 'Soft moonlight, rim lighting')",
          "environment": "String (e.g., 'Interior spaceship cockpit, metallic surfaces')",
          "film_style": "String (e.g., 'Kodak Portra 400, grain')",
          "aspect_ratio": "16:9"
        },
        "camera_angle": "String (e.g., 'Wide Shot', 'Dutch Angle')",
        "camera_movement": "String (e.g., 'Static', 'Pan Right')"
      },
      "generation_prompts": {
        "start_frame_image": "String (Full detailed prompt for Bria FIBO at T=0)",
        "end_frame_image": "String (Full detailed prompt for Bria FIBO at T=8)",
        "video_motion_bridge": "String (Prompt for Veo: 'The camera slowly pushes in on the pilot while he turns his head left...')"
      }
    }
  ]
}"""

class AdvancedDirectorAgent:
    """Advanced AI Director that generates production-ready JSON."""
    
    def __init__(self, api_key: str):
        """Initialize the director agent."""
        self.api_key = api_key
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the director agent with the full system prompt."""
        model = GeminiModel(
            client_args={"api_key": self.api_key},
            model_id="gemini-2.5-flash",
            params={"temperature": 0.3}
        )
        
        return Agent(
            model=model,
            system_prompt=DIRECTOR_SYSTEM_PROMPT
        )
    
    def generate_production_plan(self, script_text: str) -> dict:
        """Generate a complete production plan from a movie script.
        
        Args:
            script_text: The movie script to process
            
        Returns:
            Dictionary containing the production plan JSON
        """
        try:
            # Ask the agent to process the script
            prompt = f"SCRIPT TO PROCESS:\n{script_text}"
            response = self.agent(prompt)
            
            # Convert AgentResult to string if needed
            response_text = str(response)
            
            # Try to parse as JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If response isn't pure JSON, try to extract it
                if "{" in response_text and "}" in response_text:
                    start = response_text.find("{")
                    end = response_text.rfind("}") + 1
                    json_str = response_text[start:end]
                    return json.loads(json_str)
                else:
                    # Print the response for debugging
                    print(f"Raw response: {response_text[:500]}...")
                    raise ValueError("No valid JSON found in response")
                    
        except Exception as e:
            print(f"Error generating production plan: {e}")
            return self._create_fallback_plan(script_text)
    
    def _create_fallback_plan(self, script_text: str) -> dict:
        """Create a basic fallback production plan."""
        return {
            "project_title": "Generated Film",
            "shots": [
                {
                    "shot_id": 1,
                    "duration_sec": 8,
                    "is_continuation": False,
                    "pacing_reasoning": "Single establishing shot for script",
                    "fibo_parameters": {
                        "static_world_state": {
                            "lighting": "Natural daylight, balanced exposure",
                            "environment": "Scene environment from script",
                            "film_style": "Cinematic, photorealistic",
                            "aspect_ratio": "16:9"
                        },
                        "camera_angle": "Wide Shot",
                        "camera_movement": "Static"
                    },
                    "generation_prompts": {
                        "start_frame_image": f"Opening frame: {script_text[:200]}...",
                        "end_frame_image": f"Closing frame: {script_text[:200]}...",
                        "video_motion_bridge": "Smooth cinematic transition with natural movement"
                    }
                }
            ]
        }

def main():
    """Demo the Advanced Director Agent."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Get your API key from: https://aistudio.google.com/apikey")
        print("Then set: set GOOGLE_API_KEY=your_key")
        return
    
    # Initialize the director agent
    director = AdvancedDirectorAgent(os.environ["GOOGLE_API_KEY"])
    
    # Sample cyberpunk script
    sample_script = """
    FADE IN:
    
    EXT. NEON-LIT STREET - NIGHT
    
    Rain cascades down the windshield of a hovering police car. Neon signs reflect in puddles below.
    
    DETECTIVE MAYA (35, cybernetic eye implant, worn leather coat) steps out of the car onto the wet pavement. She looks up at a towering corporate building, its holographic advertisements flickering.
    
    MAYA
    (into comm device)
    I'm at the Nexus Tower. Beginning investigation.
    
    She walks toward the building entrance, her footsteps echoing. The automatic doors slide open with a soft hiss.
    
    INT. NEXUS TOWER LOBBY - CONTINUOUS
    
    Maya enters a pristine white lobby. Holographic receptionists flicker to life.
    
    HOLOGRAM
    Welcome to Nexus Corporation. How may we assist you?
    
    Maya flashes her badge. The hologram's expression changes to concern.
    
    FADE OUT.
    """
    
    try:
        print("🎬 Advanced AI Director Agent")
        print("="*50)
        print("Processing cyberpunk script...")
        
        # Generate the production plan
        production_plan = director.generate_production_plan(sample_script)
        
        print("\n📋 PRODUCTION PLAN:")
        print("="*50)
        print(json.dumps(production_plan, indent=2))
        
        # Save to file
        with open("production_plan.json", "w") as f:
            json.dump(production_plan, f, indent=2)
        
        print(f"\n✅ Production plan saved to: production_plan.json")
        print("\n🎥 Ready for FIBO + Veo pipeline!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()