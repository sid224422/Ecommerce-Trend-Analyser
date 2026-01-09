"""
Environment Setup Helper

Helps create .env file from template for API key configuration.
"""

from pathlib import Path


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if env_file.exists():
        print("[INFO] .env file already exists")
        print(f"  Location: {env_file.absolute()}")
        return False
    
    if not template_file.exists():
        print("[ERROR] env_template.txt not found")
        return False
    
    # Read template
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Create .env file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print("[SUCCESS] .env file created!")
    print(f"  Location: {env_file.absolute()}")
    print("\n  Next steps:")
    print("  1. Open .env file")
    print("  2. Replace 'your_api_key_here' with your actual Gemini API key")
    print("  3. Get API key from: https://ai.google.dev/gemini-api/docs/quickstart")
    print("\n  Note: .env file is in .gitignore and won't be committed to git")
    
    return True


def check_env_setup():
    """Check if environment is properly set up."""
    print("="*60)
    print("  Environment Setup Check")
    print("="*60)
    
    env_file = Path(".env")
    has_env_file = env_file.exists()
    
    # Try to load environment
    try:
        from dotenv import load_dotenv
        import os
        
        if has_env_file:
            load_dotenv()
            api_key = os.getenv('GEMINI_API_KEY')
            
            if api_key and api_key != 'your_api_key_here':
                print("\n[SUCCESS] Environment configured!")
                print(f"  .env file: Found")
                print(f"  GEMINI_API_KEY: Set ({'*' * min(len(api_key), 8)}...)")
                return True
            else:
                print("\n[WARNING] .env file exists but API key not configured")
                print("  Please edit .env and set your GEMINI_API_KEY")
                return False
        else:
            # Check system environment variable
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                print("\n[INFO] Using system environment variable")
                print(f"  GEMINI_API_KEY: Set (from system)")
                return True
            else:
                print("\n[INFO] No .env file and no system environment variable")
                print("  Run: python setup_env.py")
                return False
                
    except ImportError:
        print("\n[ERROR] python-dotenv not installed")
        print("  Install with: pip install python-dotenv")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        create_env_file()
    else:
        if not Path(".env").exists():
            print("Creating .env file from template...\n")
            create_env_file()
        check_env_setup()

