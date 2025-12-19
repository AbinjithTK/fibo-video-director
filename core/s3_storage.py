#!/usr/bin/env python3
"""AWS S3 Storage Integration for FIBO Frame Caching"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3FrameStorage:
    """S3-based storage for generated FIBO frames with caching."""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: str = "us-east-1",
        cache_ttl_days: int = 30
    ):
        self.bucket_name = bucket_name or os.environ.get("FIBO_S3_BUCKET", "fibo-frames-cache")
        self.region = region
        self.cache_ttl_days = cache_ttl_days
        self.prefix = "fibo-frames"
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client("s3", region_name=region)
            self.s3_available = True
            print(f"✅ S3 storage initialized: {self.bucket_name}")
        except NoCredentialsError:
            print("⚠️ AWS credentials not found - S3 storage disabled")
            self.s3_available = False
        except Exception as e:
            print(f"⚠️ S3 initialization failed: {e}")
            self.s3_available = False
        
        # Local cache directory as fallback
        self.local_cache = Path("cache/frames")
        self.local_cache.mkdir(parents=True, exist_ok=True)
    
    def _generate_cache_key(self, prompt: Dict[str, Any], seed: int) -> str:
        """Generate a unique cache key based on prompt content and seed."""
        # Create a hash of the prompt content
        prompt_str = json.dumps(prompt, sort_keys=True)
        prompt_hash = hashlib.sha256(prompt_str.encode()).hexdigest()[:16]
        return f"{prompt_hash}_{seed}"
    
    def _get_s3_key(self, cache_key: str, frame_type: str, extension: str = "png") -> str:
        """Generate S3 object key."""
        return f"{self.prefix}/{frame_type}/{cache_key}.{extension}"
    
    def check_cache(self, prompt: Dict[str, Any], seed: int, frame_type: str) -> Optional[str]:
        """Check if a frame is already cached and return its URL."""
        cache_key = self._generate_cache_key(prompt, seed)
        
        if self.s3_available:
            try:
                s3_key = self._get_s3_key(cache_key, frame_type)
                # Check if object exists
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                # Generate presigned URL for access
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": s3_key},
                    ExpiresIn=3600 * 24  # 24 hour URL
                )
                print(f"   ✅ Cache hit: {s3_key}")
                return url
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    print(f"   Cache miss: {cache_key}")
                    return None
                print(f"   S3 error: {e}")
                return None
        
        # Fallback to local cache
        local_path = self.local_cache / f"{frame_type}_{cache_key}.png"
        if local_path.exists():
            print(f"   ✅ Local cache hit: {local_path}")
            return f"/api/download/frames/{frame_type}_{cache_key}.png"
        
        return None

    async def upload_frame(
        self,
        image_data: bytes,
        prompt: Dict[str, Any],
        seed: int,
        frame_type: str,
        content_type: str = "image/png"
    ) -> str:
        """Upload a frame to S3 and return its URL."""
        cache_key = self._generate_cache_key(prompt, seed)
        
        if self.s3_available:
            try:
                s3_key = self._get_s3_key(cache_key, frame_type)
                
                # Upload to S3 with metadata
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=image_data,
                    ContentType=content_type,
                    Metadata={
                        "seed": str(seed),
                        "frame_type": frame_type,
                        "created_at": datetime.utcnow().isoformat(),
                        "prompt_hash": cache_key.split("_")[0]
                    }
                )
                
                # Generate presigned URL
                url = self.s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": s3_key},
                    ExpiresIn=3600 * 24 * 7  # 7 day URL
                )
                print(f"   ✅ Uploaded to S3: {s3_key}")
                return url
                
            except ClientError as e:
                print(f"   ❌ S3 upload failed: {e}")
                # Fall through to local storage
        
        # Fallback to local storage
        local_path = self.local_cache / f"{frame_type}_{cache_key}.png"
        local_path.write_bytes(image_data)
        print(f"   ✅ Saved locally: {local_path}")
        return f"/api/download/frames/{frame_type}_{cache_key}.png"
    
    async def upload_from_url(
        self,
        image_url: str,
        prompt: Dict[str, Any],
        seed: int,
        frame_type: str
    ) -> str:
        """Download image from URL and upload to S3."""
        import httpx
        
        # Check cache first
        cached_url = self.check_cache(prompt, seed, frame_type)
        if cached_url:
            return cached_url
        
        # Download image
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_data = response.content
                content_type = response.headers.get("content-type", "image/png")
        except Exception as e:
            print(f"   ❌ Failed to download image: {e}")
            return image_url  # Return original URL as fallback
        
        # Upload to S3
        return await self.upload_frame(image_data, prompt, seed, frame_type, content_type)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "s3_available": self.s3_available,
            "bucket": self.bucket_name,
            "local_cache_path": str(self.local_cache),
            "local_files": 0
        }
        
        # Count local files
        if self.local_cache.exists():
            stats["local_files"] = len(list(self.local_cache.glob("*.png")))
        
        # Get S3 stats if available
        if self.s3_available:
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=self.prefix,
                    MaxKeys=1000
                )
                stats["s3_objects"] = response.get("KeyCount", 0)
            except Exception as e:
                stats["s3_error"] = str(e)
        
        return stats
    
    def ensure_bucket_exists(self) -> bool:
        """Create the S3 bucket if it doesn't exist."""
        if not self.s3_available:
            return False
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"   ✅ Bucket exists: {self.bucket_name}")
            return True
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "404":
                # Bucket doesn't exist, create it
                try:
                    if self.region == "us-east-1":
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={"LocationConstraint": self.region}
                        )
                    
                    # Enable versioning for safety
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={"Status": "Enabled"}
                    )
                    
                    # Set lifecycle policy for cache expiration
                    self.s3_client.put_bucket_lifecycle_configuration(
                        Bucket=self.bucket_name,
                        LifecycleConfiguration={
                            "Rules": [{
                                "ID": "ExpireOldFrames",
                                "Status": "Enabled",
                                "Filter": {"Prefix": self.prefix},
                                "Expiration": {"Days": self.cache_ttl_days}
                            }]
                        }
                    )
                    
                    print(f"   ✅ Created bucket: {self.bucket_name}")
                    return True
                except Exception as create_error:
                    print(f"   ❌ Failed to create bucket: {create_error}")
                    return False
            else:
                print(f"   ❌ Bucket access error: {e}")
                return False


# Global instance
_s3_storage = None

def get_s3_storage() -> S3FrameStorage:
    """Get or create the S3 storage instance."""
    global _s3_storage
    if _s3_storage is None:
        _s3_storage = S3FrameStorage()
    return _s3_storage
