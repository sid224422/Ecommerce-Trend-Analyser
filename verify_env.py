"""
Quick Environment Verification

Checks if .env file is properly configured and tests API connectivity.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def main():
    print("\n" + "="*60)
    print("  Environment Verification")
    print("="*60)
    
    # Check !.env file first, then .env
    env_file = Path("!.env")
    if not env_file.exists():
        env_file = Path(".env")
    
    print(f"\n[1] Environment File Check:")
    print(f"    Location: {env_file.absolute()}")
    print(f"    Exists: {env_file.exists()}")
    print(f"    Filename: {env_file.name}")
    
    if env_file.exists():
        size = env_file.stat().st_size
        print(f"    Size: {size} bytes")
        
        if size == 0:
            print(f"    [WARNING] File is empty!")
            print(f"\n    To fix, add this line to .env file:")
            print(f"    GEMINI_API_KEY=your_actual_api_key_here")
            return
    
    # Load environment
    print(f"\n[2] Loading Environment Variables...")
    # Try !.env first, then .env
    if Path("!.env").exists():
        load_dotenv("!.env", override=True)
    else:
        load_dotenv(override=True)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print(f"    [ERROR] GEMINI_API_KEY not found")
        print(f"\n    Please add to .env file:")
        print(f"    GEMINI_API_KEY=your_actual_api_key_here")
        print(f"\n    Get API key from:")
        print(f"    https://ai.google.dev/gemini-api/docs/quickstart")
        return
    
    if api_key == 'your_api_key_here' or api_key == 'your_actual_api_key_here':
        print(f"    [WARNING] Template value detected")
        print(f"    Please replace with your actual API key")
        return
    
    print(f"    [OK] API Key found")
    print(f"    Length: {len(api_key)} characters")
    print(f"    Preview: {api_key[:8]}...{api_key[-4:]}")
    
    # Test API connection
    print(f"\n[3] Testing API Connection...")
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=api_key)
        
        # List available models first
        print(f"    Listing available models...")
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if not available:
            raise ValueError("No available Gemini models found")
        
        # Try to find a good model (prefer flash or pro)
        model_name = None
        for preferred in ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro']:
            for m in available:
                if preferred in m.lower():
                    model_name = m
                    break
            if model_name:
                break
        
        # Fallback to first available
        if not model_name:
            model_name = available[0]
        
        model_short = model_name.split('/')[-1]
        print(f"    Using model: {model_short}")
        
        model = genai.GenerativeModel(model_name)
        
        print(f"    Connecting...")
        response = model.generate_content("Say 'Hello' in one word.")
        
        if response and response.text:
            print(f"    [SUCCESS] API connection working!")
            print(f"    Response: {response.text.strip()}")
            print(f"\n" + "="*60)
            print(f"  [SUCCESS] Your .env setup is working correctly!")
            print(f"="*60)
            return True
        else:
            print(f"    [ERROR] No response from API")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            print(f"    [ERROR] Invalid API key")
            print(f"    Please check your API key in .env file")
        elif "403" in error_msg or "permission" in error_msg.lower():
            print(f"    [ERROR] API key permissions issue")
            print(f"    Check API key permissions in Google AI Studio")
        else:
            print(f"    [ERROR] {error_msg}")
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

