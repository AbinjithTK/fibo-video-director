#!/usr/bin/env python3
"""
Fixed AgentCore Client Integration for FIBO Video Director

This module provides integration using Gemini directly since AgentCore has API compatibility issues.
"""

import os
import json
from typing import Dict, Any
from datetime import datetime
import google.generativeai as genai


class AgentCoreClient:
    """Client for processing scripts using Gemini 2.5 Flash directly."""
    
    def __init__(self, agent_arn: str = None, region: str = "us-east-1"):
        """
        Initialize AgentCore client.
        
        Args:
            agent_arn: Not used in this implementation
            region: Not used in this implementation
        """
        # Get API key from environment
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Gemini FIBO Director initialized")
    
    async def process_script(self, script_text: str) -> Dict[str, Any]:
        """
        Process a movie script using Gemini 2.5 Flash.
        
        Args:
            script_text: The movie script to process
            
        Returns:
            Dict containing the video production plan with checkpoints
        """
        try:
            print(f"🤖 Processing script with Gemini 2.5 Flash")
            
            # Create a comprehensive prompt for video production planning
            prompt = f"""You are a professional video director and FIBO AI specialist. Analyze this movie script and create a detailed video production plan.

Script:
{script_text}

Create a JSON response with this exact structure:
{{
  "project_title": "Creative title for this video production",
  "production_id": "gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
  "created_at": "{datetime.now().isoformat()}",
  "total_duration_sec": 16,
  "visual_style": {{
    "lighting_style": "Cinematic three-point lighting with dramatic shadows",
    "color_palette": "Natural, cinematic color grading",
    "camera_style": "Professional 50mm lens, f/2.8 aperture",
    "environment_theme": "Cinematic production environment",
    "artistic_direction": "Photorealistic, high production value"
  }},
  "checkpoints": [
    {{
      "checkpoint_id": 1,
      "start_time_sec": 0,
      "end_time_sec": 8,
      "duration_sec": 8,
      "scene_description": "Detailed description of the opening scene based on the script",
      "is_continuation": false,
      "visual_consistency_notes": "Visual style and continuity notes",
      "fibo_start_frame": {{
        "short_description": "Brief description of start frame",
        "objects": [
          {{
            "description": "Main subject or character from the script",
            "location": "Position in frame using rule of thirds",
            "relationship": "Relationship to other scene elements",
            "relative_size": "Size relative to frame composition",
            "shape_and_color": "Visual appearance and color details",
            "texture": "Surface texture and material properties",
            "appearance_details": "Specific visual characteristics",
            "pose": "Body position, stance, or gesture",
            "expression": "Facial expression or emotional state",
            "orientation": "Direction facing or body orientation"
          }}
        ],
        "background_setting": "Detailed environment description from script",
        "lighting": "Specific lighting setup and atmospheric mood",
        "aesthetics": {{
          "composition": "Compositional elements and visual framing",
          "color_scheme": "Color palette and visual mood",
          "mood_atmosphere": "Overall emotional tone and atmosphere"
        }},
        "photographic_characteristics": {{
          "depth_of_field": "Depth of field settings and focus points",
          "camera_angle": "Camera position and perspective",
          "lens_focal_length": "Lens specifications and field of view"
        }},
        "style_medium": "Overall visual style and artistic medium"
      }},
      "fibo_end_frame": {{
        "short_description": "Brief description of end frame showing progression",
        "objects": [
          {{
            "description": "Main subject in evolved position",
            "location": "Final position in frame",
            "relationship": "Relationship to scene elements",
            "relative_size": "Size relative to frame",
            "shape_and_color": "Visual appearance",
            "texture": "Surface details and materials",
            "appearance_details": "Visual characteristics",
            "pose": "Final pose or position",
            "expression": "Final expression or mood",
            "orientation": "Final orientation"
          }}
        ],
        "background_setting": "Environment at scene conclusion",
        "lighting": "Lighting at scene end",
        "aesthetics": {{
          "composition": "Final composition",
          "color_scheme": "Consistent color palette",
          "mood_atmosphere": "Concluding emotional tone"
        }},
        "photographic_characteristics": {{
          "depth_of_field": "Final DOF settings",
          "camera_angle": "Final camera position",
          "lens_focal_length": "Consistent lens specifications"
        }},
        "style_medium": "Consistent visual style"
      }},
      "video_generation_notes": "Notes for smooth video transition between start and end frames"
    }},
    {{
      "checkpoint_id": 2,
      "start_time_sec": 8,
      "end_time_sec": 16,
      "duration_sec": 8,
      "scene_description": "Detailed description of the concluding scene from script",
      "is_continuation": true,
      "visual_consistency_notes": "Continuity from previous scene",
      "fibo_start_frame": {{
        "short_description": "Start of second scene",
        "objects": [
          {{
            "description": "Character or subject in second scene",
            "location": "Position maintaining visual flow",
            "relationship": "Connection to previous scene",
            "relative_size": "Appropriate scale",
            "shape_and_color": "Consistent visual style",
            "texture": "Material properties",
            "appearance_details": "Visual details",
            "pose": "Natural positioning",
            "expression": "Appropriate emotion",
            "orientation": "Directional flow"
          }}
        ],
        "background_setting": "Second scene environment",
        "lighting": "Consistent lighting approach",
        "aesthetics": {{
          "composition": "Compositional flow",
          "color_scheme": "Harmonious colors",
          "mood_atmosphere": "Emotional progression"
        }},
        "photographic_characteristics": {{
          "depth_of_field": "Appropriate DOF",
          "camera_angle": "Effective angle",
          "lens_focal_length": "Consistent lens choice"
        }},
        "style_medium": "Consistent style"
      }},
      "fibo_end_frame": {{
        "short_description": "Concluding frame of the production",
        "objects": [
          {{
            "description": "Final subject state",
            "location": "Concluding position",
            "relationship": "Final relationships",
            "relative_size": "Final scale",
            "shape_and_color": "Final appearance",
            "texture": "Final textures",
            "appearance_details": "Final details",
            "pose": "Concluding pose",
            "expression": "Final expression",
            "orientation": "Final orientation"
          }}
        ],
        "background_setting": "Final environment",
        "lighting": "Concluding lighting",
        "aesthetics": {{
          "composition": "Final composition",
          "color_scheme": "Final colors",
          "mood_atmosphere": "Final mood"
        }},
        "photographic_characteristics": {{
          "depth_of_field": "Final DOF",
          "camera_angle": "Final angle",
          "lens_focal_length": "Final lens"
        }},
        "style_medium": "Final style"
      }},
      "video_generation_notes": "Notes for final scene and overall production conclusion"
    }}
  ],
  "metadata": {{
    "agent_system": "Gemini FIBO Director",
    "model": "gemini-2.5-flash",
    "version": "1.0.0"
  }}
}}

Analyze the script carefully and create exactly 2 checkpoints of 8 seconds each. Focus on:
1. Cinematic quality and professional production values
2. Visual continuity between scenes
3. Detailed FIBO prompts that capture the essence of the script
4. Smooth transitions that will generate coherent video content
5. Creative but appropriate project title based on the script content

Return ONLY the JSON response, no additional text."""
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            result = self._parse_gemini_response(response.text, script_text)
            
            print(f"✅ Gemini processing completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Gemini processing error: {e}")
            import traceback
            traceback.print_exc()
            # Return fallback response instead of raising
            return self._create_fallback_response(str(e))
    
    def _parse_gemini_response(self, response_text: str, script_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured video plan."""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                parsed = json.loads(json_text)
                
                # Validate and enhance the parsed response
                return self._validate_and_enhance_plan(parsed, script_text)
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
        
        # Fallback to structured response creation
        return self._create_structured_plan_from_text(response_text, script_text)
    
    def _validate_and_enhance_plan(self, plan: Dict[str, Any], script_text: str) -> Dict[str, Any]:
        """Validate and enhance the parsed plan."""
        # Ensure required fields
        if 'project_title' not in plan:
            plan['project_title'] = 'Gemini FIBO Production'
        
        if 'production_id' not in plan:
            plan['production_id'] = f"gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if 'created_at' not in plan:
            plan['created_at'] = datetime.now().isoformat()
        
        # Ensure visual style
        if 'visual_style' not in plan:
            plan['visual_style'] = self._get_default_visual_style()
        
        # Validate checkpoints
        if 'checkpoints' not in plan or not plan['checkpoints']:
            plan['checkpoints'] = self._create_default_checkpoints()
        
        # Ensure metadata
        if 'metadata' not in plan:
            plan['metadata'] = {
                'agent_system': 'Gemini FIBO Director',
                'model': 'gemini-2.5-flash',
                'version': '1.0.0'
            }
        
        return plan
    
    def _create_structured_plan_from_text(self, response_text: str, script_text: str) -> Dict[str, Any]:
        """Create structured plan from text response."""
        return {
            'project_title': 'Gemini FIBO Production',
            'production_id': f"gemini_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'total_duration_sec': 16,
            'visual_style': self._get_default_visual_style(),
            'checkpoints': self._create_default_checkpoints(),
            'metadata': {
                'agent_system': 'Gemini FIBO Director',
                'model': 'gemini-2.5-flash',
                'version': '1.0.0',
                'raw_response': response_text[:500] + '...' if len(response_text) > 500 else response_text
            }
        }
    
    def _create_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Create a fallback response when processing fails."""
        return {
            'project_title': 'FIBO Fallback Production',
            'production_id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'total_duration_sec': 8,
            'visual_style': self._get_default_visual_style(),
            'checkpoints': [
                {
                    'checkpoint_id': 1,
                    'start_time_sec': 0,
                    'end_time_sec': 8,
                    'duration_sec': 8,
                    'scene_description': 'Fallback scene due to agent processing error',
                    'is_continuation': False,
                    'visual_consistency_notes': 'Maintains cinematic style',
                    'fibo_start_frame': self._create_default_fibo_prompt('start', 'Scene opening'),
                    'fibo_end_frame': self._create_default_fibo_prompt('end', 'Scene closing'),
                    'video_generation_notes': 'Smooth cinematic transition'
                }
            ],
            'metadata': {
                'agent_system': 'Fallback mode',
                'version': '1.0.0',
                'error': error_message
            }
        }
    
    def _get_default_visual_style(self) -> Dict[str, Any]:
        """Get default visual style."""
        return {
            'lighting_style': 'Cinematic three-point lighting',
            'color_palette': 'Natural, balanced colors',
            'camera_style': '50mm lens, f/2.8',
            'environment_theme': 'Professional production environment',
            'artistic_direction': 'Photorealistic, cinematic quality'
        }
    
    def _create_default_checkpoints(self) -> list:
        """Create default checkpoints."""
        return [
            {
                'checkpoint_id': 1,
                'start_time_sec': 0,
                'end_time_sec': 8,
                'duration_sec': 8,
                'scene_description': 'Opening scene with cinematic introduction',
                'is_continuation': False,
                'visual_consistency_notes': 'Maintains cinematic style throughout',
                'fibo_start_frame': self._create_default_fibo_prompt('start', 'Scene opening'),
                'fibo_end_frame': self._create_default_fibo_prompt('end', 'Scene transition'),
                'video_generation_notes': 'Smooth cinematic transition with professional quality'
            },
            {
                'checkpoint_id': 2,
                'start_time_sec': 8,
                'end_time_sec': 16,
                'duration_sec': 8,
                'scene_description': 'Closing scene with dramatic conclusion',
                'is_continuation': True,
                'visual_consistency_notes': 'Maintains visual continuity from previous scene',
                'fibo_start_frame': self._create_default_fibo_prompt('start', 'Scene continuation'),
                'fibo_end_frame': self._create_default_fibo_prompt('end', 'Scene conclusion'),
                'video_generation_notes': 'Dramatic conclusion with cinematic flair'
            }
        ]
    
    def _create_default_fibo_prompt(self, frame_type: str, scene_content: str) -> Dict[str, Any]:
        """Create default FIBO structured prompt."""
        return {
            'short_description': f'{frame_type.title()}: {scene_content}',
            'objects': [
                {
                    'description': 'Main subject from scene analysis',
                    'location': 'Center frame, rule of thirds positioning',
                    'relationship': 'Primary focus of the composition',
                    'relative_size': 'Prominent within frame',
                    'shape_and_color': 'Natural, realistic appearance',
                    'texture': 'Photorealistic surface details',
                    'appearance_details': 'High quality, professional rendering',
                    'pose': 'Natural, contextually appropriate positioning',
                    'expression': 'Contextually appropriate mood',
                    'orientation': 'Camera-facing, engaging composition'
                }
            ],
            'background_setting': scene_content,
            'lighting': 'Cinematic three-point lighting with dramatic shadows',
            'aesthetics': {
                'composition': 'Rule of thirds, balanced framing',
                'color_scheme': 'Natural, harmonious color palette',
                'mood_atmosphere': 'Cinematic, professional mood'
            },
            'photographic_characteristics': {
                'depth_of_field': 'Cinematic shallow depth of field',
                'camera_angle': 'Eye-level, professional framing',
                'lens_focal_length': '50mm equivalent focal length'
            },
            'style_medium': 'Photorealistic, cinematic, high production value'
        }


def create_agentcore_client() -> AgentCoreClient:
    """Create and return an AgentCore client instance."""
    return AgentCoreClient()