"""
Test UI Startup

Verifies that the Streamlit app can be loaded and validated by Streamlit.
"""

import subprocess
import sys
from pathlib import Path

def test_streamlit_validation():
    """Test that Streamlit can validate the app."""
    print("="*60)
    print("  Testing Streamlit App Validation")
    print("="*60)
    
    app_path = Path("ui/app.py")
    
    if not app_path.exists():
        print(f"\n[ERROR] App file not found: {app_path}")
        return False
    
    print(f"\n[INFO] Validating app: {app_path}")
    print("  This may take a few seconds...\n")
    
    try:
        # Use streamlit validate command if available, or try to compile
        # For now, we'll use Python's compile to check syntax
        with open(app_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        compile(code, str(app_path), 'exec')
        print("[PASS] App file syntax is valid")
        
        # Try to import and check main function exists
        sys.path.insert(0, str(Path.cwd()))
        from ui import app
        
        if hasattr(app, 'main') and callable(app.main):
            print("[PASS] main() function is callable")
        else:
            print("[FAIL] main() function not found or not callable")
            return False
        
        return True
        
    except SyntaxError as e:
        print(f"[FAIL] Syntax error: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streamlit_config():
    """Test Streamlit configuration."""
    print("\n[TEST] Checking Streamlit installation...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"  [OK] {version}")
            return True
        else:
            print(f"  [FAIL] Streamlit check failed")
            return False
            
    except FileNotFoundError:
        print("  [FAIL] Streamlit not found - install with: pip install streamlit")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def main():
    """Run startup tests."""
    syntax_ok = test_streamlit_validation()
    config_ok = test_streamlit_config()
    
    print("\n" + "="*60)
    print("  Startup Test Summary")
    print("="*60)
    print(f"Syntax Validation: {'[PASS]' if syntax_ok else '[FAIL]'}")
    print(f"Streamlit Config:   {'[PASS]' if config_ok else '[FAIL]'}")
    
    if syntax_ok and config_ok:
        print("\n[SUCCESS] App is ready to run!")
        print("\nStart the app with:")
        print("  python run_app.py")
        print("\nThe app will open in your browser at http://localhost:8501")
    else:
        print("\n[WARNING] Some checks failed - review errors above")
    
    print("="*60)
    
    return syntax_ok and config_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

