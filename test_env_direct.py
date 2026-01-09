"""
Direct Environment Test

Tests .env file loading and API connectivity directly.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def test_env_direct():
    """Direct test of environment loading."""
    print("="*60)
    print("  Direct Environment Test")
    print("="*60)
    
    # Check .env file
    env_file = Path(".env")
    print(f"\n[1] Checking .env file...")
    print(f"    Exists: {env_file.exists()}")
    
    if env_file.exists():
        # Check file size (to see if it has content)
        size = env_file.stat().st_size
        print(f"    Size: {size} bytes")
        
        # Read first few lines (safely, to check format)
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                print(f"    First line preview: {first_line[:50]}...")
        except Exception as e:
            print(f"    Error reading file: {e}")
    
    # Load environment
    print(f"\n[2] Loading environment variables...")
    load_dotenv(override=True)  # Force reload
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"    GEMINI_API_KEY found: {'Yes' if api_key else 'No'}")
    
    if api_key:
        key_len = len(api_key)
        print(f"    Key length: {key_len} characters")
        
        # Check if it's the template value
        if api_key == 'your_api_key_here':
            print(f"    [WARNING] Template value detected - needs real API key")
            return False
        elif key_len < 20:
            print(f"    [WARNING] Key seems too short (should be ~40+ chars)")
            return False
        else:
            print(f"    [OK] Key format looks valid")
            print(f"    Preview: {api_key[:8]}...{api_key[-4:]}")
            return True
    else:
        print(f"    [ERROR] No API key found")
        print(f"    Make sure .env file contains: GEMINI_API_KEY=your_key")
        return False


def test_api_connection():
    """Test actual API connection if key is available."""
    print(f"\n[3] Testing API connection...")
    
    load_dotenv(override=True)
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("    [SKIP] No valid API key - cannot test connection")
        return False
    
    try:
        import google.generativeai as genai
        
        # Configure
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Make a simple test call
        print("    Attempting connection...")
        response = model.generate_content("Say 'API connection successful' in one sentence.")
        
        if response and response.text:
            print(f"    [SUCCESS] API connection working!")
            print(f"    Response: {response.text.strip()}")
            return True
        else:
            print(f"    [ERROR] No response from API")
            return False
            
    except ImportError:
        print("    [ERROR] google-generativeai not installed")
        print("    Install with: pip install google-generativeai")
        return False
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            print(f"    [ERROR] Invalid API key")
            print(f"    Check your API key in .env file")
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            print(f"    [ERROR] API quota/rate limit exceeded")
        else:
            print(f"    [ERROR] Connection failed: {error_msg}")
        return False


if __name__ == "__main__":
    print("\n")
    
    # Test 1: Environment loading
    env_ok = test_env_direct()
    
    # Test 2: API connection (only if key is valid)
    api_ok = False
    if env_ok:
        api_ok = test_api_connection()
    
    # Summary
    print("\n" + "="*60)
    print("  Test Results")
    print("="*60)
    print(f"Environment Loading: {'[PASS]' if env_ok else '[FAIL]'}")
    print(f"API Connection:      {'[PASS]' if api_ok else '[SKIP/FAIL]'}")
    
    if env_ok and api_ok:
        print("\n[SUCCESS] Everything is working! Your .env setup is correct.")
    elif env_ok and not api_ok:
        print("\n[INFO] Environment loaded but API test failed")
        print("       Check API key validity or network connection")
    else:
        print("\n[ACTION REQUIRED] Fix .env file configuration")
        print("   1. Open .env file")
        print("   2. Add: GEMINI_API_KEY=your_actual_key")
        print("   3. Get key from: https://ai.google.dev/gemini-api/docs/quickstart")
    
    print("="*60)

