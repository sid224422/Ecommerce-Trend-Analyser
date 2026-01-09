"""
Full Pipeline Test

Tests the complete pipeline: Ingestion → Validation → Agents → LLM Summarization
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from agents.brand_agent import analyze_brands
from agents.pricing_agent import analyze_pricing
from agents.feature_agent import analyze_features
from agents.gap_agent import analyze_gaps
from llm.summarizer import summarize_agent_results


def run_full_analysis(csv_file: str, use_llm: bool = False):
    """
    Run the complete analysis pipeline.
    
    Args:
        csv_file: Path to CSV file
        use_llm: Whether to include LLM summarization (requires API key)
    """
    print("="*60)
    print("  Full Pipeline Analysis")
    print("="*60)
    
    # Step 1: Ingestion
    print("\n[STEP 1] Data Ingestion...")
    df = read_csv_file(csv_file)
    print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
    
    # Step 2: Validation
    print("\n[STEP 2] Data Validation & Cleaning...")
    cleaned_df = validate_and_clean(df, cleaning_strategy="drop_rows", remove_dupes=True)
    print(f"  Cleaned: {len(cleaned_df)} rows")
    
    # Step 3: Run all agents
    print("\n[STEP 3] Running Analytical Agents...")
    
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
        print(f"  [OK] Pricing Agent: Range ${pricing_result['results']['price_statistics']['min_price']:.2f} - ${pricing_result['results']['price_statistics']['max_price']:.2f}")
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
        print(f"  [OK] Gap Agent: {gap_result['results']['identified_gaps_count']} gaps identified")
    except Exception as e:
        print(f"  [ERROR] Gap Agent: {e}")
    
    print(f"\n  Total agents executed: {len(agent_outputs)}")
    
    # Step 4: LLM Summarization (optional)
    if use_llm:
        print("\n[STEP 4] LLM Summarization...")
        try:
            summary_result = summarize_agent_results(agent_outputs)
            
            if summary_result['status'] == 'success':
                print(f"  [OK] Summary generated ({len(summary_result['summary'])} chars)")
                print(f"\n  {'='*56}")
                print(f"  LLM SUMMARY:")
                print(f"  {'='*56}")
                print(f"  {summary_result['summary']}")
                print(f"  {'='*56}")
            else:
                print(f"  [ERROR] Summarization failed: {summary_result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"  [ERROR] Summarization error: {e}")
            print(f"  Note: Set GEMINI_API_KEY environment variable to enable LLM")
    else:
        print("\n[STEP 4] LLM Summarization...")
        print("  [SKIP] LLM summarization skipped (set use_llm=True to enable)")
    
    # Output results as JSON
    print("\n[OUTPUT] Saving results to reports/analysis_output.json...")
    output_data = {
        "agent_outputs": agent_outputs,
        "num_agents": len(agent_outputs)
    }
    
    if use_llm and 'summary_result' in locals() and summary_result.get('status') == 'success':
        output_data["llm_summary"] = summary_result
    
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / "analysis_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"  Results saved to: {output_file}")
    
    print("\n" + "="*60)
    print("  Pipeline Complete!")
    print("="*60)
    
    return agent_outputs


if __name__ == "__main__":
    import os
    
    # Check if API key is available
    has_api_key = os.getenv('GEMINI_API_KEY') is not None
    use_llm = has_api_key
    
    if not has_api_key:
        print("Note: GEMINI_API_KEY not set - LLM summarization will be skipped")
        print("      Set environment variable to enable full pipeline test\n")
    
    # Run full pipeline
    run_full_analysis("test_data.csv", use_llm=use_llm)

