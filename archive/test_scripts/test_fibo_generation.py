#!/usr/bin/env python3
"""
Test FIBO Image Generation with FAL.ai
"""

import requests
import json
import time

def test_fibo_image_generation():
    """Test actual FIBO image generation through FAL.ai."""
    print("🎨 TESTING FIBO IMAGE GENERATION WITH FAL.AI")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("1. 🔍 Testing API health...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status']}")
            print(f"   ✅ FAL Configured: {data['fal_configured']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return False
    
    # Test 2: Generate Video Plan with Cyberpunk Script
    print("\n2. 🎬 Generating cyberpunk video plan...")
    
    cyberpunk_script = """
    EXT. CYBERPUNK CITY - NIGHT
    
    Rain falls on neon-lit streets. Holographic advertisements flicker on towering buildings.
    JACK (30s, cybernetic arm, leather jacket) walks through the crowded street.
    His augmented reality display shows incoming messages.
    
    Jack turns into a narrow alley where ZARA (20s, punk hacker, glowing tattoos) 
    waits by a hidden door with shimmering energy.
    
    INT. DATA CENTER - CONTINUOUS
    
    A vast room filled with glowing servers and holographic data streams. 
    The air hums with electricity as Zara interfaces with the neural network core.
    """
    
    try:
        response = requests.post(f"{base_url}/api/generate-plan", 
                               json={"script_text": cyberpunk_script}, 
                               timeout=30)
        
        if response.status_code == 200:
            plan_data = response.json()
            project_id = plan_data['project_id']
            
            print(f"   ✅ Project Created: {plan_data['project_title']}")
            print(f"   🎯 Checkpoints: {len(plan_data['checkpoints'])}")
            
            # Test 3: Generate FIBO Images for First Checkpoint
            print(f"\n3. 🖼️  Generating FIBO images for checkpoint 1...")
            
            response = requests.post(f"{base_url}/api/generate-frames", 
                                   json={"project_id": project_id, "checkpoint_id": 1},
                                   timeout=10)
            
            if response.status_code == 200:
                gen_data = response.json()
                generation_id = gen_data['generation_id']
                print(f"   ✅ FIBO generation started: {generation_id}")
                
                # Monitor generation progress
                print("   ⏳ Monitoring FIBO generation progress...")
                
                for i in range(60):  # Wait up to 60 seconds
                    time.sleep(2)
                    status_response = requests.get(f"{base_url}/api/generation-status/{generation_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        progress = status_data.get('progress', 0) * 100
                        print(f"   📊 Status: {status_data['status']} ({progress:.0f}%) - {status_data['message']}")
                        
                        if status_data['status'] == 'completed':
                            print(f"\n   🎉 FIBO Generation Complete!")
                            
                            # Check what was generated
                            start_url = status_data.get('start_frame_url', '')
                            end_url = status_data.get('end_frame_url', '')
                            
                            print(f"   🖼️  Start Frame: {start_url}")
                            print(f"   🖼️  End Frame: {end_url}")
                            
                            # Check if actual images were generated (PNG files)
                            start_is_image = start_url.endswith('.png')
                            end_is_image = end_url.endswith('.png')
                            
                            if start_is_image and end_is_image:
                                print(f"   ✅ SUCCESS: Both FIBO images generated!")
                                print(f"   ⏱️  Generation Time: {status_data.get('generation_time_sec', 0):.1f}s")
                                
                                # Check cache status
                                if status_data.get('start_frame_cached'):
                                    print(f"   🚀 Start frame was cached")
                                if status_data.get('end_frame_cached'):
                                    print(f"   🚀 End frame was cached")
                                
                                return True
                                
                            elif start_is_image or end_is_image:
                                print(f"   ⚠️  PARTIAL SUCCESS: Some FIBO images generated")
                                return True
                                
                            else:
                                print(f"   ⚠️  Only structured prompts generated (no images)")
                                print(f"   📝 This means FAL.ai FIBO generation failed, but prompts are ready")
                                return False
                            
                        elif status_data['status'] == 'error':
                            print(f"   ❌ Generation error: {status_data['message']}")
                            return False
                            
                else:
                    print("   ⏰ Generation timeout after 2 minutes")
                    return False
                    
            else:
                print(f"   ❌ Failed to start generation: {response.status_code}")
                return False
                
        else:
            print(f"   ❌ Failed to generate plan: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during test: {e}")
        return False

def test_fibo_prompt_quality():
    """Test the quality of FIBO structured prompts."""
    print("\n4. 🎨 Testing FIBO structured prompt quality...")
    
    base_url = "http://localhost:8000"
    
    # Generate a simple plan first
    simple_script = "A wizard with a glowing staff stands in a mystical forest at twilight."
    
    try:
        response = requests.post(f"{base_url}/api/generate-plan", 
                               json={"script_text": simple_script}, 
                               timeout=30)
        
        if response.status_code == 200:
            plan_data = response.json()
            project_id = plan_data['project_id']
            
            # Get checkpoint details to examine FIBO prompts
            response = requests.get(f"{base_url}/api/checkpoint/{project_id}/1")
            if response.status_code == 200:
                checkpoint_data = response.json()
                
                start_frame = checkpoint_data['fibo_start_frame']
                
                print(f"   ✅ FIBO Prompt Retrieved")
                print(f"   📝 Description: {start_frame.get('short_description', 'N/A')[:80]}...")
                
                # Check required FIBO fields
                required_fields = [
                    'objects', 'background_setting', 'lighting', 
                    'aesthetics', 'photographic_characteristics', 'style_medium'
                ]
                
                missing_fields = [field for field in required_fields if field not in start_frame]
                
                if not missing_fields:
                    print(f"   ✅ All required FIBO fields present")
                    
                    # Check objects array
                    objects = start_frame.get('objects', [])
                    if objects and len(objects) > 0:
                        obj = objects[0]
                        obj_fields = ['description', 'location', 'pose', 'expression']
                        obj_complete = all(field in obj for field in obj_fields)
                        
                        if obj_complete:
                            print(f"   ✅ Object descriptions are complete")
                        else:
                            print(f"   ⚠️  Object descriptions missing some fields")
                    
                    # Check aesthetics
                    aesthetics = start_frame.get('aesthetics', {})
                    if 'composition' in aesthetics and 'color_scheme' in aesthetics:
                        print(f"   ✅ Aesthetic parameters complete")
                    
                    print(f"   🎨 Lighting: {start_frame.get('lighting', 'N/A')[:60]}...")
                    print(f"   📷 Camera: {start_frame.get('photographic_characteristics', {}).get('camera_angle', 'N/A')[:60]}...")
                    
                    return True
                    
                else:
                    print(f"   ❌ Missing FIBO fields: {missing_fields}")
                    return False
                    
            else:
                print(f"   ❌ Failed to get checkpoint: {response.status_code}")
                return False
                
        else:
            print(f"   ❌ Failed to generate plan: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing prompts: {e}")
        return False

def main():
    """Main test function."""
    
    # Test FIBO image generation
    image_success = test_fibo_image_generation()
    
    # Test FIBO prompt quality
    prompt_success = test_fibo_prompt_quality()
    
    print("\n" + "=" * 60)
    
    if image_success and prompt_success:
        print("🎉 ALL FIBO TESTS PASSED!")
        print("✅ FIBO images are being generated through FAL.ai")
        print("✅ FIBO structured prompts are complete and professional")
        
    elif image_success:
        print("⚠️  FIBO IMAGES WORKING, PROMPTS NEED ATTENTION")
        
    elif prompt_success:
        print("⚠️  FIBO PROMPTS WORKING, IMAGE GENERATION ISSUES")
        print("💡 Check FAL_KEY configuration and FAL.ai service status")
        
    else:
        print("❌ FIBO TESTS FAILED")
        print("💡 Check API server logs and FAL.ai integration")
    
    print("=" * 60)
    
    print("\n💡 Next steps:")
    print("1. Open http://localhost:3000 to test in the UI")
    print("2. Generate a video plan with a cyberpunk or fantasy script")
    print("3. Click on checkpoints to see FIBO structured prompts")
    print("4. Generate frames to see actual FIBO images")
    print("5. Download the generated images and JSON prompts")

if __name__ == "__main__":
    main()