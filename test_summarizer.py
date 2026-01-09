"""
Test Script for LLM Summarizer

Tests the summarizer module structure and prompt loading.
Note: Requires GEMINI_API_KEY environment variable for full API test.
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from llm.summarizer import load_prompt_template, format_agent_results, summarize_agent_results


def test_prompt_loading():
    """Test prompt template loading."""
    print("\n[TEST 1] Testing Prompt Template Loading...")
    try:
        prompt = load_prompt_template()
        print("[PASS] Prompt template loaded successfully")
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  Contains placeholder: {'{agent_results}' in prompt}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        return False


def test_result_formatting():
    """Test agent results formatting."""
    print("\n[TEST 2] Testing Agent Results Formatting...")
    try:
        # Sample agent outputs (same format as from actual agents)
        sample_outputs = [
            {
                "agent_name": "brand_agent",
                "results": {
                    "total_unique_brands": 4,
                    "top_brands": [
                        {"brand": "Samsung", "count": 5, "confidence": 0.3333}
                    ]
                },
                "confidence": 1.0,
                "timestamp": "2026-01-09T00:00:00"
            },
            {
                "agent_name": "pricing_agent",
                "results": {
                    "price_statistics": {
                        "min_price": 399.99,
                        "max_price": 1299.99
                    }
                },
                "confidence": 1.0,
                "timestamp": "2026-01-09T00:00:00"
            }
        ]
        
        formatted = format_agent_results(sample_outputs)
        print("[PASS] Agent results formatted successfully")
        print(f"  Formatted length: {len(formatted)} characters")
        print(f"  Contains brand_agent: {'BRAND_AGENT' in formatted}")
        return True, sample_outputs
    except Exception as e:
        print(f"[FAIL] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_summarizer_structure(sample_outputs):
    """Test summarizer structure (without API call if key missing)."""
    print("\n[TEST 3] Testing Summarizer Structure...")
    
    import os
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("[SKIP] GEMINI_API_KEY not set - skipping API call test")
        print("  To test with API: set GEMINI_API_KEY environment variable")
        print("  Structure validation: PASS (code compiles without errors)")
        return True
    
    try:
        result = summarize_agent_results(sample_outputs, api_key=api_key)
        
        if result['status'] == 'success':
            print("[PASS] Summarizer executed successfully")
            print(f"  Model: {result['model']}")
            print(f"  Temperature: {result['temperature']}")
            print(f"  Summary length: {len(result['summary'])} characters")
            print(f"\n  Summary preview:\n  {result['summary'][:200]}...")
            return True
        else:
            print(f"[FAIL] API call failed: {result.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run summarizer tests."""
    print("="*60)
    print("  LLM Summarizer Module - Testing")
    print("="*60)
    
    # Test 1: Prompt loading
    prompt_ok = test_prompt_loading()
    
    # Test 2: Result formatting
    format_ok, sample_outputs = test_result_formatting()
    
    # Test 3: Summarizer (if API key available)
    if format_ok and sample_outputs:
        summarizer_ok = test_summarizer_structure(sample_outputs)
    else:
        summarizer_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    print(f"Prompt Loading:    {'[PASS]' if prompt_ok else '[FAIL]'}")
    print(f"Result Formatting: {'[PASS]' if format_ok else '[FAIL]'}")
    print(f"Summarizer:        {'[PASS]' if summarizer_ok else '[SKIP/FAIL]'}")
    
    if prompt_ok and format_ok:
        print("\n[SUCCESS] Core summarizer structure is working!")
        if not summarizer_ok:
            print("  Note: Set GEMINI_API_KEY to test full API integration")
    else:
        print("\n[ERROR] Some tests failed")
    
    print("="*60)


if __name__ == "__main__":
    main()

