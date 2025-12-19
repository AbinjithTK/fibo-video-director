#!/usr/bin/env python3
"""Test download functionality"""

import requests

def test_download():
    """Test downloading generated FIBO images."""
    
    # Test downloading the PNG file
    url = "http://localhost:8000/api/download/start_frame_4df63779-42b9-4944-85d5-28cb760d91aa_1.png"
    
    print(f"Testing download: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("✅ Download successful!")
            
            # Save to test file
            with open("test_download.png", "wb") as f:
                f.write(response.content)
            print("✅ File saved as test_download.png")
            
        else:
            print(f"❌ Download failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_download()