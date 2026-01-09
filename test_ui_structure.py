"""
Test UI Structure and Components

Validates that the Streamlit UI is properly structured and all functions exist.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ui_imports():
    """Test that UI module imports without errors."""
    print("="*60)
    print("  Testing UI Structure")
    print("="*60)
    
    try:
        # Import the app module (this will trigger imports)
        from ui import app
        print("\n[PASS] UI module imported successfully")
        return True
    except Exception as e:
        print(f"\n[FAIL] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ui_functions():
    """Test that required functions exist in the app."""
    print("\n[TEST] Checking required functions...")
    
    from ui import app
    
    required_functions = [
        'load_environment',
        'display_header',
        'upload_data',
        'validate_data',
        'visualize_brand_analysis',
        'visualize_pricing_analysis',
        'visualize_feature_analysis',
        'visualize_gap_analysis',
        'display_llm_summary',
        'main'
    ]
    
    missing = []
    for func_name in required_functions:
        if not hasattr(app, func_name):
            missing.append(func_name)
        else:
            print(f"  [OK] {func_name}")
    
    if missing:
        print(f"\n[FAIL] Missing functions: {missing}")
        return False
    else:
        print(f"\n[PASS] All {len(required_functions)} required functions found")
        return True


def test_ui_dependencies():
    """Test that all UI dependencies are available."""
    print("\n[TEST] Checking dependencies...")
    
    dependencies = {
        'streamlit': 'st',
        'pandas': 'pd',
        'plotly.express': 'px',
        'plotly.graph_objects': 'go'
    }
    
    missing = []
    for dep_name, import_name in dependencies.items():
        try:
            __import__(dep_name)
            print(f"  [OK] {dep_name}")
        except ImportError:
            print(f"  [FAIL] {dep_name} not found")
            missing.append(dep_name)
    
    if missing:
        print(f"\n[FAIL] Missing dependencies: {missing}")
        return False
    else:
        print(f"\n[PASS] All dependencies available")
        return True


def test_integration_imports():
    """Test that app can import all project modules."""
    print("\n[TEST] Checking project module imports...")
    
    modules = [
        'core.ingestion',
        'core.validator',
        'agents.brand_agent',
        'agents.pricing_agent',
        'agents.feature_agent',
        'agents.gap_agent',
        'llm.summarizer'
    ]
    
    missing = []
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}")
        except ImportError as e:
            print(f"  [FAIL] {module_name}: {e}")
            missing.append(module_name)
    
    if missing:
        print(f"\n[FAIL] Missing modules: {missing}")
        return False
    else:
        print(f"\n[PASS] All project modules importable")
        return True


def test_file_structure():
    """Test that required files exist."""
    print("\n[TEST] Checking file structure...")
    
    required_files = [
        Path('ui/app.py'),
        Path('run_app.py'),
        Path('test_data.csv'),
        Path('!.env')
    ]
    
    missing = []
    for file_path in required_files:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  [OK] {file_path} ({size} bytes)")
        else:
            print(f"  [WARN] {file_path} not found")
            if file_path.name != '!.env':  # !.env is optional
                missing.append(file_path)
    
    if missing:
        print(f"\n[WARN] Some files missing: {missing}")
        return False
    else:
        print(f"\n[PASS] File structure OK")
        return True


def main():
    """Run all UI structure tests."""
    results = {
        'imports': test_ui_imports(),
        'functions': test_ui_functions(),
        'dependencies': test_ui_dependencies(),
        'integration': test_integration_imports(),
        'files': test_file_structure()
    }
    
    print("\n" + "="*60)
    print("  Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name.upper():20} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] UI structure is valid and ready to run!")
        print("\nTo start the app, run:")
        print("  python run_app.py")
        print("  or")
        print("  streamlit run ui/app.py")
    else:
        print("\n[WARNING] Some tests failed - check errors above")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

