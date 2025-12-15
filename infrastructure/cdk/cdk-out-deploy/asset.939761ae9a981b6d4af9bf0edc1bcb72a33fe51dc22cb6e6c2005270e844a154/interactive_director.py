#!/usr/bin/env python3
"""
Interactive AI Director

Chat interface for the AI Director & Cinematography Orchestrator.
Input movie scripts and get production-ready JSON for FIBO video pipelines.
"""

import os
import json
from pathlib import Path
from advanced_director_agent import AdvancedDirectorAgent

def load_sample_scripts():
    """Load sample scripts for testing."""
    return {
        "cyberpunk": """
FADE IN:

EXT. RAIN-SOAKED ALLEY - NIGHT

Neon signs cast colored reflections on wet concrete. Steam rises from manholes.

JACK (30s, cybernetic arm, leather jacket) walks cautiously through the alley, scanning for threats. His augmented eye glows blue in the darkness.

JACK
(whispering to comm)
Approaching the drop point now.

A FIGURE emerges from the shadows - ZARA (20s, punk aesthetic, glowing tattoos).

ZARA
You're late, Jack.

JACK
Traffic was murder. You got the data?

Zara holds up a glowing data chip. Jack reaches for it, but she pulls back.

ZARA
Payment first.

Jack transfers credits via his wrist display. The transaction completes with a soft chime.

FADE OUT.
        """,
        
        "space_thriller": """
FADE IN:

INT. SPACESHIP BRIDGE - DAY

Warning lights flash red. Alarms blare. The ship shudders violently.

CAPTAIN SARAH (40s, uniform torn, blood on forehead) grips her command chair as the ship rocks.

SARAH
(shouting over alarms)
Damage report!

ENGINEER TORRES (30s, panicked) frantically works at his console.

TORRES
Hull breach on deck seven! We're losing atmosphere fast!

Sarah's eyes widen as she sees something on the main viewscreen - a massive alien vessel approaching.

SARAH
(whispered)
My God... what is that thing?

The alien ship fires. A brilliant beam of energy streaks toward them.

SARAH
(screaming)
Brace for impact!

FADE OUT.
        """,
        
        "mystery": """
FADE IN:

INT. VICTORIAN MANSION - LIBRARY - NIGHT

Rain patters against tall windows. A fire crackles in the ornate fireplace.

DETECTIVE HOLMES (50s, sharp suit, pipe) examines a bloodstain on the Persian rug with a magnifying glass.

HOLMES
Fascinating. The blood spatter suggests the victim was struck from behind.

DR. WATSON (45, medical bag, concerned expression) enters carrying his black bag.

WATSON
The servants are all accounted for, Holmes. But there's something odd...

HOLMES
(looking up)
Oh?

WATSON
The victim's study was locked from the inside. No other way out except the window... which is three stories up.

Holmes sets down his magnifying glass and walks to the window, deep in thought.

HOLMES
(smiling slightly)
Ah, Watson. The game is afoot.

FADE OUT.
        """
    }

def main():
    """Interactive director interface."""
    
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set!")
        print("Get your API key from: https://aistudio.google.com/apikey")
        print("Then set: set GOOGLE_API_KEY=your_key")
        return
    
    print("🎬 Interactive AI Director & Cinematography Orchestrator")
    print("="*60)
    print("Transform movie scripts into FIBO production plans!")
    
    # Initialize director
    director = AdvancedDirectorAgent(os.environ["GOOGLE_API_KEY"])
    samples = load_sample_scripts()
    
    while True:
        print("\n" + "="*60)
        print("📝 SCRIPT INPUT OPTIONS:")
        print("1. Use sample script (cyberpunk/space_thriller/mystery)")
        print("2. Enter your own script")
        print("3. Load script from file")
        print("4. Quit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == "4":
            print("👋 Goodbye!")
            break
        
        script_text = ""
        
        if choice == "1":
            print("\nAvailable samples:")
            for name in samples.keys():
                print(f"  • {name}")
            
            sample_name = input("\nEnter sample name: ").strip().lower()
            if sample_name in samples:
                script_text = samples[sample_name]
                print(f"✅ Loaded {sample_name} sample script")
            else:
                print("❌ Sample not found")
                continue
                
        elif choice == "2":
            print("\n📝 Enter your script (press Ctrl+Z then Enter on Windows, or Ctrl+D on Mac/Linux when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                script_text = "\n".join(lines)
                
        elif choice == "3":
            filename = input("Enter script filename: ").strip()
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    script_text = f.read()
                print(f"✅ Loaded script from {filename}")
            except FileNotFoundError:
                print(f"❌ File {filename} not found")
                continue
        
        if not script_text.strip():
            print("❌ No script provided")
            continue
        
        try:
            print("\n🎬 Processing script with AI Director...")
            print("⏳ This may take a moment...")
            
            # Generate production plan
            production_plan = director.generate_production_plan(script_text)
            
            print("\n📋 PRODUCTION PLAN GENERATED:")
            print("="*60)
            print(json.dumps(production_plan, indent=2))
            
            # Save option
            save = input("\n💾 Save to file? (y/n): ").strip().lower()
            if save == 'y':
                filename = input("Enter filename (default: production_plan.json): ").strip()
                if not filename:
                    filename = "production_plan.json"
                
                with open(filename, 'w') as f:
                    json.dump(production_plan, f, indent=2)
                
                print(f"✅ Saved to {filename}")
            
            print("\n🎥 Production plan ready for FIBO + Veo pipeline!")
            
        except Exception as e:
            print(f"❌ Error processing script: {e}")

if __name__ == "__main__":
    main()