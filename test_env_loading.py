"""
Test Environment Loading

Verifies that environment variables load correctly from .env file.
"""

import os
from pathlib import Path


def test_env_loading():
    """Test if .env file loading works."""
    print("="*60)
    print("  Environment Loading Test")
    print("="*60)
    
    # Check if .env file exists
    env_file = Path(".env")
    print(f"\n[CHECK] .env file exists: {env_file.exists()}")
    
    if env_file.exists():
        print(f"  Location: {env_file.absolute()}")
    
    # Try loading with dotenv
    try:
        from dotenv import load_dotenv
        print("\n[CHECK] python-dotenv: Installed")
        
        # Load .env file
        load_dotenv()
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key:
            if api_key == 'your_api_key_here':
                print("\n[STATUS] API Key: Template value (needs configuration)")
                print("  Action: Edit .env file and replace with actual API key")
            else:
                print(f"\n[SUCCESS] API Key: Loaded ({len(api_key)} characters)")
                print(f"  Preview: {api_key[:8]}...")
        else:
            print("\n[STATUS] API Key: Not set in .env")
            print("  Action: Add GEMINI_API_KEY to .env file")
        
        return api_key and api_key != 'your_api_key_here'
        
    except ImportError:
        print("\n[ERROR] python-dotenv: Not installed")
        print("  Install with: pip install python-dotenv")
        return False


def test_summarizer_env_loading():
    """Test if summarizer can load from environment."""
    print("\n" + "="*60)
    print("  Summarizer Environment Test")
    print("="*60)
    
    try:
        # Import summarizer (this will trigger dotenv loading)
        from llm.summarizer import summarize_agent_results
        print("\n[PASS] Summarizer imports successfully")
        
        # Check if it can access environment
        import os
        api_key = os.getenv('GEMINI_API_KEY')
        
        if api_key and api_key != 'your_api_key_here':
            print(f"[PASS] Environment accessible: API key found")
            print("  Summarizer is ready to use!")
            return True
        else:
            print(f"[INFO] Environment accessible: API key needs configuration")
            print("  Set GEMINI_API_KEY in .env or system environment")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    env_ok = test_env_loading()
    summarizer_ok = test_summarizer_env_loading()
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    print(f"Environment Loading: {'[OK]' if env_ok else '[NEEDS CONFIG]'}")
    print(f"Summarizer Ready:    {'[OK]' if summarizer_ok else '[NEEDS CONFIG]'}")
    
    if not env_ok:
        print("\nNext steps:")
        print("  1. Edit .env file")
        print("  2. Set GEMINI_API_KEY=your_actual_key")
        print("  3. Get key from: https://ai.google.dev/gemini-api/docs/quickstart")
    
    print("="*60)

