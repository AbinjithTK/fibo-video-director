#!/usr/bin/env python3
"""
AgentCore Client Integration for FIBO Video Director

This module provides integration with the deployed AgentCore agent
to process movie scripts and generate FIBO video production plans.
"""

import os
import json
import boto3
from typing import Dict, Any, Optional
from datetime import datetime


class AgentCoreClient:
    """Client for interacting with the deployed AgentCore FIBO agent."""
    
    def __init__(self, agent_arn: str, region: str = "us-east-1"):
        """
        Initialize AgentCore client.
        
        Args:
            agent_arn: The ARN of the deployed AgentCore agent
            region: AWS region where the agent is deployed
        """
        self.agent_arn = agent_arn
        self.region = region
        
        # Initialize Bedrock AgentCore client
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)
        
        # Get API key from environment
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required for AgentCore agent")
    
    async def process_script(self, script_text: str) -> Dict[str, Any]:
        """
        Process a movie script using the AgentCore agent.
        
        Args:
            script_text: The movie script to process
            
        Returns:
            Dict containing the video production plan with checkpoints
        """
        try:
            # Prepare payload for AgentCore agent
            payload = {
                "script_text": script_text,
                "api_key": self.api_key
            }
            
            print(f"🤖 Calling AgentCore agent: {self.agent_arn}")
            
            # Call the AgentCore agent
            response = self.client.invoke_agent(
                agentId=self.agent_arn.split('/')[-1],  # Extract agent ID from ARN
                agentAliasId='TSTALIASID',  # Default test alias
                sessionId=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                inputText=json.dumps(payload)
            )
            
            # Process the response
            result = self._process_agent_response(response)
            
            print(f"✅ AgentCore agent completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ AgentCore agent error: {e}")
            raise Exception(f"AgentCore processing failed: {str(e)}")
    
    def _process_agent_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the response from AgentCore agent.
        
        Args:
            response: Raw response from AgentCore
            
        Returns:
            Processed video production plan
        """
        try:
            # Extract the response text from AgentCore
            if 'completion' in response:
                response_text = response['completion']
            elif 'output' in response:
                response_text = response['output']
            else:
                # Handle streaming response
                response_text = ""
                for event in response.get('completion', []):
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            response_text += chunk['bytes'].decode('utf-8')
            
            # Try to parse as JSON first
            try:
                parsed_response = json.loads(response_text)
                if isinstance(parsed_response, dict) and 'status' in parsed_response:
                    if parsed_response['status'] == 'success':
                        return parsed_response.get('response', parsed_response)
                    else:
                        raise Exception(parsed_response.get('message', 'Agent returned error status'))
            except json.JSONDecodeError:
                pass
            
            # If not JSON, try to extract JSON from text response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            
            # If no JSON found, create a structured response from text
            return self._create_structured_response(response_text)
            
        except Exception as e:
            print(f"⚠️ Error processing agent response: {e}")
            return self._create_fallback_response(str(e))
    
    def _create_structured_response(self, response_text: str) -> Dict[str, Any]:
        """
        Create a structured response from agent text output.
        
        Args:
            response_text: Raw text response from agent
            
        Returns:
            Structured video production plan
        """
        # Parse the text response and create a basic structure
        lines = response_text.split('\n')
        
        # Look for key information in the response
        project_title = "FIBO Video Production"
        checkpoints = []
        
        # Try to extract segments/checkpoints from the response
        segment_count = 1
        for line in lines:
            if 'segment' in line.lower() or 'checkpoint' in line.lower():
                segment_count += 1
        
        # Create basic checkpoints structure
        for i in range(max(1, segment_count - 1)):
            checkpoint = {
                "checkpoint_id": i + 1,
                "start_time_sec": i * 8,
                "end_time_sec": (i + 1) * 8,
                "duration_sec": 8,
                "scene_description": f"Scene {i + 1} from agent analysis",
                "is_continuation": i > 0,
                "visual_consistency_notes": "Maintains cinematic style",
                "fibo_start_frame": self._create_default_fibo_prompt(f"start_{i+1}", "Scene opening"),
                "fibo_end_frame": self._create_default_fibo_prompt(f"end_{i+1}", "Scene closing"),
                "video_generation_notes": "Smooth cinematic transition"
            }
            checkpoints.append(checkpoint)
        
        return {
            "project_title": project_title,
            "production_id": f"agentcore_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "total_duration_sec": len(checkpoints) * 8,
            "visual_style": {
                "lighting_style": "Cinematic three-point lighting",
                "color_palette": "Natural, balanced",
                "camera_style": "50mm, f/2.8",
                "environment_theme": "Professional production",
                "artistic_direction": "Photorealistic, cinematic"
            },
            "checkpoints": checkpoints,
            "metadata": {
                "agent_system": "AgentCore FIBO Director",
                "model": "gemini-2.5-flash",
                "version": "1.0.0",
                "raw_response": response_text[:500] + "..." if len(response_text) > 500 else response_text
            }
        }
    
    def _create_default_fibo_prompt(self, frame_type: str, scene_content: str) -> Dict[str, Any]:
        """Create a default FIBO structured prompt."""
        return {
            "short_description": f"{frame_type}: {scene_content}",
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
            "background_setting": scene_content,
            "lighting": "Cinematic lighting",
            "aesthetics": {
                "composition": "Rule of thirds",
                "color_scheme": "Natural",
                "mood_atmosphere": "Cinematic"
            },
            "photographic_characteristics": {
                "depth_of_field": "Cinematic shallow DOF",
                "camera_angle": "Eye-level",
                "lens_focal_length": "50mm"
            },
            "style_medium": "Photorealistic, cinematic"
        }
    
    def _create_fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Create a fallback response when agent processing fails."""
        return {
            "project_title": "FIBO Fallback Production",
            "production_id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
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
                    "scene_description": "Fallback scene due to agent processing error",
                    "is_continuation": False,
                    "visual_consistency_notes": "Maintains cinematic style",
                    "fibo_start_frame": self._create_default_fibo_prompt("start", "Scene opening"),
                    "fibo_end_frame": self._create_default_fibo_prompt("end", "Scene closing"),
                    "video_generation_notes": "Smooth cinematic transition"
                }
            ],
            "metadata": {
                "agent_system": "Fallback mode",
                "version": "1.0.0",
                "error": error_message
            }
        }


# AgentCore configuration
AGENTCORE_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:476114109859:runtime/src_main-PQhMz74UaU"
AGENTCORE_REGION = "us-east-1"


def create_agentcore_client() -> AgentCoreClient:
    """Create and return an AgentCore client instance."""
    return AgentCoreClient(
        agent_arn=AGENTCORE_AGENT_ARN,
        region=AGENTCORE_REGION
    )