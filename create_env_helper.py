"""
Helper to create .env file with API key

This script helps you set up the .env file correctly.
"""

from pathlib import Path


def create_env_with_key():
    """Interactive helper to create .env file."""
    print("="*60)
    print("  .env File Setup Helper")
    print("="*60)
    
    env_file = Path(".env")
    
    # Check if file exists and has content
    if env_file.exists():
        size = env_file.stat().st_size
        if size > 0:
            print(f"\n[INFO] .env file exists and has content ({size} bytes)")
            print(f"  If you're having issues, the format should be:")
            print(f"  GEMINI_API_KEY=your_actual_key_here")
            print(f"\n  No spaces around the = sign!")
            return
    
    print(f"\n[INFO] Creating .env file...")
    print(f"\nPlease enter your Gemini API key:")
    print(f"(Get it from: https://ai.google.dev/gemini-api/docs/quickstart)")
    print(f"\nOr press Enter to create template file that you can edit manually.")
    
    api_key = input("\nAPI Key (or Enter for template): ").strip()
    
    if api_key:
        # Create file with actual key
        content = f"# Gemini API Key for LLM Summarization\nGEMINI_API_KEY={api_key}\n"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[SUCCESS] .env file created with your API key!")
        print(f"  File location: {env_file.absolute()}")
        print(f"  Key length: {len(api_key)} characters")
    else:
        # Create template file
        content = "# Gemini API Key for LLM Summarization\n# Get your API key from: https://ai.google.dev/gemini-api/docs/quickstart\nGEMINI_API_KEY=your_api_key_here\n"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n[INFO] Template .env file created")
        print(f"  Location: {env_file.absolute()}")
        print(f"  Please edit it and replace 'your_api_key_here' with your actual key")
    
    # Verify
    if env_file.exists():
        size = env_file.stat().st_size
        print(f"\n[VERIFY] File created: {size} bytes")
        
        if size > 0:
            print(f"\n[SUCCESS] Setup complete!")
            print(f"  Test it with: python verify_env.py")
        else:
            print(f"\n[WARNING] File appears empty - there may be a saving issue")


if __name__ == "__main__":
    try:
        create_env_with_key()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

