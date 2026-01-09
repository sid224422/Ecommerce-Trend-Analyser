"""
Complete Flow Test

Tests the entire system with .env file: Data → Agents → LLM
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from agents.brand_agent import analyze_brands
from agents.pricing_agent import analyze_pricing
from agents.feature_agent import analyze_features
from agents.gap_agent import analyze_gaps
from llm.summarizer import summarize_agent_results


def main():
    """Run complete flow test."""
    print("="*60)
    print("  Complete System Flow Test")
    print("="*60)
    
    # Check API key first
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key or api_key == 'your_api_key_here':
        print("\n[WARNING] GEMINI_API_KEY not found in .env file")
        print("\nTo fix:")
        print("  1. Open .env file in your editor")
        print("  2. Add this line: GEMINI_API_KEY=your_actual_api_key")
        print("  3. Get API key from: https://ai.google.dev/gemini-api/docs/quickstart")
        print("\nTesting will continue with agents only (no LLM)...")
        use_llm = False
    else:
        print(f"\n[OK] API key found ({len(api_key)} characters)")
        use_llm = True
    
    # Step 1: Load data
    print("\n[STEP 1] Loading data...")
    try:
        df = read_csv_file("test_data.csv")
        print(f"  [OK] Loaded {len(df)} rows")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False
    
    # Step 2: Validate
    print("\n[STEP 2] Validating data...")
    try:
        cleaned_df = validate_and_clean(df, cleaning_strategy="drop_rows", remove_dupes=True)
        print(f"  [OK] Validated {len(cleaned_df)} rows")
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False
    
    # Step 3: Run agents
    print("\n[STEP 3] Running analytical agents...")
    agent_outputs = []
    
    try:
        brand_result = analyze_brands(cleaned_df, brand_column="brand", top_n=5)
        agent_outputs.append(brand_result)
        print(f"  [OK] Brand Agent: {len(brand_result['results']['top_brands'])} brands")
    except Exception as e:
        print(f"  [ERROR] Brand Agent: {e}")
    
    try:
        pricing_result = analyze_pricing(cleaned_df, price_column="price")
        agent_outputs.append(pricing_result)
        print(f"  [OK] Pricing Agent: ${pricing_result['results']['price_statistics']['min_price']:.2f} - ${pricing_result['results']['price_statistics']['max_price']:.2f}")
    except Exception as e:
        print(f"  [ERROR] Pricing Agent: {e}")
    
    try:
        feature_result = analyze_features(cleaned_df, feature_column="feature", top_n=10)
        agent_outputs.append(feature_result)
        print(f"  [OK] Feature Agent: {len(feature_result['results']['top_features'])} features")
    except Exception as e:
        print(f"  [ERROR] Feature Agent: {e}")
    
    try:
        gap_result = analyze_gaps(cleaned_df, brand_column="brand", feature_column="feature", top_n=5)
        agent_outputs.append(gap_result)
        print(f"  [OK] Gap Agent: {gap_result['results']['identified_gaps_count']} gaps")
    except Exception as e:
        print(f"  [ERROR] Gap Agent: {e}")
    
    print(f"\n  [SUMMARY] {len(agent_outputs)}/4 agents completed successfully")
    
    # Step 4: LLM Summarization
    if use_llm and len(agent_outputs) == 4:
        print("\n[STEP 4] LLM Summarization...")
        try:
            summary_result = summarize_agent_results(agent_outputs)
            
            if summary_result['status'] == 'success':
                print(f"  [SUCCESS] Summary generated!")
                print(f"  Model: {summary_result['model']}")
                print(f"  Temperature: {summary_result['temperature']}")
                print(f"\n  {'='*56}")
                print(f"  LLM SUMMARY:")
                print(f"  {'='*56}")
                print(f"  {summary_result['summary']}")
                print(f"  {'='*56}")
                return True
            else:
                print(f"  [ERROR] {summary_result.get('error', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        if not use_llm:
            print("\n[STEP 4] LLM Summarization...")
            print("  [SKIP] No API key configured")
        else:
            print("\n[STEP 4] LLM Summarization...")
            print("  [SKIP] Not all agents completed")
        
        print("\n[INFO] Agents completed successfully!")
        print("  Add GEMINI_API_KEY to .env to enable LLM summarization")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

