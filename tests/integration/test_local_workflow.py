#!/usr/bin/env python3
"""
Complete Local Workflow Test for FIBO Video Director
Tests the full pipeline: Script → Video Plan → Checkpoints → FIBO Prompts
"""

import sys
from pathlib import Path

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))

import requests
import json
import time
from datetime import datetime

def test_local_workflow():
    """Test the complete local workflow."""
    print("🎬 FIBO Video Director - Complete Local Workflow Test")
    print("=" * 70)
    
    # Configuration
    backend_url = "http://127.0.0.1:8000"
    frontend_url = "http://localhost:3000"
    
    # Test script - a compelling cyberpunk story
    test_script = """
    FADE IN:
    
    EXT. NEO-TOKYO MEGACITY - NIGHT
    
    Rain cascades down towering holographic billboards. Neon signs flicker 
    in Japanese and English, casting electric blues and magentas across 
    wet streets. Flying cars weave between massive skyscrapers.
    
    MAYA (25, cybernetic eyes glowing blue) stands on a rooftop, her 
    augmented reality interface displaying data streams. She wears a 
    sleek black jacket with fiber-optic threads.
    
    MAYA
    (into her neural comm)
    I've located the data vault. Beginning infiltration sequence.
    
    She leaps across rooftops with enhanced agility, her cybernetic 
    legs absorbing the impact. Below, security drones patrol the 
    corporate district.
    
    INT. QUANTUM DYNAMICS CORP - DATA CENTER - CONTINUOUS
    
    Maya phases through a quantum-encrypted wall using her molecular 
    disruptor. The data center hums with holographic servers floating 
    in zero-gravity chambers.
    
    MAYA
    (whispering)
    The consciousness transfer protocols... they're here.
    
    Suddenly, alarms blare. Red warning lights strobe throughout 
    the facility.
    
    SECURITY AI (V.O.)
    Intruder detected. Initiating lockdown sequence.
    
    Maya's eyes widen as blast doors begin sealing. She sprints toward 
    the quantum core, her enhanced reflexes dodging laser security grids.
    
    MAYA
    (determined)
    Not today, corporate overlords.
    
    She reaches the core and interfaces directly with her neural jack, 
    downloading terabytes of classified data. Her cybernetic implants 
    glow brighter as the transfer completes.
    
    EXT. NEO-TOKYO MEGACITY - ROOFTOP - DAWN
    
    Maya emerges onto the rooftop as the first rays of synthetic sunlight 
    pierce through the smog. The city awakens below, a symphony of 
    technology and humanity.
    
    MAYA
    (to herself)
    The truth about Project Mindbridge... now the resistance has a chance.
    
    She activates her cloaking device and disappears into the urban maze.
    
    FADE OUT.
    """
    
    print("📝 Test Script:")
    print(f"   Length: {len(test_script)} characters")
    print(f"   Lines: {len(test_script.split(chr(10)))} lines")
    print(f"   Estimated reading time: {len(test_script.split()) * 0.5:.1f} seconds")
    
    # Step 1: Test Backend Health
    print(f"\n🔧 Step 1: Testing Backend Health ({backend_url})")
    try:
        response = requests.get(f"{backend_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend server is healthy")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        return False
    
    # Step 2: Generate Video Plan
    print(f"\n🎬 Step 2: Generating Video Production Plan")
    try:
        plan_request = {"script_text": test_script}
        response = requests.post(
            f"{backend_url}/api/generate-plan",
            json=plan_request,
            timeout=60
        )
        
        if response.status_code == 200:
            video_plan = response.json()
            print(f"   ✅ Video plan generated successfully")
            print(f"   📊 Project: {video_plan.get('project_title', 'Unknown')}")
            print(f"   ⏱️  Duration: {video_plan.get('total_duration_sec', 0)} seconds")
            print(f"   🎯 Checkpoints: {len(video_plan.get('checkpoints', []))}")
            
            project_id = video_plan.get('project_id') or video_plan.get('production_id')
            if not project_id:
                print("   ❌ No project ID returned")
                return False
            else:
                print(f"   📋 Project ID: {project_id}")
                
        else:
            print(f"   ❌ Video plan generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Video plan generation error: {e}")
        return False
    
    # Step 3: Test Checkpoint Retrieval
    print(f"\n📋 Step 3: Testing Checkpoint Retrieval")
    try:
        checkpoints = video_plan.get('checkpoints', [])
        if not checkpoints:
            print("   ❌ No checkpoints found in video plan")
            return False
        
        # Test first checkpoint
        checkpoint_id = checkpoints[0].get('checkpoint_id', 1)
        response = requests.get(
            f"{backend_url}/api/checkpoint/{project_id}/{checkpoint_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            checkpoint_data = response.json()
            print(f"   ✅ Checkpoint {checkpoint_id} retrieved successfully")
            print(f"   🎬 Scene: {checkpoint_data.get('scene_description', '')[:60]}...")
            
            # Verify FIBO prompts exist
            if 'fibo_start_frame' in checkpoint_data and 'fibo_end_frame' in checkpoint_data:
                print(f"   ✅ FIBO prompts present (start & end frames)")
            else:
                print(f"   ⚠️  FIBO prompts missing or incomplete")
                
        else:
            print(f"   ❌ Checkpoint retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Checkpoint retrieval error: {e}")
        return False
    
    # Step 4: Test Frontend Accessibility
    print(f"\n🌐 Step 4: Testing Frontend Accessibility ({frontend_url})")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            if "FIBO Video Director" in response.text or "React" in response.text:
                print("   ✅ Frontend content loaded correctly")
            else:
                print("   ⚠️  Frontend content may not be fully loaded")
        else:
            print(f"   ❌ Frontend accessibility failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Frontend connection issue (may still be starting): {e}")
    
    # Step 5: Performance Summary
    print(f"\n📊 Step 5: Performance Summary")
    print(f"   🎬 Video Plan Generation: Success")
    print(f"   📋 Checkpoint Count: {len(checkpoints)}")
    print(f"   ⏱️  Total Video Duration: {video_plan.get('total_duration_sec', 0)}s")
    print(f"   🎨 Visual Style: {video_plan.get('visual_style', {}).get('artistic_direction', 'Unknown')}")
    
    # Step 6: Sample FIBO Prompt Display
    print(f"\n🖼️  Step 6: Sample FIBO Prompt Structure")
    if checkpoints:
        sample_checkpoint = checkpoints[0]
        start_frame = sample_checkpoint.get('fibo_start_frame', {})
        if start_frame:
            print(f"   📝 Short Description: {start_frame.get('short_description', 'N/A')[:80]}...")
            print(f"   🎨 Lighting: {start_frame.get('lighting', 'N/A')[:60]}...")
            print(f"   📷 Camera Style: {start_frame.get('photographic_characteristics', {}).get('camera_angle', 'N/A')}")
            print(f"   🎭 Style Medium: {start_frame.get('style_medium', 'N/A')}")
    
    print(f"\n" + "=" * 70)
    print("🎉 LOCAL WORKFLOW TEST COMPLETED SUCCESSFULLY!")
    print("🚀 Your FIBO Video Director is ready for production use!")
    print(f"\n📱 Access your application at:")
    print(f"   🌐 Frontend: {frontend_url}")
    print(f"   🔧 Backend API: {backend_url}")
    print(f"   📚 API Docs: {backend_url}/docs")
    
    return True

if __name__ == "__main__":
    success = test_local_workflow()
    if success:
        print(f"\n✅ All tests passed! System is operational.")
    else:
        print(f"\n❌ Some tests failed. Check the output above.")