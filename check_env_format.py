"""
Check .env File Format

Helps verify .env file format is correct.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values


def check_env_format():
    """Check if .env file format is correct."""
    print("="*60)
    print("  .env File Format Check")
    print("="*60)
    
    env_file = Path(".env")
    
    if not env_file.exists():
        print("\n[ERROR] .env file does not exist")
        print("  Run: python setup_env.py create")
        return False
    
    # Try to read raw content (for debugging format issues)
    print(f"\n[1] Reading .env file...")
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')
            
        print(f"    File size: {len(content)} characters")
        print(f"    Number of lines: {len(lines)}")
        
        if len(content) == 0:
            print(f"    [ERROR] File is completely empty!")
            print(f"\n    Solution:")
            print(f"    1. Open .env file")
            print(f"    2. Add exactly this line (no spaces around =):")
            print(f"       GEMINI_API_KEY=your_actual_key_here")
            print(f"    3. Save the file")
            return False
        
        # Show non-empty lines (safely, without exposing full key)
        print(f"\n    Non-empty lines found:")
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value_preview = value[:10] + "..." if len(value) > 10 else value
                    print(f"      Line {i}: {key}={value_preview}")
                else:
                    print(f"      Line {i}: {line} (no = sign found)")
        
    except Exception as e:
        print(f"    [ERROR] Could not read file: {e}")
        return False
    
    # Try loading with dotenv_values (shows what dotenv sees)
    print(f"\n[2] Testing dotenv loading...")
    try:
        values = dotenv_values(env_file)
        print(f"    Keys found: {list(values.keys())}")
        
        if 'GEMINI_API_KEY' in values:
            key_value = values['GEMINI_API_KEY']
            if key_value:
                print(f"    [OK] GEMINI_API_KEY found!")
                print(f"    Value length: {len(key_value)} characters")
                if key_value == 'your_api_key_here' or key_value == 'your_actual_api_key_here':
                    print(f"    [WARNING] Template value - replace with real key")
                    return False
                return True
            else:
                print(f"    [WARNING] GEMINI_API_KEY exists but is empty")
                print(f"    Format should be: GEMINI_API_KEY=value")
                return False
        else:
            print(f"    [ERROR] GEMINI_API_KEY not found in file")
            print(f"\n    Make sure your .env file has exactly this format:")
            print(f"    GEMINI_API_KEY=your_actual_key_here")
            print(f"\n    Common mistakes:")
            print(f"    - Spaces around = sign (WRONG: GEMINI_API_KEY = value)")
            print(f"    - Quotes around value (usually OK, but not required)")
            print(f"    - Missing GEMINI_API_KEY name")
            return False
            
    except Exception as e:
        print(f"    [ERROR] dotenv_values failed: {e}")
        return False
    
    # Final test: Try loading into environment
    print(f"\n[3] Testing environment variable loading...")
    load_dotenv(env_file, override=True)
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        print(f"    [SUCCESS] API key loaded into environment!")
        print(f"    Length: {len(api_key)} characters")
        return True
    else:
        print(f"    [ERROR] API key not in environment after loading")
        return False


if __name__ == "__main__":
    success = check_env_format()
    
    if success:
        print("\n" + "="*60)
        print("  [SUCCESS] .env file format is correct!")
        print("  You can now test the API connection:")
        print("  python test_env_direct.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("  [ACTION REQUIRED] Fix .env file format")
        print("="*60)

