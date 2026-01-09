"""Test all agents with comprehensive data"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.ingestion import read_csv_file
from core.validator import validate_and_clean
from core.orchestrator import run_all_agents
import pandas as pd

print("="*60)
print("Comprehensive Analysis Test")
print("="*60)

# Load data
df = read_csv_file('test_data_comprehensive.csv')
print(f"\n[1] Loaded: {len(df)} rows")

# Validate
cleaned_df = validate_and_clean(df, cleaning_strategy="drop_rows", remove_dupes=True)
print(f"[2] Validated: {len(cleaned_df)} rows")

# Run all agents
results = run_all_agents(cleaned_df)
print(f"[3] All agents executed")

# Brand Analysis
brand_result = results["agents"]["brand"]
print(f"\n[BRAND] Total brands: {brand_result['results']['total_unique_brands']}")
print(f"  Top 5 brands:")
for i, brand in enumerate(brand_result['results']['top_brands'][:5], 1):
    print(f"    {i}. {brand['brand']}: {brand['count']} products ({brand['confidence']:.1%})")

# Pricing Analysis
pricing_result = results["agents"]["pricing"]
stats = pricing_result['results']['price_statistics']
print(f"\n[PRICING] Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
print(f"  Mean: ${stats['mean_price']:.2f}, Median: ${stats['median_price']:.2f}")
optimal = pricing_result['results']['optimal_price_range']
print(f"  Optimal: ${optimal['optimal_range_min']:.2f} - ${optimal['optimal_range_max']:.2f}")

# Feature Analysis
feature_result = results["agents"]["feature"]
print(f"\n[FEATURE] Unique features: {feature_result['results']['total_unique_features']}")
print(f"  Top 5 features:")
for i, feat in enumerate(feature_result['results']['top_features'][:5], 1):
    print(f"    {i}. {feat['feature']}: {feat['count']} occurrences ({feat['confidence']:.1%})")

# Gap Analysis
gap_result = results["agents"]["gap"]
print(f"\n[GAP] Combinations analyzed: {gap_result['results']['total_combinations']}")
print(f"  Gaps identified: {gap_result['results']['identified_gaps_count']}")
if gap_result['results']['top_gaps']:
    print(f"  Top 3 gaps:")
    for i, gap in enumerate(gap_result['results']['top_gaps'][:3], 1):
        print(f"    {i}. {gap['brand']} + {gap['feature']}: score {gap['gap_score']:.4f}")
else:
    print(f"  No significant gaps found")

print("\n" + "="*60)
print("All features tested successfully!")
print("="*60)

