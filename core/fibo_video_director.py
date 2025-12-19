#!/usr/bin/env python3
"""
FIBO Video Director

Core class for processing movie scripts and generating FIBO video production plans.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai


class FIBOVideoDirector:
    """Main director class for FIBO video production planning."""
    
    def __init__(self, google_api_key: str):
        """
        Initialize the FIBO Video Director.
        
        Args:
            google_api_key: Google API key for Gemini
        """
        self.google_api_key = google_api_key
        
        # Configure Gemini
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ FIBO Video Director initialized with Gemini 2.5 Flash")
    
    def create_video_plan(self, script_text: str) -> Dict[str, Any]:
        """
        Create a video production plan from a movie script.
        
        Args:
            script_text: The movie script text
            
        Returns:
            Dict containing the video production plan
        """
        try:
            print(f"📝 Processing script ({len(script_text)} characters)")
            
            # Generate video plan using Gemini
            prompt = self._create_analysis_prompt(script_text)
            response = self.model.generate_content(prompt)
            
            # Parse the response
            video_plan = self._parse_gemini_response(response.text, script_text)
            
            print(f"✅ Video plan created with {len(video_plan.get('checkpoints', []))} checkpoints")
            return video_plan
            
        except Exception as e:
            print(f"❌ Error creating video plan: {e}")
            return self._create_fallback_plan(script_text)
    
    def export_checkpoint_fibo_prompts(self, video_plan: Dict[str, Any], checkpoint_id: int) -> Dict[str, Any]:
        """
        Export FIBO structured prompts for a specific checkpoint.
        
        Args:
            video_plan: The video production plan
            checkpoint_id: The checkpoint ID to export
            
        Returns:
            Dict containing checkpoint data and FIBO prompts
        """
        try:
            # Find the checkpoint
            checkpoint = None
            for cp in video_plan.get('checkpoints', []):
                if cp['checkpoint_id'] == checkpoint_id:
                    checkpoint = cp
                    break
            
            if not checkpoint:
                return {'error': f'Checkpoint {checkpoint_id} not found'}
            
            return {
                'checkpoint_id': checkpoint_id,
                'scene_description': checkpoint.get('scene_description', ''),
                'duration_sec': checkpoint.get('duration_sec', 8),
                'visual_style': video_plan.get('visual_style', {}),
                'fibo_start_frame': checkpoint.get('fibo_start_frame', {}),
                'fibo_end_frame': checkpoint.get('fibo_end_frame', {}),
                'video_generation_notes': checkpoint.get('video_generation_notes', '')
            }
            
        except Exception as e:
            return {'error': f'Error exporting checkpoint: {str(e)}'}
    
    def _create_analysis_prompt(self, script_text: str) -> str:
        """Create analysis prompt for Gemini."""
        return f"""Analyze this movie script and create a detailed video production plan for FIBO generation.

Script:
{script_text}

Please provide a JSON response with this structure:
{{
  "project_title": "Title of the production",
  "production_id": "unique_id",
  "total_duration_sec": 16,
  "visual_style": {{
    "lighting_style": "Cinematic three-point lighting",
    "color_palette": "Natural, balanced colors",
    "camera_style": "50mm lens, f/2.8",
    "environment_theme": "Professional production environment",
    "artistic_direction": "Photorealistic, cinematic quality"
  }},
  "checkpoints": [
    {{
      "checkpoint_id": 1,
      "start_time_sec": 0,
      "end_time_sec": 8,
      "duration_sec": 8,
      "scene_description": "Detailed description of the scene",
      "is_continuation": false,
      "visual_consistency_notes": "Notes about visual consistency",
      "fibo_start_frame": {{
        "short_description": "Brief description of the start frame",
        "objects": [
          {{
            "description": "Main subject or object",
            "location": "Position in frame",
            "relationship": "Relationship to other elements",
            "relative_size": "Size relative to frame",
            "shape_and_color": "Visual appearance",
            "texture": "Surface texture details",
            "appearance_details": "Additional visual details",
            "pose": "Position or pose",
            "expression": "Facial expression or mood",
            "orientation": "Direction facing"
          }}
        ],
        "background_setting": "Description of background and environment",
        "lighting": "Lighting setup and mood",
        "aesthetics": {{
          "composition": "Compositional elements",
          "color_scheme": "Color palette and mood",
          "mood_atmosphere": "Overall mood and atmosphere"
        }},
        "photographic_characteristics": {{
          "depth_of_field": "DOF settings",
          "camera_angle": "Camera position and angle",
          "lens_focal_length": "Lens specifications"
        }},
        "style_medium": "Overall style and medium"
      }},
      "fibo_end_frame": {{
        // Same structure as start_frame but for the end of the scene
      }},
      "video_generation_notes": "Notes for video generation between frames"
    }}
  ],
  "metadata": {{
    "agent_system": "FIBO Video Director",
    "model": "gemini-2.5-flash",
    "version": "1.0.0"
  }}
}}

Create 2 checkpoints of 8 seconds each for a total of 16 seconds. Focus on cinematic quality and smooth transitions between frames."""
    
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
            plan['project_title'] = 'FIBO Video Production'
        
        if 'production_id' not in plan:
            plan['production_id'] = f"fibo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if 'created_at' not in plan:
            plan['created_at'] = datetime.now().isoformat()
        
        # Ensure visual style
        if 'visual_style' not in plan:
            plan['visual_style'] = self._get_default_visual_style()
        
        # Validate checkpoints
        if 'checkpoints' not in plan or not plan['checkpoints']:
            plan['checkpoints'] = self._create_default_checkpoints()
        
        # Ensure each checkpoint has FIBO prompts
        for checkpoint in plan['checkpoints']:
            if 'fibo_start_frame' not in checkpoint:
                checkpoint['fibo_start_frame'] = self._create_default_fibo_prompt(
                    'start', checkpoint.get('scene_description', 'Scene opening')
                )
            if 'fibo_end_frame' not in checkpoint:
                checkpoint['fibo_end_frame'] = self._create_default_fibo_prompt(
                    'end', checkpoint.get('scene_description', 'Scene closing')
                )
        
        return plan
    
    def _create_structured_plan_from_text(self, response_text: str, script_text: str) -> Dict[str, Any]:
        """Create structured plan from text response."""
        return {
            'project_title': 'FIBO Video Production',
            'production_id': f"fibo_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'total_duration_sec': 16,
            'visual_style': self._get_default_visual_style(),
            'checkpoints': self._create_default_checkpoints(),
            'metadata': {
                'agent_system': 'FIBO Video Director',
                'model': 'gemini-2.5-flash',
                'version': '1.0.0',
                'raw_response': response_text[:500] + '...' if len(response_text) > 500 else response_text
            }
        }
    
    def _create_fallback_plan(self, script_text: str) -> Dict[str, Any]:
        """Create fallback plan when Gemini fails."""
        return {
            'project_title': 'FIBO Fallback Production',
            'production_id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'created_at': datetime.now().isoformat(),
            'total_duration_sec': 16,
            'visual_style': self._get_default_visual_style(),
            'checkpoints': self._create_default_checkpoints(),
            'metadata': {
                'agent_system': 'Fallback Director',
                'version': '1.0.0',
                'script_length': len(script_text)
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
    
    def _create_default_checkpoints(self) -> List[Dict[str, Any]]:
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