#!/usr/bin/env python3
"""FAL.ai FIBO Integration for Frame Generation with S3 Caching"""

import os
import json
import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path

import fal_client

# Try to import S3 storage
try:
    from s3_storage import get_s3_storage
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    print("⚠️ S3 storage not available - using local storage only")


class FalFiboIntegration:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY not set")
        os.environ["FAL_KEY"] = self.api_key
        self.output_dir = Path("examples/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 storage if available
        self.s3_storage = get_s3_storage() if S3_AVAILABLE else None
        if self.s3_storage and self.s3_storage.s3_available:
            print("✅ S3 caching enabled for frame storage")
    
    def _build_prompt(self, fibo_prompt: Dict[str, Any]) -> str:
        """Build a comprehensive prompt from FIBO structured JSON."""
        parts = []
        
        # Main description
        short_desc = fibo_prompt.get("short_description", "")
        if short_desc:
            parts.append(short_desc)
        
        # Detailed description if available
        detailed = fibo_prompt.get("detailed_description", "")
        if detailed:
            parts.append(detailed)
        
        # Objects with their details
        objects = fibo_prompt.get("objects", [])
        for obj in objects[:5]:  # Up to 5 objects
            obj_parts = []
            if obj.get("name"):
                obj_parts.append(obj["name"])
            if obj.get("description"):
                obj_parts.append(obj["description"])
            if obj.get("position"):
                obj_parts.append(f"positioned {obj['position']}")
            if obj.get("color"):
                obj_parts.append(f"in {obj['color']} color")
            if obj_parts:
                parts.append(", ".join(obj_parts))
        
        # Background and environment
        background = fibo_prompt.get("background_setting", "") or fibo_prompt.get("background", "")
        if background:
            parts.append(f"Background: {background}")
        
        # Lighting
        lighting = fibo_prompt.get("lighting", "") or fibo_prompt.get("lighting_style", "")
        if lighting:
            parts.append(f"Lighting: {lighting}")
        
        # Color palette
        colors = fibo_prompt.get("color_palette", "") or fibo_prompt.get("colors", "")
        if colors:
            parts.append(f"Color palette: {colors}")
        
        # Camera/composition
        camera = fibo_prompt.get("camera_angle", "") or fibo_prompt.get("camera_style", "")
        if camera:
            parts.append(f"Camera: {camera}")
        
        # Style/medium
        style = fibo_prompt.get("style_medium", "") or fibo_prompt.get("artistic_style", "")
        if style:
            parts.append(f"Style: {style}")
        
        # Mood/atmosphere
        mood = fibo_prompt.get("mood", "") or fibo_prompt.get("atmosphere", "")
        if mood:
            parts.append(f"Mood: {mood}")
        
        prompt = ". ".join(filter(None, parts))
        print(f"   Built prompt ({len(prompt)} chars): {prompt[:200]}...")
        return prompt[:2000]  # FAL allows longer prompts
    
    def _on_queue_update(self, update):
        if isinstance(update, fal_client.InProgress):
            for log in update.logs:
                msg = log.get("message", str(log)) if isinstance(log, dict) else str(log)
                print(f"   FAL: {msg}")
    
    def generate_image_sync(self, fibo_prompt: Dict[str, Any], seed: int = 5555,
                           steps: int = 50, aspect_ratio: str = "16:9",
                           guidance_scale: int = 5) -> Dict[str, Any]:
        prompt = self._build_prompt(fibo_prompt)
        print(f"   Calling FAL FIBO API with seed={seed}, steps={steps}...")
        print(f"   Prompt: {prompt[:300]}...")
        
        try:
            result = fal_client.subscribe(
                "bria/fibo/generate",
                arguments={
                    "prompt": prompt, 
                    "seed": seed, 
                    "steps_num": steps,
                    "aspect_ratio": aspect_ratio, 
                    "guidance_scale": guidance_scale
                },
                with_logs=True, 
                on_queue_update=self._on_queue_update
            )
            print(f"   FAL response received: {type(result)}")
            
            if isinstance(result, dict):
                if result.get("image"):
                    print(f"   ✅ Image URL: {result['image'].get('url', 'N/A')[:100]}...")
                else:
                    print(f"   ⚠️ No image in result: {list(result.keys())}")
                return result
            else:
                print(f"   ⚠️ Unexpected result type: {type(result)}")
                return {"raw": str(result)}
                
        except Exception as e:
            print(f"   ❌ FAL API error: {e}")
            raise
    
    async def generate_image(self, fibo_prompt: Dict[str, Any], seed: int = 5555,
                            steps: int = 50, aspect_ratio: str = "16:9",
                            guidance_scale: int = 5) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None,
            lambda: self.generate_image_sync(fibo_prompt, seed, steps, aspect_ratio, guidance_scale))
    
    def download_image_sync(self, image_url: str, output_path: Path) -> Path:
        import httpx
        print(f"   Downloading image...")
        with httpx.Client(timeout=60.0) as client:
            response = client.get(image_url)
            response.raise_for_status()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.content)
        print(f"   Saved: {output_path}")
        return output_path
    
    async def download_image(self, image_url: str, output_path: Path) -> Path:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: self.download_image_sync(image_url, output_path))

    
    async def generate_checkpoint_frames(self, start_prompt: Dict[str, Any],
                                         end_prompt: Dict[str, Any],
                                         checkpoint_id: int, project_id: str,
                                         seed: int = 5555) -> Dict[str, Any]:
        results = {}
        errors = []
        generation_times = {}
        
        # Check S3 cache for start frame
        print(f"\n{'='*50}")
        print(f"Generating START frame for checkpoint {checkpoint_id}...")
        print(f"{'='*50}")
        
        start_time = time.time()
        cached_start = None
        if self.s3_storage:
            cached_start = self.s3_storage.check_cache(start_prompt, seed, "start")
        
        if cached_start:
            print(f"   🚀 Cache HIT! Using cached start frame")
            results["start_frame_url"] = cached_start
            results["start_frame_cached"] = True
            generation_times["start_frame"] = round(time.time() - start_time, 3)
        else:
            try:
                start_result = await self.generate_image(start_prompt, seed=seed, aspect_ratio="16:9")
                if isinstance(start_result, dict) and start_result.get("image"):
                    url = start_result["image"].get("url")
                    if url:
                        print(f"   ✅ Start frame generated, processing...")
                        
                        # Try to upload to S3 if available, but keep original URL as fallback
                        if self.s3_storage:
                            try:
                                cached_url = await self.s3_storage.upload_from_url(
                                    url, start_prompt, seed, "start"
                                )
                                # If S3 upload returns a local URL (fallback), use original FAL URL instead
                                if cached_url.startswith('/api/download/'):
                                    print(f"   ⚠️ S3 upload failed, using original FAL URL")
                                    results["start_frame_url"] = url
                                else:
                                    results["start_frame_url"] = cached_url
                            except Exception as s3_error:
                                print(f"   ⚠️ S3 upload error: {s3_error}, using original FAL URL")
                                results["start_frame_url"] = url
                        else:
                            # No S3 available, use original FAL URL directly
                            results["start_frame_url"] = url
                        
                        results["start_frame_cached"] = False
                        generation_times["start_frame"] = round(time.time() - start_time, 3)
                        print(f"   ✅ Start frame ready ({generation_times['start_frame']}s)")
                    else:
                        errors.append("Start frame: No URL in response")
                else:
                    errors.append(f"Start frame: Invalid response - {start_result}")
            except Exception as e:
                errors.append(f"Start frame error: {str(e)}")
                print(f"   ❌ Start frame failed: {e}")
        
        # Always save JSON prompt
        start_json = self.output_dir / f"start_frame_{project_id}_{checkpoint_id}.json"
        with open(start_json, "w") as f:
            json.dump(start_prompt, f, indent=2)
        results["start_frame_json"] = str(start_json)
        
        # Check S3 cache for end frame
        print(f"\n{'='*50}")
        print(f"Generating END frame for checkpoint {checkpoint_id}...")
        print(f"{'='*50}")
        
        end_start_time = time.time()
        cached_end = None
        if self.s3_storage:
            cached_end = self.s3_storage.check_cache(end_prompt, seed + 1, "end")
        
        if cached_end:
            print(f"   🚀 Cache HIT! Using cached end frame")
            results["end_frame_url"] = cached_end
            results["end_frame_cached"] = True
            generation_times["end_frame"] = round(time.time() - end_start_time, 3)
        else:
            try:
                end_result = await self.generate_image(end_prompt, seed=seed+1, aspect_ratio="16:9")
                if isinstance(end_result, dict) and end_result.get("image"):
                    url = end_result["image"].get("url")
                    if url:
                        print(f"   ✅ End frame generated, processing...")
                        
                        # Try to upload to S3 if available, but keep original URL as fallback
                        if self.s3_storage:
                            try:
                                cached_url = await self.s3_storage.upload_from_url(
                                    url, end_prompt, seed + 1, "end"
                                )
                                # If S3 upload returns a local URL (fallback), use original FAL URL instead
                                if cached_url.startswith('/api/download/'):
                                    print(f"   ⚠️ S3 upload failed, using original FAL URL")
                                    results["end_frame_url"] = url
                                else:
                                    results["end_frame_url"] = cached_url
                            except Exception as s3_error:
                                print(f"   ⚠️ S3 upload error: {s3_error}, using original FAL URL")
                                results["end_frame_url"] = url
                        else:
                            # No S3 available, use original FAL URL directly
                            results["end_frame_url"] = url
                        
                        results["end_frame_cached"] = False
                        generation_times["end_frame"] = round(time.time() - end_start_time, 3)
                        print(f"   ✅ End frame ready ({generation_times['end_frame']}s)")
                    else:
                        errors.append("End frame: No URL in response")
                else:
                    errors.append(f"End frame: Invalid response - {end_result}")
            except Exception as e:
                errors.append(f"End frame error: {str(e)}")
                print(f"   ❌ End frame failed: {e}")
        
        # Always save JSON prompt
        end_json = self.output_dir / f"end_frame_{project_id}_{checkpoint_id}.json"
        with open(end_json, "w") as f:
            json.dump(end_prompt, f, indent=2)
        results["end_frame_json"] = str(end_json)
        
        # Add timing info
        results["generation_times"] = generation_times
        total_time = sum(generation_times.values())
        
        # Summary
        print("\n" + "=" * 50)
        print(f"Generation Summary for Checkpoint {checkpoint_id}:")
        
        # Start frame status
        if results.get("start_frame_url"):
            if results.get("start_frame_cached"):
                print("  Start frame: ✅ CACHED")
            else:
                start_time = generation_times.get("start_frame", 0)
                print(f"  Start frame: ✅ {start_time}s")
        else:
            print("  Start frame: ❌ Failed")
        
        # End frame status
        if results.get("end_frame_url"):
            if results.get("end_frame_cached"):
                print("  End frame: ✅ CACHED")
            else:
                end_time = generation_times.get("end_frame", 0)
                print(f"  End frame: ✅ {end_time}s")
        else:
            print("  End frame: ❌ Failed")
        
        print(f"  Total time: {total_time:.2f}s")
        if errors:
            print(f"  Errors: {errors}")
            results["errors"] = errors
        print("=" * 50 + "\n")
        
        return results


_fal_integration = None

def get_fal_integration() -> FalFiboIntegration:
    global _fal_integration
    if _fal_integration is None:
        _fal_integration = FalFiboIntegration()
    return _fal_integration


if __name__ == "__main__":
    test_prompt = {"short_description": "A majestic elephant in African savanna at sunset"}
    try:
        fal = get_fal_integration()
        print("Testing FAL FIBO...")
        result = fal.generate_image_sync(test_prompt, seed=42)
        if result.get("image"):
            print(f"Success! URL: {result['image']['url']}")
        else:
            print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
