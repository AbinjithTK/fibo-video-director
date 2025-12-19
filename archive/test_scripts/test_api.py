#!/usr/bin/env python3
"""
Test the Simple FIBO API Server
"""

import requests
import json
import time

def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Simple FIBO API Server")
    print("=" * 50)
    
    # Test health check
    print("1. Testing health check...")
    response = requests.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()['message']}")
    
    # Test generate plan
    print("\n2. Testing generate plan...")
    script_data = {
        "script_text": """
        A cyberpunk hacker named Jack walks through neon-lit streets.
        Rain falls as holographic ads flicker on towering buildings.
        He meets Zara, a punk hacker with glowing tattoos.
        They enter a data center filled with glowing servers.
        Alarms blare as they download consciousness files.
        """
    }
    
    response = requests.post(f"{base_url}/api/generate-plan", json=script_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        plan_data = response.json()
        project_id = plan_data['project_id']
        print(f"   ✅ Project created: {plan_data['project_title']}")
        print(f"   📊 Duration: {plan_data['total_duration_sec']} seconds")
        print(f"   🎯 Checkpoints: {len(plan_data['checkpoints'])}")
        
        # Test get project
        print(f"\n3. Testing get project...")
        response = requests.get(f"{base_url}/api/project/{project_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Project retrieved successfully")
        
        # Test get checkpoint
        print(f"\n4. Testing get checkpoint...")
        response = requests.get(f"{base_url}/api/checkpoint/{project_id}/1")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            checkpoint_data = response.json()
            print(f"   ✅ Checkpoint retrieved: {checkpoint_data['scene_description'][:60]}...")
            print(f"   🎨 Start frame: {checkpoint_data['fibo_start_frame']['short_description'][:60]}...")
        
        # Test generate frames
        print(f"\n5. Testing generate frames...")
        frame_data = {
            "project_id": project_id,
            "checkpoint_id": 1
        }
        response = requests.post(f"{base_url}/api/generate-frames", json=frame_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            gen_data = response.json()
            generation_id = gen_data['generation_id']
            print(f"   ✅ Frame generation started: {generation_id}")
            
            # Wait and check status
            print(f"   ⏳ Waiting for generation...")
            time.sleep(3)
            
            response = requests.get(f"{base_url}/api/generation-status/{generation_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   📊 Status: {status_data['status']}")
                print(f"   💬 Message: {status_data['message']}")
                if status_data.get('start_frame_url'):
                    print(f"   🖼️ Start frame: {status_data['start_frame_url']}")
                if status_data.get('end_frame_url'):
                    print(f"   🖼️ End frame: {status_data['end_frame_url']}")
    
    print("\n" + "=" * 50)
    print("✅ API test complete!")

if __name__ == "__main__":
    test_api()