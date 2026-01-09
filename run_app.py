"""
Quick launcher for Streamlit app
"""
import subprocess
import sys
from pathlib import Path

def main():
    """Launch Streamlit app."""
    app_path = Path(__file__).parent / "ui" / "app.py"
    
    if not app_path.exists():
        print(f"Error: {app_path} not found")
        return 1
    
    print("="*60)
    print("  Starting Streamlit App")
    print("="*60)
    print(f"App path: {app_path}")
    print("\nThe app will open in your default web browser.")
    print("Press Ctrl+C to stop the server.\n")
    print("="*60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n\nApp stopped by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

