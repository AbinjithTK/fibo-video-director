#!/usr/bin/env python3
"""
FIBO Checkpoint Interface

Interactive interface for managing FIBO video generation checkpoints.
Users can select specific checkpoints and generate FIBO structured prompts.
"""

import os
import json
from pathlib import Path
from fibo_video_director import FIBOVideoDirector

class FIBOCheckpointInterface:
    """Interactive interface for FIBO checkpoint management."""
    
    def __init__(self, api_key: str):
        """Initialize the interface."""
        self.director = FIBOVideoDirector(api_key)
        self.current_video_plan = None
    
    def load_sample_scripts(self):
        """Load sample scripts for testing."""
        return {
            "cyberpunk_heist": """
FADE IN:

EXT. NEON CITY - NIGHT

Rain reflects neon signs on wet streets. MAYA (30s, cybernetic eye, leather coat) approaches a towering corporate building.

MAYA
(into comm device)
Beginning infiltration. Wish me luck.

She walks toward the entrance. Automatic doors slide open.

INT. CORPORATE LOBBY - CONTINUOUS

Pristine white lobby with holographic receptionists. Maya shows her badge.

HOLOGRAM
Welcome, Detective. How may we assist you?

Maya's expression hardens as she realizes something is wrong.

FADE OUT.
            """,
            
            "space_adventure": """
FADE IN:

INT. SPACESHIP BRIDGE - DAY

Captain SARAH (40s, uniform) grips her chair as the ship shakes violently.

SARAH
(shouting)
Damage report!

TORRES (30s, engineer) works frantically at his console.

TORRES
Hull breach on deck seven! We're losing atmosphere!

Through the viewscreen, a massive alien vessel approaches.

SARAH
(whispered)
What is that thing?

The alien ship charges its weapons. A brilliant energy beam streaks toward them.

FADE OUT.
            """,
            
            "fantasy_quest": """
FADE IN:

EXT. ENCHANTED FOREST - DAY

Sunlight filters through ancient trees. ELENA (25, ranger, bow) tracks mysterious footprints.

ELENA
(to herself)
These tracks... they're not human.

A rustling in the bushes. She draws her bow, arrow nocked.

A DRAGON HATCHLING (small, iridescent scales) emerges, injured and afraid.

ELENA
(softening)
Hey there, little one. I won't hurt you.

She slowly approaches, hand extended. The hatchling sniffs cautiously.

ELENA
Where's your mother?

A thunderous ROAR echoes through the forest. Both Elena and the hatchling look up in alarm.

FADE OUT.
            """
        }
    
    def create_video_plan(self, script_text: str) -> bool:
        """Create a new video plan from script."""
        try:
            print("🎬 Creating FIBO video plan...")
            print("⏳ Analyzing script and generating checkpoints...")
            
            self.current_video_plan = self.director.create_video_plan(script_text)
            
            if self.current_video_plan:
                print("✅ Video plan created successfully!")
                return True
            else:
                print("❌ Failed to create video plan")
                return False
                
        except Exception as e:
            print(f"❌ Error creating video plan: {e}")
            return False
    
    def show_checkpoint_overview(self):
        """Display overview of all checkpoints."""
        if not self.current_video_plan:
            print("❌ No video plan loaded. Create one first.")
            return
        
        summary = self.director.get_checkpoint_summary(self.current_video_plan)
        print("\n" + "="*60)
        print(summary)
        print("="*60)
    
    def select_checkpoint(self, checkpoint_id: int):
        """Select and export a specific checkpoint for FIBO generation."""
        if not self.current_video_plan:
            print("❌ No video plan loaded.")
            return None
        
        try:
            checkpoint_data = self.director.export_checkpoint_fibo_prompts(
                self.current_video_plan, checkpoint_id
            )
            
            if "error" in checkpoint_data:
                print(f"❌ {checkpoint_data['error']}")
                return None
            
            print(f"\n🎯 CHECKPOINT {checkpoint_id} SELECTED")
            print("="*50)
            print(f"Scene: {checkpoint_data['scene_description']}")
            print(f"Duration: {checkpoint_data['duration_sec']} seconds")
            print(f"Visual Style: {checkpoint_data['visual_style'].get('artistic_direction', 'Standard')}")
            
            # Save checkpoint data
            filename = f"checkpoint_{checkpoint_id}_fibo_prompts.json"
            with open(filename, "w") as f:
                json.dump(checkpoint_data, f, indent=2)
            
            print(f"💾 FIBO prompts saved to: {filename}")
            
            return checkpoint_data
            
        except Exception as e:
            print(f"❌ Error selecting checkpoint: {e}")
            return None
    
    def preview_fibo_prompts(self, checkpoint_data: dict):
        """Preview the FIBO structured prompts for a checkpoint."""
        if not checkpoint_data:
            return
        
        print(f"\n📋 FIBO STRUCTURED PROMPTS PREVIEW")
        print("="*50)
        
        # Start frame preview
        start_frame = checkpoint_data["fibo_start_frame"]
        print(f"🎬 START FRAME:")
        print(f"  Description: {start_frame['short_description']}")
        print(f"  Objects: {len(start_frame.get('objects', []))} objects defined")
        print(f"  Lighting: {start_frame.get('lighting', 'Standard')}")
        print(f"  Style: {start_frame.get('style_medium', 'Photorealistic')}")
        
        # End frame preview
        end_frame = checkpoint_data["fibo_end_frame"]
        print(f"\n🎬 END FRAME:")
        print(f"  Description: {end_frame['short_description']}")
        print(f"  Objects: {len(end_frame.get('objects', []))} objects defined")
        print(f"  Lighting: {end_frame.get('lighting', 'Standard')}")
        print(f"  Style: {end_frame.get('style_medium', 'Photorealistic')}")
        
        print(f"\n🎥 Video Notes: {checkpoint_data.get('video_generation_notes', 'N/A')}")
    
    def run_interactive_session(self):
        """Run the interactive checkpoint management session."""
        print("🎬 FIBO Video Checkpoint Interface")
        print("="*60)
        print("Create video plans from scripts and manage FIBO generation checkpoints")
        
        samples = self.load_sample_scripts()
        
        while True:
            print("\n" + "="*60)
            print("📋 MAIN MENU:")
            print("1. Create video plan from sample script")
            print("2. Create video plan from custom script")
            print("3. Load video plan from file")
            print("4. Show checkpoint overview")
            print("5. Select checkpoint for FIBO generation")
            print("6. Save current video plan")
            print("7. Quit")
            
            choice = input("\nChoose option (1-7): ").strip()
            
            if choice == "7":
                print("👋 Goodbye!")
                break
            
            elif choice == "1":
                print("\nAvailable sample scripts:")
                for name in samples.keys():
                    print(f"  • {name}")
                
                sample_name = input("\nEnter sample name: ").strip()
                if sample_name in samples:
                    self.create_video_plan(samples[sample_name])
                else:
                    print("❌ Sample not found")
            
            elif choice == "2":
                print("\n📝 Enter your script (press Ctrl+Z then Enter when done):")
                lines = []
                try:
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    script_text = "\n".join(lines)
                    if script_text.strip():
                        self.create_video_plan(script_text)
                    else:
                        print("❌ No script provided")
            
            elif choice == "3":
                filename = input("Enter video plan filename: ").strip()
                try:
                    with open(filename, 'r') as f:
                        self.current_video_plan = json.load(f)
                    print(f"✅ Video plan loaded from {filename}")
                except FileNotFoundError:
                    print(f"❌ File {filename} not found")
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON in {filename}")
            
            elif choice == "4":
                self.show_checkpoint_overview()
            
            elif choice == "5":
                if not self.current_video_plan:
                    print("❌ No video plan loaded. Create one first.")
                    continue
                
                try:
                    checkpoint_id = int(input("Enter checkpoint ID: ").strip())
                    checkpoint_data = self.select_checkpoint(checkpoint_id)
                    
                    if checkpoint_data:
                        preview = input("Preview FIBO prompts? (y/n): ").strip().lower()
                        if preview == 'y':
                            self.preview_fibo_prompts(checkpoint_data)
                            
                except ValueError:
                    print("❌ Invalid checkpoint ID")
            
            elif choice == "6":
                if not self.current_video_plan:
                    print("❌ No video plan to save")
                    continue
                
                filename = input("Enter filename (default: fibo_video_plan.json): ").strip()
                if not filename:
                    filename = "fibo_video_plan.json"
                
                try:
                    with open(filename, 'w') as f:
                        json.dump(self.current_video_plan, f, indent=2)
                    print(f"✅ Video plan saved to {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")

def main():
    """Run the FIBO checkpoint interface."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Get your API key from: https://aistudio.google.com/apikey")
        print("Then set: set GOOGLE_API_KEY=your_key")
        return
    
    interface = FIBOCheckpointInterface(os.environ["GOOGLE_API_KEY"])
    interface.run_interactive_session()

if __name__ == "__main__":
    main()