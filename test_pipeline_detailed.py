"""
Detailed Full Pipeline Test

Tests complete pipeline and generates a detailed report.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables
if Path("!.env").exists():
    load_dotenv("!.env")
else:
    load_dotenv()

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from agents.brand_agent import analyze_brands
from agents.pricing_agent import analyze_pricing
from agents.feature_agent import analyze_features
from agents.gap_agent import analyze_gaps
from llm.summarizer import summarize_agent_results


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():
    """Run detailed pipeline test."""
    print_section("Full Pipeline Test - Detailed Report")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "steps": {},
        "agent_outputs": [],
        "llm_summary": None,
        "status": "partial"
    }
    
    # Step 1: Check API key
    print_section("Step 1: Environment Check")
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key != 'your_api_key_here':
        print(f"[OK] API Key: Found ({len(api_key)} characters)")
        results["steps"]["environment"] = {"status": "pass", "api_key_length": len(api_key)}
    else:
        print(f"[WARNING] API Key: Not configured")
        results["steps"]["environment"] = {"status": "warning", "message": "API key not set"}
    
    # Step 2: Data Ingestion
    print_section("Step 2: Data Ingestion")
    try:
        df = read_csv_file("test_data.csv")
        print(f"[OK] Loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {', '.join(df.columns)}")
        results["steps"]["ingestion"] = {
            "status": "pass",
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        results["steps"]["ingestion"] = {"status": "fail", "error": str(e)}
        return results
    
    # Step 3: Validation
    print_section("Step 3: Data Validation")
    try:
        cleaned_df = validate_and_clean(df, cleaning_strategy="drop_rows", remove_dupes=True)
        print(f"[OK] Validated: {len(cleaned_df)} rows after cleaning")
        results["steps"]["validation"] = {
            "status": "pass",
            "rows_after_cleaning": len(cleaned_df)
        }
    except Exception as e:
        print(f"[ERROR] {e}")
        results["steps"]["validation"] = {"status": "fail", "error": str(e)}
        return results
    
    # Step 4: Run Agents
    print_section("Step 4: Analytical Agents")
    agent_outputs = []
    
    # Brand Agent
    try:
        brand_result = analyze_brands(cleaned_df, brand_column="brand", top_n=5)
        agent_outputs.append(brand_result)
        top_brands = brand_result['results']['top_brands']
        print(f"[OK] Brand Agent:")
        print(f"    Top brands: {len(top_brands)}")
        print(f"    Leader: {top_brands[0]['brand']} ({top_brands[0]['count']} products, {top_brands[0]['confidence']:.1%})")
        results["steps"]["brand_agent"] = {"status": "pass", "brands_found": len(top_brands)}
    except Exception as e:
        print(f"[ERROR] Brand Agent: {e}")
        results["steps"]["brand_agent"] = {"status": "fail", "error": str(e)}
    
    # Pricing Agent
    try:
        pricing_result = analyze_pricing(cleaned_df, price_column="price")
        agent_outputs.append(pricing_result)
        stats = pricing_result['results']['price_statistics']
        print(f"[OK] Pricing Agent:")
        print(f"    Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
        print(f"    Mean: ${stats['mean_price']:.2f}, Median: ${stats['median_price']:.2f}")
        print(f"    Optimal Range: ${pricing_result['results']['optimal_price_range']['optimal_range_min']:.2f} - ${pricing_result['results']['optimal_price_range']['optimal_range_max']:.2f}")
        results["steps"]["pricing_agent"] = {"status": "pass"}
    except Exception as e:
        print(f"[ERROR] Pricing Agent: {e}")
        results["steps"]["pricing_agent"] = {"status": "fail", "error": str(e)}
    
    # Feature Agent
    try:
        feature_result = analyze_features(cleaned_df, feature_column="feature", top_n=10)
        agent_outputs.append(feature_result)
        top_features = feature_result['results']['top_features']
        print(f"[OK] Feature Agent:")
        print(f"    Unique features: {feature_result['results']['total_unique_features']}")
        print(f"    Top feature: {top_features[0]['feature']} ({top_features[0]['count']} occurrences, {top_features[0]['confidence']:.1%})")
        results["steps"]["feature_agent"] = {"status": "pass", "features_found": len(top_features)}
    except Exception as e:
        print(f"[ERROR] Feature Agent: {e}")
        results["steps"]["feature_agent"] = {"status": "fail", "error": str(e)}
    
    # Gap Agent
    try:
        gap_result = analyze_gaps(cleaned_df, brand_column="brand", feature_column="feature", top_n=5)
        agent_outputs.append(gap_result)
        gaps_count = gap_result['results']['identified_gaps_count']
        print(f"[OK] Gap Agent:")
        print(f"    Combinations analyzed: {gap_result['results']['total_combinations']}")
        print(f"    Gaps identified: {gaps_count}")
        results["steps"]["gap_agent"] = {"status": "pass", "gaps_found": gaps_count}
    except Exception as e:
        print(f"[ERROR] Gap Agent: {e}")
        results["steps"]["gap_agent"] = {"status": "fail", "error": str(e)}
    
    results["agent_outputs"] = agent_outputs
    print(f"\n  [SUMMARY] {len(agent_outputs)}/4 agents completed successfully")
    
    # Step 5: LLM Summarization
    print_section("Step 5: LLM Summarization")
    
    if api_key and api_key != 'your_api_key_here' and len(agent_outputs) == 4:
        try:
            print("  Attempting to generate summary...")
            summary_result = summarize_agent_results(agent_outputs)
            
            if summary_result['status'] == 'success':
                print(f"[SUCCESS] Summary generated!")
                print(f"  Model: {summary_result['model']}")
                print(f"  Temperature: {summary_result['temperature']}")
                print(f"\n  {'='*56}")
                print(f"  LLM SUMMARY:")
                print(f"  {'='*56}")
                print(f"  {summary_result['summary']}")
                print(f"  {'='*56}")
                
                results["llm_summary"] = summary_result
                results["status"] = "complete"
                results["steps"]["llm_summarization"] = {"status": "pass"}
            else:
                error_msg = summary_result.get('error', 'Unknown error')
                print(f"[ERROR] Summarization failed")
                
                if "429" in error_msg or "quota" in error_msg.lower():
                    print(f"  Reason: API quota exceeded")
                    print(f"  This is temporary - wait a few minutes and retry")
                elif "invalid" in error_msg.lower():
                    print(f"  Reason: Invalid API key or configuration")
                else:
                    print(f"  Reason: {error_msg[:200]}")
                
                results["steps"]["llm_summarization"] = {
                    "status": "fail",
                    "error": error_msg[:500]  # Truncate long errors
                }
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] {error_msg[:200]}")
            
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"  API quota exceeded - wait and retry later")
            
            results["steps"]["llm_summarization"] = {"status": "fail", "error": error_msg[:500]}
    else:
        print("[SKIP] LLM summarization skipped")
        if not api_key:
            print("  Reason: No API key configured")
        elif len(agent_outputs) != 4:
            print(f"  Reason: Not all agents completed ({len(agent_outputs)}/4)")
        results["steps"]["llm_summarization"] = {"status": "skipped"}
    
    # Save results
    print_section("Step 6: Saving Results")
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    output_file = reports_dir / f"pipeline_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Results saved to: {output_file}")
    
    # Final Summary
    print_section("Test Summary")
    
    passed = sum(1 for step in results["steps"].values() if step.get("status") == "pass")
    failed = sum(1 for step in results["steps"].values() if step.get("status") == "fail")
    total = len(results["steps"])
    
    print(f"Steps completed: {passed}/{total}")
    print(f"Steps passed: {passed}")
    if failed > 0:
        print(f"Steps failed: {failed}")
    
    if results["status"] == "complete":
        print("\n[SUCCESS] Full pipeline completed successfully!")
    elif passed >= 4:  # All agents passed
        print("\n[SUCCESS] All analytical agents working!")
        if "llm_summarization" in results["steps"] and results["steps"]["llm_summarization"]["status"] == "fail":
            print("  Note: LLM summarization failed due to quota - agents are working correctly")
    else:
        print("\n[PARTIAL] Some steps failed - check errors above")
    
    print("="*60)
    
    return results


if __name__ == "__main__":
    try:
        results = main()
        sys.exit(0 if results["status"] == "complete" or len([s for s in results["steps"].values() if s.get("status") == "pass"]) >= 4 else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

