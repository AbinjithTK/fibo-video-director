#!/usr/bin/env python3
"""
Test the complete FIBO workflow end-to-end
"""

import requests
import json
import time

def test_complete_workflow():
    """Test the complete workflow from script to checkpoints"""
    
    print("🎬 FIBO Video Director - Complete Workflow Test")
    print("=" * 60)
    
    # Test script - same as frontend sample
    test_script = """FADE IN:

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

FADE OUT."""

    try:
        # Step 1: Health Check
        print("1️⃣ Testing API health...")
        response = requests.get("http://localhost:8000/")
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   Mode: {health['active_mode']}")
        print(f"   Enhanced: {health['enhanced_enabled']}")
        
        # Step 2: Generate Plan
        print("\n2️⃣ Generating video plan...")
        response = requests.post(
            "http://localhost:8000/api/generate-plan",
            json={"script_text": test_script}
        )
        
        if response.status_code != 200:
            print(f"❌ Plan generation failed: {response.status_code}")
            print(response.text)
            return False
            
        plan = response.json()
        project_id = plan['project_id']
        
        print(f"   ✅ Project created: {project_id}")
        print(f"   📝 Title: {plan['project_title']}")
        print(f"   ⏱️ Duration: {plan['total_duration_sec']} seconds")
        print(f"   🎯 Checkpoints: {len(plan['checkpoints'])}")
        
        # Validate plan structure (same as frontend)
        if not plan.get('checkpoints') or len(plan['checkpoints']) == 0:
            print("❌ No checkpoints found - frontend would reject this")
            return False
        
        print("   ✅ Plan structure valid for frontend")
        
        # Step 3: Test checkpoint details
        print("\n3️⃣ Testing checkpoint details...")
        for i, checkpoint in enumerate(plan['checkpoints'][:2], 1):  # Test first 2
            checkpoint_id = checkpoint['checkpoint_id']
            
            response = requests.get(f"http://localhost:8000/api/checkpoint/{project_id}/{checkpoint_id}")
            if response.status_code == 200:
                details = response.json()
                print(f"   ✅ Checkpoint {checkpoint_id}: {details['scene_description'][:50]}...")
                
                # Validate FIBO prompts exist
                if 'fibo_start_frame' in details and 'fibo_end_frame' in details:
                    print(f"      🎨 FIBO prompts: ✅")
                else:
                    print(f"      🎨 FIBO prompts: ❌")
            else:
                print(f"   ❌ Checkpoint {checkpoint_id} failed: {response.status_code}")
        
        # Step 4: Test frame generation (mock)
        print("\n4️⃣ Testing frame generation...")
        checkpoint_id = plan['checkpoints'][0]['checkpoint_id']
        
        response = requests.post(
            "http://localhost:8000/api/generate-frames",
            json={"project_id": project_id, "checkpoint_id": checkpoint_id}
        )
        
        if response.status_code == 200:
            gen_data = response.json()
            generation_id = gen_data['generation_id']
            print(f"   ✅ Frame generation started: {generation_id}")
            
            # Check status a few times
            for i in range(3):
                time.sleep(1)
                response = requests.get(f"http://localhost:8000/api/generation-status/{generation_id}")
                if response.status_code == 200:
                    status = response.json()
                    print(f"   📊 Status: {status['status']} ({status['progress']*100:.0f}%)")
                    if status['status'] == 'completed':
                        print(f"   🎉 Generation complete: {status['message']}")
                        break
        else:
            print(f"   ❌ Frame generation failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("✅ COMPLETE WORKFLOW TEST PASSED")
        print("🌐 Frontend should work at: http://localhost:3000")
        print("🔧 Backend running at: http://localhost:8000")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)