#!/usr/bin/env python3
"""
Test the FIBO API to debug the checkpoints issue
"""

import requests
import json

# Test script
test_script = """FADE IN:

EXT. CYBERPUNK CITY - NIGHT

Rain falls on neon-lit streets. Holographic advertisements flicker on towering buildings.

JACK (30s, cybernetic arm, leather jacket) walks through the crowded street, dodging flying cars overhead.

JACK
(to his AI assistant)
Show me the route to the data center.

A holographic path appears in his vision, leading through dark alleys.

FADE OUT."""

def test_generate_plan():
    """Test the generate plan endpoint"""
    print("🧪 Testing FIBO API...")
    
    # Test health check
    response = requests.get("http://localhost:8000/")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test plan generation
    print("\n📝 Testing plan generation...")
    response = requests.post(
        "http://localhost:8000/api/generate-plan",
        json={"script_text": test_script}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        plan = response.json()
        print(f"Project ID: {plan.get('project_id')}")
        print(f"Title: {plan.get('project_title')}")
        print(f"Duration: {plan.get('total_duration_sec')} seconds")
        print(f"Checkpoints: {len(plan.get('checkpoints', []))}")
        
        if plan.get('checkpoints'):
            print("\n✅ Checkpoints found!")
            for i, cp in enumerate(plan['checkpoints'][:2]):  # Show first 2
                print(f"  Checkpoint {cp.get('checkpoint_id')}: {cp.get('scene_description', '')[:50]}...")
        else:
            print("\n❌ No checkpoints found!")
            print("Full response:")
            print(json.dumps(plan, indent=2))
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_generate_plan()