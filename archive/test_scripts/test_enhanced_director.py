#!/usr/bin/env python3
"""
Test Enhanced FIBO Director with Strands Agents
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_enhanced_director():
    """Test the Enhanced FIBO Director."""
    print("🎬 Testing Enhanced FIBO Director with Strands")
    print("=" * 60)
    
    try:
        from enhanced_fibo_director import EnhancedFIBODirector
        
        # Get API key
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        # Create enhanced director
        director = EnhancedFIBODirector(api_key)
        print("✅ Enhanced FIBO Director created successfully")
        
        # Test script
        test_script = """
        FADE IN:
        
        EXT. CYBERPUNK CITY - NIGHT
        
        Rain falls on neon-lit streets. Holographic advertisements flicker.
        
        JACK (30s, cybernetic arm) walks through the crowd.
        His augmented reality display shows incoming messages.
        
        JACK
        (to his AI assistant)
        Show me the route to the data center.
        
        A holographic path appears in his vision.
        
        ZARA (20s, punk hacker) waits by a hidden door.
        
        ZARA
        You're late. The security window closes in five minutes.
        
        They approach the shimmering portal.
        
        FADE OUT.
        """
        
        print("\n📝 Processing script with multi-agent system...")
        video_plan = director.process_script(test_script)
        
        print(f"\n✅ Project: {video_plan.get('project_title', 'Unknown')}")
        print(f"📊 Duration: {video_plan.get('total_duration_sec', 0)} seconds")
        print(f"🎯 Checkpoints: {len(video_plan.get('checkpoints', []))}")
        
        if video_plan.get('visual_style'):
            print(f"🎨 Style: {video_plan['visual_style'].get('artistic_direction', 'Unknown')}")
        
        # Test checkpoint export
        if video_plan.get('checkpoints'):
            print("\n📋 Testing checkpoint export...")
            checkpoint_data = director.export_checkpoint_fibo_prompts(video_plan, 1)
            if 'error' not in checkpoint_data:
                print("   ✅ Checkpoint 1 exported successfully")
                print(f"   Scene: {checkpoint_data.get('scene_description', '')[:60]}...")
            else:
                print(f"   ❌ Checkpoint export failed: {checkpoint_data['error']}")
        
        print(f"\n📈 Summary: {director.get_checkpoint_summary(video_plan)}")
        
        print("\n" + "=" * 60)
        print("✅ Enhanced FIBO Director test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Director Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_director()