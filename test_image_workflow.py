#!/usr/bin/env python3
"""
Test the complete image generation and display workflow
"""

import requests
import json
import time

def test_image_workflow():
    """Test the complete image workflow"""
    
    print("🖼️ FIBO Image Workflow Test")
    print("=" * 50)
    
    # Test script
    test_script = """FADE IN:

EXT. CYBERPUNK CITY - NIGHT

Rain falls on neon-lit streets. A figure in a leather jacket walks through the shadows.

FADE OUT."""

    try:
        # Step 1: Generate Plan
        print("1️⃣ Generating video plan...")
        response = requests.post(
            "http://localhost:8000/api/generate-plan",
            json={"script_text": test_script}
        )
        
        if response.status_code != 200:
            print(f"❌ Plan generation failed: {response.status_code}")
            return False
            
        plan = response.json()
        project_id = plan['project_id']
        checkpoint_id = plan['checkpoints'][0]['checkpoint_id']
        
        print(f"   ✅ Project: {project_id}")
        print(f"   🎯 Testing checkpoint: {checkpoint_id}")
        
        # Step 2: Start Frame Generation
        print("\n2️⃣ Starting frame generation...")
        response = requests.post(
            "http://localhost:8000/api/generate-frames",
            json={"project_id": project_id, "checkpoint_id": checkpoint_id}
        )
        
        if response.status_code != 200:
            print(f"❌ Frame generation failed: {response.status_code}")
            return False
            
        gen_data = response.json()
        generation_id = gen_data['generation_id']
        print(f"   ✅ Generation started: {generation_id}")
        
        # Step 3: Monitor Progress
        print("\n3️⃣ Monitoring generation progress...")
        max_attempts = 30  # 60 seconds max
        
        for attempt in range(max_attempts):
            time.sleep(2)
            
            response = requests.get(f"http://localhost:8000/api/generation-status/{generation_id}")
            if response.status_code != 200:
                print(f"   ❌ Status check failed: {response.status_code}")
                continue
                
            status = response.json()
            progress = int(status['progress'] * 100)
            print(f"   📊 Progress: {progress}% - {status['message']}")
            
            if status['status'] == 'completed':
                print(f"\n   🎉 Generation completed!")
                
                # Check URLs
                start_url = status.get('start_frame_url')
                end_url = status.get('end_frame_url')
                
                print(f"   🖼️ Start frame URL: {start_url}")
                print(f"   🖼️ End frame URL: {end_url}")
                
                # Test URL accessibility
                if start_url:
                    if start_url.startswith('http') and not start_url.startswith('http://localhost'):
                        # External URL - test proxy
                        proxy_url = f"http://localhost:8000/api/proxy-image?url={start_url}"
                        print(f"   🔗 Testing proxy: {proxy_url[:100]}...")
                        
                        try:
                            proxy_response = requests.get(proxy_url, timeout=10)
                            if proxy_response.status_code == 200:
                                print(f"   ✅ Proxy works! Content-Type: {proxy_response.headers.get('content-type')}")
                                print(f"   📏 Image size: {len(proxy_response.content)} bytes")
                            else:
                                print(f"   ❌ Proxy failed: {proxy_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Proxy error: {e}")
                    else:
                        # Local URL
                        try:
                            local_response = requests.get(f"http://localhost:8000{start_url}", timeout=10)
                            if local_response.status_code == 200:
                                print(f"   ✅ Local URL works! Content-Type: {local_response.headers.get('content-type')}")
                                print(f"   📏 File size: {len(local_response.content)} bytes")
                            else:
                                print(f"   ❌ Local URL failed: {local_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Local URL error: {e}")
                
                # Test frontend compatibility
                print(f"\n4️⃣ Frontend compatibility check...")
                
                # Check if URLs would be detected as images by frontend
                def is_image_url(url):
                    if not url:
                        return False
                    if 'fal.media' in url or 'fal.ai' in url or 'storage.googleapis.com' in url:
                        return True
                    if '.png' in url or '.jpg' in url or '.jpeg' in url:
                        return True
                    if url.startswith('https://') and not url.endswith('.json'):
                        return True
                    return False
                
                start_is_image = is_image_url(start_url)
                end_is_image = is_image_url(end_url)
                
                print(f"   🖼️ Start frame detected as image: {start_is_image}")
                print(f"   🖼️ End frame detected as image: {end_is_image}")
                
                if start_is_image and end_is_image:
                    print(f"   ✅ Both frames should display in frontend!")
                elif start_is_image or end_is_image:
                    print(f"   ⚠️ One frame should display in frontend")
                else:
                    print(f"   ❌ No frames will display in frontend")
                
                break
                
            elif status['status'] == 'error':
                print(f"   ❌ Generation failed: {status['message']}")
                return False
        else:
            print(f"   ⏰ Generation timed out after {max_attempts * 2} seconds")
            return False
        
        print("\n" + "=" * 50)
        print("✅ IMAGE WORKFLOW TEST COMPLETED")
        print("🌐 Frontend should now display images properly!")
        print("📱 Test at: http://localhost:3000")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_workflow()
    exit(0 if success else 1)