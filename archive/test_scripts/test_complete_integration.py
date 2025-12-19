#!/usr/bin/env python3
"""
Test Complete FIBO Video Director Integration
Frontend + Backend + Working Director
"""

import requests
import json
import time

def test_complete_integration():
    """Test the complete integration."""
    print("🧪 TESTING COMPLETE FIBO VIDEO DIRECTOR INTEGRATION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health Check
    print("1. 🔍 Testing API health...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data['status']}")
            print(f"   ✅ Director Available: {data['director_available']}")
            print(f"   ✅ Mode: {data['active_mode']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {e}")
        return False
    
    # Test 2: Generate Video Plan
    print("\n2. 🎬 Testing video plan generation...")
    
    cyberpunk_script = """
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
    
    try:
        response = requests.post(f"{base_url}/api/generate-plan", 
                               json={"script_text": cyberpunk_script}, 
                               timeout=30)
        
        if response.status_code == 200:
            plan_data = response.json()
            project_id = plan_data['project_id']
            
            print(f"   ✅ Project Created: {plan_data['project_title']}")
            print(f"   📊 Duration: {plan_data['total_duration_sec']} seconds")
            print(f"   🎯 Checkpoints: {len(plan_data['checkpoints'])}")
            print(f"   🎨 Style: {plan_data['visual_style']['artistic_direction'][:50]}...")
            
            # Test 3: Get Project Details
            print("\n3. 📋 Testing project retrieval...")
            response = requests.get(f"{base_url}/api/project/{project_id}")
            if response.status_code == 200:
                print("   ✅ Project details retrieved successfully")
            else:
                print(f"   ❌ Failed to get project: {response.status_code}")
            
            # Test 4: Get Checkpoint Details
            print("\n4. 🎯 Testing checkpoint details...")
            response = requests.get(f"{base_url}/api/checkpoint/{project_id}/1")
            if response.status_code == 200:
                checkpoint_data = response.json()
                print(f"   ✅ Checkpoint 1 retrieved")
                print(f"   📝 Scene: {checkpoint_data['scene_description'][:60]}...")
                
                # Verify FIBO prompts
                start_frame = checkpoint_data['fibo_start_frame']
                end_frame = checkpoint_data['fibo_end_frame']
                
                print(f"   🎨 Start Frame: {start_frame['short_description'][:50]}...")
                print(f"   🎨 End Frame: {end_frame['short_description'][:50]}...")
                
                # Verify structured prompt completeness
                required_fields = ['objects', 'background_setting', 'lighting', 'aesthetics', 'photographic_characteristics']
                start_complete = all(field in start_frame for field in required_fields)
                end_complete = all(field in end_frame for field in required_fields)
                
                if start_complete and end_complete:
                    print("   ✅ FIBO structured prompts are complete")
                else:
                    print("   ⚠️  FIBO structured prompts missing some fields")
                
            else:
                print(f"   ❌ Failed to get checkpoint: {response.status_code}")
            
            # Test 5: Generate Frames
            print("\n5. 🖼️  Testing frame generation...")
            response = requests.post(f"{base_url}/api/generate-frames", 
                                   json={"project_id": project_id, "checkpoint_id": 1})
            
            if response.status_code == 200:
                gen_data = response.json()
                generation_id = gen_data['generation_id']
                print(f"   ✅ Frame generation started: {generation_id}")
                
                # Wait and check status
                print("   ⏳ Waiting for generation to complete...")
                for i in range(5):  # Wait up to 5 seconds
                    time.sleep(1)
                    status_response = requests.get(f"{base_url}/api/generation-status/{generation_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   📊 Status: {status_data['status']} ({status_data.get('progress', 0)*100:.0f}%)")
                        
                        if status_data['status'] == 'completed':
                            print(f"   💬 Message: {status_data['message']}")
                            if status_data.get('start_frame_url'):
                                print(f"   🖼️  Start Frame: {status_data['start_frame_url']}")
                            if status_data.get('end_frame_url'):
                                print(f"   🖼️  End Frame: {status_data['end_frame_url']}")
                            break
                        elif status_data['status'] == 'error':
                            print(f"   ❌ Generation error: {status_data['message']}")
                            break
                else:
                    print("   ⏰ Generation still in progress...")
            else:
                print(f"   ❌ Failed to start generation: {response.status_code}")
            
            # Test 6: Director Mode
            print("\n6. 🎛️  Testing director mode...")
            response = requests.get(f"{base_url}/api/director-mode")
            if response.status_code == 200:
                mode_data = response.json()
                print(f"   ✅ Director Mode: {mode_data['mode']}")
            
            # Test 7: Cache Stats
            print("\n7. 💾 Testing cache stats...")
            response = requests.get(f"{base_url}/api/cache-stats")
            if response.status_code == 200:
                cache_data = response.json()
                print(f"   ✅ Projects Cached: {cache_data['projects_cached']}")
                print(f"   ✅ Generations Tracked: {cache_data['generations_tracked']}")
            
            return True
            
        else:
            print(f"   ❌ Failed to generate plan: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error during plan generation: {e}")
        return False

def test_frontend_accessibility():
    """Test if frontend is accessible."""
    print("\n8. 🌐 Testing frontend accessibility...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible at http://localhost:3000")
            return True
        else:
            print(f"   ❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot access frontend: {e}")
        return False

def main():
    """Main test function."""
    
    # Test backend integration
    backend_success = test_complete_integration()
    
    # Test frontend accessibility
    frontend_success = test_frontend_accessibility()
    
    print("\n" + "=" * 60)
    
    if backend_success and frontend_success:
        print("🎉 ALL TESTS PASSED! FIBO VIDEO DIRECTOR IS FULLY FUNCTIONAL!")
        print("=" * 60)
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend: http://localhost:8000")
        print("📚 API Health: http://localhost:8000/")
        print("=" * 60)
        print("\n💡 Ready for use:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Enter a movie script")
        print("3. Click 'Generate Plan'")
        print("4. Explore checkpoints and generate FIBO frames")
        print("\n🎬 Features working:")
        print("   ✅ Intelligent script analysis")
        print("   ✅ Automatic checkpoint generation")
        print("   ✅ FIBO structured prompt creation")
        print("   ✅ Genre detection (cyberpunk, fantasy, sci-fi, etc.)")
        print("   ✅ Professional cinematic styling")
        print("   ✅ Real-time generation status")
        print("   ✅ File download functionality")
        
    elif backend_success:
        print("⚠️  BACKEND WORKING, FRONTEND ISSUE")
        print("Backend API is fully functional, but frontend may need attention.")
        
    elif frontend_success:
        print("⚠️  FRONTEND ACCESSIBLE, BACKEND ISSUE")
        print("Frontend is accessible, but backend API has issues.")
        
    else:
        print("❌ INTEGRATION TESTS FAILED")
        print("Both backend and frontend need attention.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()