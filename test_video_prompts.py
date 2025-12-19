#!/usr/bin/env python3
"""
Test the enhanced video generation prompts
"""

import requests
import json

def test_video_prompts():
    """Test that video generation prompts are now scene-specific"""
    
    print("🎬 Testing Enhanced Video Generation Prompts")
    print("=" * 60)
    
    # Test script with varied scenes
    test_script = """FADE IN:

EXT. CYBERPUNK CITY - NIGHT

Rain falls on neon-lit streets. JACK (30s, cybernetic arm) walks quickly through the shadows.

JACK
(urgent, into comm device)
We need to move now. They've found us.

Jack turns into an alley where ZARA (20s, hacker) waits by a glowing portal.

ZARA
(worried)
The security window closes in two minutes.

JACK
(determined)
Then we better hurry.

Zara activates the portal. It shimmers with electric energy.

ZARA
(smiling)
After you, corporate spy.

Jack steps through the portal as alarms begin to wail in the distance.

FADE OUT."""

    try:
        # Generate plan
        print("1️⃣ Generating video plan with enhanced prompts...")
        response = requests.post(
            "http://localhost:8000/api/generate-plan",
            json={"script_text": test_script}
        )
        
        if response.status_code != 200:
            print(f"❌ Plan generation failed: {response.status_code}")
            return False
            
        plan = response.json()
        project_id = plan['project_id']
        
        print(f"   ✅ Project: {project_id}")
        print(f"   📊 Checkpoints: {len(plan['checkpoints'])}")
        
        # Analyze video generation prompts for each checkpoint
        print("\n2️⃣ Analyzing video generation prompts...")
        
        for i, checkpoint in enumerate(plan['checkpoints'], 1):
            checkpoint_id = checkpoint['checkpoint_id']
            
            # Get detailed checkpoint data
            response = requests.get(f"http://localhost:8000/api/checkpoint/{project_id}/{checkpoint_id}")
            if response.status_code == 200:
                details = response.json()
                
                print(f"\n📋 CHECKPOINT {checkpoint_id}:")
                print(f"   Scene: {details['scene_description'][:80]}...")
                
                # Parse video generation notes
                video_notes = details.get('video_generation_notes', '')
                
                if isinstance(video_notes, str):
                    try:
                        video_data = json.loads(video_notes)
                        
                        print(f"   🎥 Camera Work: {video_data.get('camera_work', {}).get('movement', 'N/A')}")
                        
                        # Check for dialogue cues
                        dialogue_cues = video_data.get('dialogue_cues', {})
                        if dialogue_cues.get('spoken_lines'):
                            print(f"   💬 Dialogue: {len(dialogue_cues['spoken_lines'])} lines")
                            for line in dialogue_cues['spoken_lines'][:2]:
                                print(f"      - {line[:60]}...")
                        
                        # Check for action descriptions
                        action_desc = video_data.get('action_description', {})
                        if action_desc.get('character_actions'):
                            print(f"   🎭 Actions: {len(action_desc['character_actions'])} actions")
                            for action in action_desc['character_actions'][:2]:
                                print(f"      - {action[:60]}...")
                        
                        # Check for Veo optimization
                        veo_opt = video_data.get('veo_optimization', {})
                        if veo_opt:
                            print(f"   🤖 Veo Optimized: {veo_opt.get('prompt_style', 'N/A')}")
                        
                        # Check if prompts are unique
                        scene_summary = video_data.get('scene_summary', '')
                        if scene_summary and len(scene_summary) > 50:
                            print(f"   ✅ Scene-specific content detected")
                        else:
                            print(f"   ⚠️ Generic content detected")
                            
                    except json.JSONDecodeError:
                        print(f"   📝 Simple text prompt: {video_notes[:100]}...")
                else:
                    print(f"   📝 Prompt type: {type(video_notes)}")
            else:
                print(f"   ❌ Failed to get checkpoint {checkpoint_id}")
        
        print("\n" + "=" * 60)
        print("✅ VIDEO PROMPT ANALYSIS COMPLETE")
        print("🎯 Check if prompts are now scene-specific with:")
        print("   • Unique dialogue for each scene")
        print("   • Specific character actions")
        print("   • Appropriate camera movements")
        print("   • Veo optimization keywords")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_video_prompts()
    exit(0 if success else 1)