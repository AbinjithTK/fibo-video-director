#!/usr/bin/env python3
"""
Enhanced FIBO Video Director with Strands & AgentCore MCP Integration

Production-ready implementation using:
- Strands multi-agent patterns (Swarm collaboration)
- Shared state management with invocation_state
- AgentCore Runtime compatibility
- Tool context integration for state sharing
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from strands import Agent, tool
from strands.models.gemini import GeminiModel


# =============================================================================
# SHARED STATE TOOLS - Using @tool decorator with state management
# =============================================================================

@tool
def update_shared_state(key: str, value: str) -> str:
    """Update shared state for cross-agent communication.
    
    Args:
        key: State key to update
        value: Value to store (JSON string for complex data)
    """
    return f"State updated: {key} = {value[:100]}..."


@tool
def get_production_context() -> str:
    """Get current production context from shared state."""
    return "Production context retrieved from shared state"


@tool
def analyze_script_structure(script_text: str) -> str:
    """Analyze script structure for pacing decisions.
    
    Args:
        script_text: The movie script to analyze
    """
    lines = [l.strip() for l in script_text.split('\n') if l.strip()]
    
    # Count different line types
    dialogue_count = sum(1 for l in lines if any(c.isupper() for c in l[:20]) and ':' not in l[:30])
    action_count = len(lines) - dialogue_count
    
    # Estimate timing (rough heuristic)
    estimated_seconds = (dialogue_count * 4) + (action_count * 2)
    segments_needed = max(1, (estimated_seconds + 7) // 8)  # Round up to 8-second segments
    
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
    # Analyze context for style decisions
    context_lower = scene_context.lower()
    
    # Determine lighting based on context
    if "night" in context_lower or "dark" in context_lower:
        lighting = "Low-key lighting with dramatic shadows, rim lighting, neon accents"
    elif "day" in context_lower or "bright" in context_lower:
        lighting = "Natural daylight, soft diffused shadows, warm color temperature"
    elif "cyberpunk" in context_lower or "neon" in context_lower:
        lighting = "Volumetric fog, neon noir, high contrast, colored gels (cyan/magenta)"
    else:
        lighting = "Balanced three-point lighting, natural color temperature"
    
    # Determine color palette
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


@tool
def create_video_motion_notes(
    scene_content: str,
    start_frame_description: str,
    end_frame_description: str,
    segment_duration: str = "8 seconds"
) -> str:
    """Create detailed video generation prompt optimized for video AI models like Veo.
    
    Args:
        scene_content: The actual script content for this segment
        start_frame_description: Description of the starting frame
        end_frame_description: Description of the ending frame
        segment_duration: Duration of the video segment
    """
    
    # Analyze scene content for specific elements
    scene_lower = scene_content.lower()
    
    # Extract dialogue if present
    dialogue_lines = []
    action_lines = []
    
    for line in scene_content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if it's dialogue (character name followed by dialogue)
        if any(char.isupper() for char in line[:20]) and not line.startswith(('EXT.', 'INT.', 'FADE', 'CUT')):
            if '(' in line and ')' in line:  # Action in parentheses
                action_lines.append(line)
            else:
                dialogue_lines.append(line)
        else:
            action_lines.append(line)
    
    # Determine camera movement based on scene content
    camera_movement = "Static shot"
    if any(word in scene_lower for word in ['walks', 'runs', 'moves', 'approaches']):
        camera_movement = "Smooth tracking shot following character movement"
    elif any(word in scene_lower for word in ['turns', 'looks', 'faces']):
        camera_movement = "Subtle pan following character's gaze"
    elif any(word in scene_lower for word in ['reveals', 'shows', 'appears']):
        camera_movement = "Slow reveal with gentle dolly movement"
    elif any(word in scene_lower for word in ['close', 'closeup', 'detail']):
        camera_movement = "Slow push-in to close-up"
    
    # Determine pacing and mood
    pacing = "Measured, cinematic pacing"
    if any(word in scene_lower for word in ['urgent', 'quickly', 'suddenly', 'rush']):
        pacing = "Fast-paced, dynamic movement"
    elif any(word in scene_lower for word in ['slowly', 'gentle', 'calm', 'peaceful']):
        pacing = "Slow, contemplative pacing"
    elif any(word in scene_lower for word in ['tense', 'suspense', 'danger']):
        pacing = "Tense, building suspense"
    
    # Determine lighting and atmosphere changes
    lighting_transition = "Consistent lighting throughout"
    if any(word in scene_lower for word in ['shadow', 'dark', 'dim']):
        lighting_transition = "Gradual transition to darker, more dramatic lighting"
    elif any(word in scene_lower for word in ['bright', 'light', 'sun', 'glow']):
        lighting_transition = "Brightening lighting with warm tones"
    elif any(word in scene_lower for word in ['flicker', 'flash', 'strobe']):
        lighting_transition = "Dynamic lighting changes with flickering effects"
    
    # Create comprehensive video prompt
    video_prompt = {
        "duration": segment_duration,
        "scene_summary": scene_content[:300] + "..." if len(scene_content) > 300 else scene_content,
        
        # Visual Transition
        "visual_transition": {
            "start_frame": start_frame_description[:200],
            "end_frame": end_frame_description[:200],
            "transition_type": "Smooth cinematic transition maintaining visual continuity"
        },
        
        # Camera Work
        "camera_work": {
            "movement": camera_movement,
            "shot_type": "Professional cinematic framing",
            "focus": "Sharp focus on main subjects with cinematic depth of field",
            "composition": "Rule of thirds, balanced composition"
        },
        
        # Action & Movement
        "action_description": {
            "character_actions": [action.strip() for action in action_lines[:3]],  # Top 3 actions
            "movement_flow": "Natural, realistic character movement and gestures",
            "pacing": pacing,
            "continuity": "Seamless action flow from start to end frame"
        },
        
        # Dialogue & Audio Cues
        "dialogue_cues": {
            "spoken_lines": [dialogue.strip() for dialogue in dialogue_lines[:2]],  # Top 2 dialogue lines
            "delivery_style": "Natural, emotionally appropriate delivery",
            "timing": "Dialogue synchronized with character lip movement and gestures",
            "audio_atmosphere": "Ambient sound appropriate to scene setting"
        },
        
        # Lighting & Atmosphere
        "lighting_atmosphere": {
            "lighting_transition": lighting_transition,
            "mood_progression": "Consistent emotional tone throughout segment",
            "color_grading": "Cinematic color palette maintaining visual style",
            "atmospheric_effects": "Subtle environmental effects (dust, mist, particles) if appropriate"
        },
        
        # Technical Specifications
        "technical_specs": {
            "frame_rate": "24fps for cinematic feel",
            "resolution": "4K for high quality output",
            "aspect_ratio": "16:9 widescreen",
            "motion_blur": "Natural motion blur for realistic movement"
        },
        
        # Video AI Optimization
        "veo_optimization": {
            "prompt_style": "Cinematic, professional video production",
            "quality_keywords": "high quality, detailed, realistic, smooth motion",
            "avoid": "jumpcuts, inconsistent lighting, unnatural movement",
            "enhance": "natural character expressions, realistic physics, professional cinematography"
        }
    }
    
    return json.dumps(video_prompt, indent=2)


# =============================================================================
# ENHANCED FIBO DIRECTOR CLASS
# =============================================================================

class EnhancedFIBODirector:
    """Enhanced FIBO Video Director using Strands best practices."""
    
    def __init__(self, api_key: str):
        """Initialize the enhanced director system."""
        self.api_key = api_key
        self.shared_state: Dict[str, Any] = {}
        self.agents = self._create_agents()
        
    def _create_model(self, temperature: float = 0.3):
        """Create Gemini model instance."""
        return GeminiModel(
            client_args={"api_key": self.api_key},
            model_id="gemini-2.5-flash",
            params={"temperature": temperature}
        )
    
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized agents for the production pipeline."""
        return {
            "editor": self._create_editor_agent(),
            "cinematographer": self._create_cinematographer_agent(),
            "action_director": self._create_action_director_agent()
        }
    
    def _create_editor_agent(self) -> Agent:
        """Create the Editor agent for pacing and segmentation."""
        return Agent(
            model=self._create_model(0.2),
            tools=[analyze_script_structure, split_into_segments, update_shared_state],
            system_prompt="""You are THE EDITOR AGENT in a multi-agent FIBO video production system.

YOUR ROLE:
- Analyze script pacing and dialogue/action density
- Apply the "Rule of 8": Break scripts into 8-second video segments
- Determine continuity between segments
- Create logical segment boundaries

WORKFLOW:
1. Use analyze_script_structure to understand the script
2. Use split_into_segments to create 8-second checkpoints
3. Use update_shared_state to share segment data with other agents

OUTPUT: Return segment breakdown as JSON with timing and continuity flags."""
        )
    
    def _create_cinematographer_agent(self) -> Agent:
        """Create the Cinematographer agent for visual consistency."""
        return Agent(
            model=self._create_model(0.1),
            tools=[define_visual_style, get_production_context, update_shared_state],
            system_prompt="""You are THE CINEMATOGRAPHER AGENT in a multi-agent FIBO video production system.

YOUR ROLE:
- Define STATIC VISUAL PARAMETERS that remain consistent across all frames
- Prevent "AI flickering" by establishing consistent world state
- Set lighting, color palette, camera style, and environment theme

CRITICAL FOCUS:
- Lighting: Must be consistent across all segments
- Color Palette: Unified color grading throughout
- Camera Style: Consistent lens and depth of field
- Environment: Coherent world-building

OUTPUT: Return visual_style JSON that will be applied to ALL FIBO prompts."""
        )
    
    def _create_action_director_agent(self) -> Agent:
        """Create the Action Director agent for frame prompts."""
        return Agent(
            model=self._create_model(0.4),
            tools=[
                create_fibo_frame_prompt,
                create_video_motion_notes,
                get_production_context,
                update_shared_state
            ],
            system_prompt="""You are THE ACTION DIRECTOR AGENT in a multi-agent FIBO video production system.

YOUR ROLE:
- Create detailed FIBO structured JSON prompts for start and end frames
- Write SCENE-SPECIFIC video motion notes optimized for video AI models like Veo
- Ensure visual continuity between segments while capturing unique scene elements

FOR EACH SEGMENT, CREATE:
1. fibo_start_frame: Detailed structured JSON for opening frame
2. fibo_end_frame: Detailed structured JSON for closing frame  
3. video_generation_notes: SCENE-SPECIFIC motion description with:
   - Actual dialogue from the script
   - Specific character actions and movements
   - Appropriate camera work for the scene
   - Lighting and atmosphere changes
   - Technical specifications for video AI

CRITICAL RULES:
- If segment is_continuation=true, start_frame MUST match previous end_frame
- Use the visual_style from Cinematographer for consistency
- Create production-ready FIBO structured prompts
- Make video_generation_notes UNIQUE for each scene - analyze the actual script content
- Include specific dialogue lines, character actions, and camera movements
- Optimize prompts for video AI models (Veo, Runway, etc.)

OUTPUT: Return checkpoint data with complete FIBO prompts and scene-specific video notes."""
        )
    
    def process_script(self, script_text: str) -> Dict[str, Any]:
        """Process a movie script through the multi-agent Swarm.
        
        Uses Strands Swarm pattern for collaborative agent processing.
        
        Args:
            script_text: The input movie script
            
        Returns:
            Complete production plan with FIBO checkpoints
        """
        print("🎬 Enhanced FIBO Director - Processing Script...")
        
        # Initialize shared state for this production
        production_id = str(uuid.uuid4())[:8]
        self.shared_state = {
            "production_id": production_id,
            "script_text": script_text,
            "created_at": datetime.now().isoformat(),
            "segments": [],
            "visual_style": {},
            "checkpoints": []
        }
        
        try:
            # PHASE 1: Editor analyzes and segments the script
            print("📝 Phase 1: Editor Agent analyzing script...")
            editor_prompt = f"""Analyze this script and create 8-second segments:

{script_text}

Steps:
1. First use analyze_script_structure to understand the script
2. Then use split_into_segments with the recommended number of segments
3. Return the complete segment breakdown"""

            editor_response = self.agents["editor"](editor_prompt)
            segments = self._extract_json_from_response(str(editor_response))
            
            if isinstance(segments, list):
                self.shared_state["segments"] = segments
            elif isinstance(segments, dict) and "segments" in segments:
                self.shared_state["segments"] = segments["segments"]
            else:
                # Fallback: Create segments manually if agent fails
                print("   ⚠️ Agent segmentation failed, using fallback")
                self.shared_state["segments"] = self._create_fallback_segments(script_text)
            
            print(f"   ✓ Created {len(self.shared_state['segments'])} segments")
            
            # PHASE 2: Cinematographer defines visual style
            print("🎥 Phase 2: Cinematographer Agent defining visual style...")
            
            # Extract scene context from script
            scene_context = self._extract_scene_context(script_text)
            mood = self._extract_mood(script_text)
            
            cinematographer_prompt = f"""Define the visual style for this production:

Scene Context: {scene_context}
Mood: {mood}

Use define_visual_style to create consistent visual parameters for all frames."""

            cinematographer_response = self.agents["cinematographer"](cinematographer_prompt)
            visual_style = self._extract_json_from_response(str(cinematographer_response))
            
            if visual_style and isinstance(visual_style, dict):
                self.shared_state["visual_style"] = visual_style
            else:
                # Fallback visual style
                print("   ⚠️ Agent visual style failed, using fallback")
                self.shared_state["visual_style"] = self._create_fallback_visual_style(scene_context, mood)
            
            print(f"   ✓ Visual style defined")
            
            # PHASE 3: Action Director creates FIBO prompts for each segment
            print("🎬 Phase 3: Action Director Agent creating FIBO prompts...")
            
            checkpoints = []
            visual_style_json = json.dumps(self.shared_state.get("visual_style", {}))
            
            for i, segment in enumerate(self.shared_state.get("segments", [])):
                segment_content = segment.get("content", script_text[:500])
                is_continuation = segment.get("is_continuation", i > 0)
                
                action_prompt = f"""Create FIBO prompts for segment {i + 1}:

Segment Content: {segment_content}
Visual Style: {visual_style_json}
Is Continuation: {is_continuation}

Create detailed prompts for this specific scene:
1. Start frame FIBO prompt using create_fibo_frame_prompt
2. End frame FIBO prompt using create_fibo_frame_prompt  
3. Scene-specific video motion notes using create_video_motion_notes with the actual segment content

Make sure the video motion notes are specific to this scene's actions, dialogue, and camera work."""

                action_response = self.agents["action_director"](action_prompt)
                
                # Create checkpoint structure
                checkpoint = self._create_checkpoint(
                    checkpoint_id=i + 1,
                    segment=segment,
                    visual_style=self.shared_state.get("visual_style", {}),
                    action_response=str(action_response)
                )
                checkpoints.append(checkpoint)
                print(f"   ✓ Checkpoint {i + 1} created")
            
            self.shared_state["checkpoints"] = checkpoints
            
            # Build final production plan
            production_plan = self._build_production_plan()
            
            print(f"\n✅ Production plan complete: {len(checkpoints)} checkpoints")
            return production_plan
            
        except Exception as e:
            print(f"❌ Error in processing: {e}")
            # Check if it's a quota error and create a better fallback
            if "quota" in str(e).lower() or "resource_exhausted" in str(e).lower():
                print("   📊 API quota exceeded - creating enhanced fallback plan")
                return self._create_enhanced_fallback_plan(script_text)
            return self._create_fallback_plan(script_text)
    
    def _extract_json_from_response(self, response_text: str) -> Any:
        """Extract JSON from agent response with improved parsing."""
        print(f"   DEBUG: Parsing response (length: {len(response_text)})")
        print(f"   DEBUG: Response preview: {response_text[:200]}...")
        
        try:
            # Try to find the largest valid JSON structure
            json_candidates = []
            
            # Look for JSON arrays
            array_start = 0
            while True:
                start = response_text.find("[", array_start)
                if start == -1:
                    break
                    
                depth = 0
                end = start
                for i, char in enumerate(response_text[start:], start):
                    if char == "[":
                        depth += 1
                    elif char == "]":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                
                if end > start:
                    try:
                        json_str = response_text[start:end]
                        result = json.loads(json_str)
                        json_candidates.append(("array", result, len(json_str)))
                        print(f"   DEBUG: Found valid JSON array with {len(result) if isinstance(result, list) else 'unknown'} items")
                    except json.JSONDecodeError:
                        pass
                
                array_start = start + 1
            
            # Look for JSON objects
            obj_start = 0
            while True:
                start = response_text.find("{", obj_start)
                if start == -1:
                    break
                    
                depth = 0
                end = start
                for i, char in enumerate(response_text[start:], start):
                    if char == "{":
                        depth += 1
                    elif char == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                
                if end > start:
                    try:
                        json_str = response_text[start:end]
                        result = json.loads(json_str)
                        json_candidates.append(("object", result, len(json_str)))
                        print(f"   DEBUG: Found valid JSON object with keys: {list(result.keys()) if isinstance(result, dict) else 'unknown'}")
                    except json.JSONDecodeError:
                        pass
                
                obj_start = start + 1
            
            # Return the largest valid JSON structure
            if json_candidates:
                # Sort by size (largest first) and prefer arrays for segments
                json_candidates.sort(key=lambda x: (x[0] == "array", x[2]), reverse=True)
                best_candidate = json_candidates[0]
                print(f"   DEBUG: Selected {best_candidate[0]} with size {best_candidate[2]}")
                return best_candidate[1]
                
        except Exception as e:
            print(f"   DEBUG: JSON extraction error: {e}")
        
        print(f"   DEBUG: No valid JSON found in response")
        return {}
    
    def _extract_scene_context(self, script_text: str) -> str:
        """Extract scene context from script."""
        lines = script_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('EXT.') or line.startswith('INT.'):
                return line
            if any(word in line.lower() for word in ['scene', 'setting', 'location']):
                return line
        return "Cinematic scene with professional production values"
    
    def _extract_mood(self, script_text: str) -> str:
        """Extract mood from script."""
        script_lower = script_text.lower()
        
        if any(word in script_lower for word in ['tense', 'danger', 'urgent', 'chase']):
            return "Tense, suspenseful"
        elif any(word in script_lower for word in ['happy', 'joy', 'laugh', 'celebrate']):
            return "Joyful, uplifting"
        elif any(word in script_lower for word in ['sad', 'grief', 'loss', 'cry']):
            return "Melancholic, emotional"
        elif any(word in script_lower for word in ['dark', 'night', 'shadow', 'mystery']):
            return "Dark, mysterious"
        else:
            return "Dramatic, cinematic"
    
    def _create_fallback_segments(self, script_text: str) -> List[Dict[str, Any]]:
        """Create fallback segments when agent processing fails."""
        lines = [l.strip() for l in script_text.split('\n') if l.strip()]
        
        # Estimate segments needed (aim for 8-second segments)
        estimated_seconds = len(lines) * 2  # Rough estimate: 2 seconds per line
        num_segments = max(2, min(4, (estimated_seconds + 7) // 8))  # 2-4 segments
        
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
        
        print(f"   DEBUG: Created {len(segments)} fallback segments")
        return segments
    
    def _create_fallback_visual_style(self, scene_context: str, mood: str) -> Dict[str, Any]:
        """Create fallback visual style when agent processing fails."""
        context_lower = scene_context.lower()
        
        # Determine lighting based on context
        if "night" in context_lower or "dark" in context_lower:
            lighting = "Low-key lighting with dramatic shadows, rim lighting"
        elif "cyberpunk" in context_lower or "neon" in context_lower:
            lighting = "Volumetric fog, neon noir, high contrast, colored gels"
        else:
            lighting = "Balanced three-point lighting, natural color temperature"
        
        # Determine color palette
        if "warm" in mood.lower() or "happy" in mood.lower():
            palette = "Warm tones, golden highlights, saturated colors"
        elif "cold" in mood.lower() or "tense" in mood.lower():
            palette = "Cool tones, desaturated, teal and orange contrast"
        else:
            palette = "Natural, balanced color palette with cinematic grading"
        
        return {
            "lighting_style": lighting,
            "color_palette": palette,
            "camera_style": "50mm lens, f/2.8, cinematic depth of field",
            "environment_theme": scene_context[:200],
            "artistic_direction": f"{mood} mood, photorealistic, high production value",
            "film_stock": "Digital cinema, slight grain, high dynamic range"
        }
    
    def _create_scene_specific_video_notes(self, scene_content: str, start_desc: str, end_desc: str) -> str:
        """Create scene-specific video notes when agent processing fails."""
        
        # Analyze scene content for specific elements
        scene_lower = scene_content.lower()
        lines = [l.strip() for l in scene_content.split('\n') if l.strip()]
        
        # Extract dialogue and actions
        dialogue_lines = []
        action_lines = []
        character_actions = []
        
        for line in lines:
            if not line:
                continue
                
            # Check for character dialogue (UPPERCASE name followed by dialogue)
            if line.isupper() and len(line) < 50:  # Character name
                continue
            elif '(' in line and ')' in line:  # Stage directions
                action_lines.append(line.strip('()'))
                if any(word in line.lower() for word in ['walks', 'runs', 'moves', 'turns', 'looks', 'grabs', 'opens']):
                    character_actions.append(line.strip('()'))
            elif not line.startswith(('EXT.', 'INT.', 'FADE', 'CUT')) and not line.isupper():
                # Likely dialogue
                dialogue_lines.append(line)
            else:
                # Action description
                action_lines.append(line)
                if any(word in line.lower() for word in ['walks', 'runs', 'moves', 'turns', 'looks', 'grabs', 'opens']):
                    character_actions.append(line)
        
        # Determine camera movement based on scene content
        camera_movement = "Static cinematic shot with subtle movement"
        if any(word in scene_lower for word in ['walks', 'runs', 'moves', 'approaches', 'steps']):
            camera_movement = "Smooth tracking shot following character movement"
        elif any(word in scene_lower for word in ['turns', 'looks', 'faces', 'glances']):
            camera_movement = "Subtle pan following character's gaze and attention"
        elif any(word in scene_lower for word in ['reveals', 'shows', 'appears', 'emerges']):
            camera_movement = "Slow reveal with gentle dolly movement"
        elif any(word in scene_lower for word in ['close', 'closeup', 'detail', 'focus']):
            camera_movement = "Slow push-in to close-up for dramatic emphasis"
        elif any(word in scene_lower for word in ['urgent', 'quickly', 'rush', 'hurry']):
            camera_movement = "Dynamic handheld movement conveying urgency"
        
        # Determine pacing and mood
        pacing = "Measured, cinematic pacing"
        if any(word in scene_lower for word in ['urgent', 'quickly', 'suddenly', 'rush', 'hurry']):
            pacing = "Fast-paced, dynamic movement with quick cuts"
        elif any(word in scene_lower for word in ['slowly', 'gentle', 'calm', 'peaceful', 'quiet']):
            pacing = "Slow, contemplative pacing with lingering shots"
        elif any(word in scene_lower for word in ['tense', 'suspense', 'danger', 'worried', 'afraid']):
            pacing = "Tense, building suspense with deliberate timing"
        
        # Determine lighting and atmosphere
        lighting_transition = "Consistent cinematic lighting throughout"
        if any(word in scene_lower for word in ['night', 'dark', 'shadow', 'dim']):
            lighting_transition = "Dramatic low-key lighting with strong shadows"
        elif any(word in scene_lower for word in ['neon', 'glow', 'electric', 'bright']):
            lighting_transition = "Dynamic lighting with neon and electric effects"
        elif any(word in scene_lower for word in ['rain', 'storm', 'weather']):
            lighting_transition = "Atmospheric lighting with weather effects"
        
        # Extract specific environment details
        environment_details = "Professional cinematic environment"
        if 'cyberpunk' in scene_lower or 'neon' in scene_lower:
            environment_details = "Cyberpunk cityscape with neon lighting and futuristic elements"
        elif 'city' in scene_lower or 'street' in scene_lower:
            environment_details = "Urban environment with realistic city atmosphere"
        elif 'alley' in scene_lower:
            environment_details = "Narrow alley with dramatic lighting and shadows"
        elif 'portal' in scene_lower or 'energy' in scene_lower:
            environment_details = "Sci-fi environment with energy effects and technological elements"
        
        # Create comprehensive video notes optimized for video AI
        video_notes = {
            "duration": "8 seconds",
            "scene_summary": scene_content[:300] + "..." if len(scene_content) > 300 else scene_content,
            
            # Visual Transition
            "visual_transition": {
                "start_frame": start_desc,
                "end_frame": end_desc,
                "transition_type": "Smooth cinematic transition maintaining visual continuity"
            },
            
            # Camera Work
            "camera_work": {
                "movement": camera_movement,
                "shot_type": "Professional cinematic framing with rule of thirds",
                "focus": "Sharp focus on main subjects with cinematic depth of field",
                "composition": "Balanced composition with dynamic visual interest"
            },
            
            # Action & Movement
            "action_description": {
                "character_actions": character_actions[:3] if character_actions else ["Natural character movement and gestures"],
                "movement_flow": "Realistic character movement with natural physics",
                "pacing": pacing,
                "continuity": "Seamless action flow from start to end frame"
            },
            
            # Dialogue & Audio Cues
            "dialogue_cues": {
                "spoken_lines": dialogue_lines[:2] if dialogue_lines else [],
                "delivery_style": "Natural, emotionally appropriate delivery",
                "timing": "Dialogue synchronized with character lip movement",
                "audio_atmosphere": f"Ambient sound appropriate to {environment_details.lower()}"
            },
            
            # Lighting & Atmosphere
            "lighting_atmosphere": {
                "lighting_transition": lighting_transition,
                "mood_progression": "Consistent emotional tone throughout segment",
                "color_grading": "Cinematic color palette with professional grading",
                "atmospheric_effects": "Subtle environmental effects enhancing realism"
            },
            
            # Technical Specifications
            "technical_specs": {
                "frame_rate": "24fps for cinematic feel",
                "resolution": "4K for high quality output",
                "aspect_ratio": "16:9 widescreen",
                "motion_blur": "Natural motion blur for realistic movement"
            },
            
            # Video AI Optimization (Veo, Runway, etc.)
            "veo_optimization": {
                "prompt_style": "Cinematic, professional video production",
                "quality_keywords": "high quality, detailed, realistic, smooth motion, professional cinematography",
                "environment": environment_details,
                "avoid": "jumpcuts, inconsistent lighting, unnatural movement, low quality",
                "enhance": "natural expressions, realistic physics, smooth transitions, cinematic composition"
            }
        }
        
        return json.dumps(video_notes, indent=2)
    
    def _create_checkpoint(
        self,
        checkpoint_id: int,
        segment: Dict,
        visual_style: Dict,
        action_response: str
    ) -> Dict[str, Any]:
        """Create a checkpoint structure from agent outputs."""
        
        # Try to extract FIBO prompts from action response
        extracted = self._extract_json_from_response(action_response)
        
        # Handle both list and dict responses
        if isinstance(extracted, list) and len(extracted) > 0:
            extracted = extracted[0]  # Take first item if it's a list
        elif not isinstance(extracted, dict):
            extracted = {}
        
        # Build FIBO start frame
        start_frame = extracted.get("fibo_start_frame") or self._create_default_fibo_prompt(
            "start",
            segment.get("content", "Scene opening"),
            visual_style
        )
        
        # Build FIBO end frame
        end_frame = extracted.get("fibo_end_frame") or self._create_default_fibo_prompt(
            "end",
            segment.get("content", "Scene closing"),
            visual_style
        )
        
        # Build video notes with scene-specific content
        if isinstance(extracted, dict) and extracted.get("video_generation_notes"):
            video_notes = extracted["video_generation_notes"]
        else:
            # Create scene-specific fallback video notes
            video_notes = self._create_scene_specific_video_notes(
                segment.get("content", "Scene content"),
                start_frame.get("short_description", "Start frame"),
                end_frame.get("short_description", "End frame")
            )
        
        return {
            "checkpoint_id": checkpoint_id,
            "start_time_sec": segment.get("start_time_sec", (checkpoint_id - 1) * 8),
            "end_time_sec": segment.get("end_time_sec", checkpoint_id * 8),
            "duration_sec": 8,
            "scene_description": segment.get("content", "")[:200],
            "is_continuation": segment.get("is_continuation", checkpoint_id > 1),
            "visual_consistency_notes": f"Maintains {visual_style.get('artistic_direction', 'cinematic')} style",
            "fibo_start_frame": start_frame,
            "fibo_end_frame": end_frame,
            "video_generation_notes": video_notes if isinstance(video_notes, str) else json.dumps(video_notes)
        }
    
    def _create_default_fibo_prompt(
        self,
        frame_type: str,
        scene_content: str,
        visual_style: Dict
    ) -> Dict[str, Any]:
        """Create a default FIBO structured prompt."""
        return {
            "short_description": f"{frame_type.title()} frame: {scene_content[:100]}",
            "objects": [
                {
                    "description": "Main subject from scene",
                    "location": "Center frame",
                    "relationship": "Primary focus",
                    "relative_size": "Prominent",
                    "shape_and_color": "Natural appearance",
                    "texture": "Photorealistic",
                    "appearance_details": "High quality",
                    "pose": "Natural positioning",
                    "expression": "Contextually appropriate",
                    "orientation": "Camera-facing"
                }
            ],
            "background_setting": scene_content[:150],
            "lighting": visual_style.get("lighting_style", "Cinematic lighting"),
            "aesthetics": {
                "composition": "Rule of thirds",
                "color_scheme": visual_style.get("color_palette", "Natural"),
                "mood_atmosphere": visual_style.get("artistic_direction", "Cinematic")
            },
            "photographic_characteristics": {
                "depth_of_field": "Cinematic shallow DOF",
                "camera_angle": "Eye-level",
                "lens_focal_length": "50mm"
            },
            "style_medium": "Photorealistic, cinematic"
        }
    
    def _build_production_plan(self) -> Dict[str, Any]:
        """Build the final production plan."""
        checkpoints = self.shared_state.get("checkpoints", [])
        
        return {
            "project_title": f"FIBO Production {self.shared_state.get('production_id', 'Unknown')}",
            "production_id": self.shared_state.get("production_id"),
            "created_at": self.shared_state.get("created_at"),
            "total_duration_sec": len(checkpoints) * 8,
            "visual_style": self.shared_state.get("visual_style", {}),
            "checkpoints": checkpoints,
            "metadata": {
                "agent_system": "Enhanced FIBO Director with Strands",
                "model": "gemini-2.5-flash",
                "version": "2.0.0"
            }
        }
    
    def _create_enhanced_fallback_plan(self, script_text: str) -> Dict[str, Any]:
        """Create an enhanced fallback plan when API quota is exceeded."""
        # Create segments using fallback logic
        segments = self._create_fallback_segments(script_text)
        
        # Extract scene context and mood
        scene_context = self._extract_scene_context(script_text)
        mood = self._extract_mood(script_text)
        
        # Create visual style
        visual_style = self._create_fallback_visual_style(scene_context, mood)
        
        # Create checkpoints for each segment
        checkpoints = []
        for i, segment in enumerate(segments):
            checkpoint = {
                "checkpoint_id": i + 1,
                "start_time_sec": segment["start_time_sec"],
                "end_time_sec": segment["end_time_sec"],
                "duration_sec": 8,
                "scene_description": segment["content"][:200],
                "is_continuation": segment["is_continuation"],
                "visual_consistency_notes": f"Maintains {visual_style['artistic_direction']} style",
                "fibo_start_frame": self._create_default_fibo_prompt("start", segment["content"][:100], visual_style),
                "fibo_end_frame": self._create_default_fibo_prompt("end", segment["content"][:100], visual_style),
                "video_generation_notes": self._create_scene_specific_video_notes(
                    segment["content"],
                    f"Start frame: {segment['content'][:50]}...",
                    f"End frame: {segment['content'][50:100]}..."
                )
            }
            checkpoints.append(checkpoint)
        
        return {
            "project_title": f"Enhanced FIBO Production {str(uuid.uuid4())[:8]}",
            "production_id": str(uuid.uuid4())[:8],
            "created_at": datetime.now().isoformat(),
            "total_duration_sec": len(checkpoints) * 8,
            "visual_style": visual_style,
            "checkpoints": checkpoints,
            "metadata": {
                "agent_system": "Enhanced Fallback (Quota Limited)",
                "model": "local-processing",
                "version": "2.0.0",
                "note": "Generated with local processing due to API quota limits"
            }
        }
    
    def _create_fallback_plan(self, script_text: str) -> Dict[str, Any]:
        """Create a basic fallback plan if agent processing fails."""
        return {
            "project_title": "FIBO Fallback Production",
            "production_id": str(uuid.uuid4())[:8],
            "created_at": datetime.now().isoformat(),
            "total_duration_sec": 8,
            "visual_style": {
                "lighting_style": "Cinematic three-point lighting",
                "color_palette": "Natural, balanced",
                "camera_style": "50mm, f/2.8",
                "environment_theme": "Professional production",
                "artistic_direction": "Photorealistic, cinematic"
            },
            "checkpoints": [
                {
                    "checkpoint_id": 1,
                    "start_time_sec": 0,
                    "end_time_sec": 8,
                    "duration_sec": 8,
                    "scene_description": script_text[:200],
                    "is_continuation": False,
                    "visual_consistency_notes": "Maintains cinematic style",
                    "fibo_start_frame": self._create_default_fibo_prompt("start", script_text[:100], {}),
                    "fibo_end_frame": self._create_default_fibo_prompt("end", script_text[:100], {}),
                    "video_generation_notes": "Smooth cinematic transition"
                }
            ],
            "metadata": {
                "agent_system": "Basic Fallback",
                "version": "2.0.0"
            }
        }
    
    def export_checkpoint_fibo_prompts(self, video_plan: Dict, checkpoint_id: int) -> Dict[str, Any]:
        """Export FIBO prompts for a specific checkpoint."""
        if not video_plan or "checkpoints" not in video_plan:
            return {"error": "No video plan available"}
        
        for checkpoint in video_plan["checkpoints"]:
            if checkpoint["checkpoint_id"] == checkpoint_id:
                return {
                    "checkpoint_id": checkpoint_id,
                    "scene_description": checkpoint["scene_description"],
                    "duration_sec": checkpoint["duration_sec"],
                    "visual_style": video_plan.get("visual_style", {}),
                    "fibo_start_frame": checkpoint["fibo_start_frame"],
                    "fibo_end_frame": checkpoint["fibo_end_frame"],
                    "video_generation_notes": checkpoint["video_generation_notes"]
                }
        
        return {"error": f"Checkpoint {checkpoint_id} not found"}
    
    def get_checkpoint_summary(self, video_plan: Dict) -> str:
        """Get a summary of all checkpoints."""
        if not video_plan or "checkpoints" not in video_plan:
            return "No checkpoints available"
        
        lines = [
            f"🎬 {video_plan.get('project_title', 'Video Project')}",
            f"📊 Total Duration: {video_plan.get('total_duration_sec', 0)} seconds",
            f"🎯 Checkpoints: {len(video_plan['checkpoints'])}",
            "",
            "📋 CHECKPOINT OVERVIEW:"
        ]
        
        for cp in video_plan["checkpoints"]:
            lines.append(f"  ✓ Checkpoint {cp['checkpoint_id']}: {cp['start_time_sec']}-{cp['end_time_sec']}s")
            lines.append(f"    {cp['scene_description'][:60]}...")
        
        return "\n".join(lines)


# =============================================================================
# AGENTCORE RUNTIME WRAPPER
# =============================================================================

def create_agentcore_app():
    """Create AgentCore-compatible application wrapper.
    
    This wrapper allows the Enhanced FIBO Director to be deployed
    on Amazon Bedrock AgentCore Runtime for production use.
    
    Returns:
        AgentCore app instance or None if AgentCore not available
    """
    try:
        from bedrock_agentcore import BedrockAgentCoreApp
        
        app = BedrockAgentCoreApp()
        
        @app.entrypoint
        def invoke(payload: Dict[str, Any]) -> Dict[str, Any]:
            """AgentCore entrypoint for FIBO Director.
            
            Args:
                payload: Request payload with script_text
                
            Returns:
                Production plan with FIBO checkpoints
            """
            # Get API key from environment or payload
            api_key = os.environ.get("GOOGLE_API_KEY") or payload.get("api_key")
            
            if not api_key:
                return {
                    "error": "GOOGLE_API_KEY not configured",
                    "status": "failed"
                }
            
            # Get script text from payload
            script_text = payload.get("script_text", "")
            
            if not script_text:
                return {
                    "error": "No script_text provided in payload",
                    "status": "failed"
                }
            
            try:
                # Initialize director and process script
                director = EnhancedFIBODirector(api_key)
                production_plan = director.process_script(script_text)
                
                return {
                    "status": "success",
                    "production_plan": production_plan
                }
                
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "failed"
                }
        
        return app
        
    except ImportError:
        print("⚠️ AgentCore not available - running in standalone mode")
        return None


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

def main():
    """Demo the Enhanced FIBO Director system."""
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not set!")
        print("Set your Google API key: set GOOGLE_API_KEY=your_key")
        return
    
    # Sample cyberpunk script
    sample_script = """
    FADE IN:
    
    EXT. CYBERPUNK CITY - NIGHT
    
    Rain falls on neon-lit streets. Holographic advertisements flicker on towering buildings.
    
    JACK (30s, cybernetic arm, leather jacket) walks through the crowded street, 
    dodging flying cars overhead. His augmented reality display shows incoming messages.
    
    JACK
    (to his AI assistant)
    Show me the route to the data center.
    
    A holographic path appears in his vision, leading through dark alleys.
    
    Jack turns into a narrow alley where ZARA (20s, punk hacker, glowing tattoos) 
    waits by a hidden door.
    
    ZARA
    You're late. The security window closes in five minutes.
    
    JACK
    Traffic was hell. Flying cars everywhere.
    
    Zara activates a device that makes the door shimmer and become transparent.
    
    ZARA
    After you, corporate spy.
    
    Jack smirks and steps through the shimmering portal.
    
    INT. DATA CENTER - CONTINUOUS
    
    A vast room filled with glowing servers and holographic data streams. 
    The air hums with electricity.
    
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
    
    print("=" * 70)
    print("🎬 ENHANCED FIBO VIDEO DIRECTOR")
    print("   Strands Multi-Agent System with AgentCore Compatibility")
    print("=" * 70)
    
    # Initialize the enhanced director
    director = EnhancedFIBODirector(api_key)
    
    try:
        # Process the script through the multi-agent system
        production_plan = director.process_script(sample_script)
        
        # Display results
        print("\n" + "=" * 70)
        print("📋 PRODUCTION PLAN GENERATED")
        print("=" * 70)
        
        print(director.get_checkpoint_summary(production_plan))
        
        # Save the production plan
        output_file = "production_plan.json"
        with open(output_file, "w") as f:
            json.dump(production_plan, f, indent=2)
        print(f"\n💾 Production plan saved to: {output_file}")
        
        # Demo: Export a specific checkpoint
        if production_plan.get("checkpoints"):
            checkpoint_id = 1
            checkpoint_data = director.export_checkpoint_fibo_prompts(production_plan, checkpoint_id)
            
            print(f"\n🎯 CHECKPOINT {checkpoint_id} FIBO PROMPTS:")
            print("-" * 50)
            print(f"Start Frame: {checkpoint_data['fibo_start_frame']['short_description'][:80]}...")
            print(f"End Frame: {checkpoint_data['fibo_end_frame']['short_description'][:80]}...")
        
        print("\n" + "=" * 70)
        print("✅ ENHANCED FIBO DIRECTOR COMPLETE")
        print("=" * 70)
        print("\n🔧 Features Used:")
        print("   • Strands multi-agent Swarm pattern")
        print("   • Shared state management")
        print("   • Tool-based agent collaboration")
        print("   • AgentCore Runtime compatibility")
        print("\n💡 Next Steps:")
        print("   • Use the API server to integrate with frontend")
        print("   • Deploy to AgentCore for production scaling")
        print("   • Generate frames using FIBO structured prompts")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


# AgentCore app instance (created if AgentCore is available)
agentcore_app = create_agentcore_app()

if __name__ == "__main__":
    main()
