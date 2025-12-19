#!/usr/bin/env python3
"""
Quick test to verify the cleaned up application structure works
"""

import sys
from pathlib import Path

# Add core directory to path
sys.path.insert(0, str(Path(__file__).parent / "core"))

def test_imports():
    """Test that all core imports work."""
    print("🧪 Testing core imports...")
    
    try:
        from api_server import app
        print("   ✅ API server import successful")
    except ImportError as e:
        print(f"   ❌ API server import failed: {e}")
        return False
    
    try:
        from working_fibo_director import WorkingFIBODirector
        print("   ✅ Working FIBO Director import successful")
    except ImportError as e:
        print(f"   ❌ Working FIBO Director import failed: {e}")
        return False
    
    try:
        from fibo_video_director import FIBOVideoDirector
        print("   ✅ FIBO Video Director import successful")
    except ImportError as e:
        print(f"   ❌ FIBO Video Director import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment setup."""
    print("🔧 Testing environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("   ✅ .env file exists")
    else:
        print("   ⚠️  .env file not found")
    
    frontend_dir = Path("frontend")
    if frontend_dir.exists():
        print("   ✅ Frontend directory exists")
    else:
        print("   ❌ Frontend directory not found")
        return False
    
    return True

def main():
    """Main test function."""
    print("🎬 FIBO Video Director - Structure Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return False
    
    print()
    
    # Test environment
    if not test_environment():
        print("❌ Environment tests failed")
        return False
    
    print()
    print("✅ All tests passed! The cleaned structure is working.")
    print()
    print("🚀 To start the application:")
    print("   python scripts/start_fibo_app.py")
    print()
    print("🧪 To run integration tests:")
    print("   python tests/integration/test_local_workflow.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)