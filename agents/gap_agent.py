"""
Market Gap Analysis Agent

Deterministic agent that identifies underrepresented brand-feature combinations.
Finds market gaps where certain brand-feature pairs are rare or missing.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime


def get_brand_feature_combinations(df: pd.DataFrame, 
                                   brand_column: str,
                                   feature_column: str) -> pd.DataFrame:
    """
    Extract all brand-feature combinations from the dataset.
    
    Args:
        df: Pandas DataFrame with brand and feature data
        brand_column: Name of the column containing brands
        feature_column: Name of the column containing features
    
    Returns:
        DataFrame with brand-feature combinations and their counts
    """
    if brand_column not in df.columns:
        raise ValueError(f"Column '{brand_column}' not found in DataFrame")
    if feature_column not in df.columns:
        raise ValueError(f"Column '{feature_column}' not found in DataFrame")
    
    # Extract valid combinations
    valid_data = df[[brand_column, feature_column]].dropna()
    
    if len(valid_data) == 0:
        return pd.DataFrame(columns=['brand', 'feature', 'count'])
    
    # Count combinations
    combinations = valid_data.groupby([brand_column, feature_column]).size().reset_index(name='count')
    combinations.columns = ['brand', 'feature', 'count']
    
    return combinations


def calculate_expected_frequency(combination_counts: pd.DataFrame, 
                                total_records: int) -> pd.DataFrame:
    """
    Calculate expected frequency for each brand-feature combination.
    Expected = (brand_count * feature_count) / total_records
    
    Args:
        combination_counts: DataFrame with brand-feature counts
        total_records: Total number of records
    
    Returns:
        DataFrame with expected frequencies added
    """
    if total_records == 0:
        combination_counts['expected_count'] = 0.0
        combination_counts['gap_score'] = 0.0
        return combination_counts
    
    # Calculate brand and feature totals
    brand_totals = combination_counts.groupby('brand')['count'].sum()
    feature_totals = combination_counts.groupby('feature')['count'].sum()
    
    # Calculate expected counts
    expected_counts = []
    gap_scores = []
    
    for _, row in combination_counts.iterrows():
        brand = row['brand']
        feature = row['feature']
        observed = row['count']
        
        brand_total = brand_totals.get(brand, 0)
        feature_total = feature_totals.get(feature, 0)
        
        # Expected frequency if independent
        expected = (brand_total * feature_total) / total_records
        
        expected_counts.append(expected)
        
        # Gap score: negative if underrepresented, positive if overrepresented
        if expected > 0:
            gap_score = (observed - expected) / expected
        else:
            gap_score = 0.0
        
        gap_scores.append(gap_score)
    
    combination_counts['expected_count'] = expected_counts
    combination_counts['gap_score'] = gap_scores
    
    return combination_counts


def identify_gaps(combination_df: pd.DataFrame, 
                 threshold: float = -0.5,
                 min_observations: int = 1) -> pd.DataFrame:
    """
    Identify underrepresented combinations (gaps).
    
    Args:
        combination_df: DataFrame with gap scores
        threshold: Gap score threshold (negative = underrepresented)
        min_observations: Minimum number of observations to consider
    
    Returns:
        DataFrame with identified gaps, sorted by gap score
    """
    # Filter for underrepresented combinations
    gaps = combination_df[
        (combination_df['gap_score'] <= threshold) & 
        (combination_df['count'] >= min_observations)
    ].copy()
    
    # Sort by gap score (most underrepresented first)
    gaps = gaps.sort_values('gap_score').reset_index(drop=True)
    
    return gaps


def analyze_gaps(df: pd.DataFrame,
                brand_column: str = "brand",
                feature_column: str = "feature",
                gap_threshold: float = -0.5,
                top_n: int = 10) -> Dict:
    """
    Main analysis function for gap agent.
    
    Args:
        df: Pandas DataFrame with market data
        brand_column: Name of the column containing brands
        feature_column: Name of the column containing features
        gap_threshold: Threshold for identifying gaps (negative values = underrepresented)
        top_n: Number of top gaps to include in results
    
    Returns:
        Structured JSON output with gap analysis results
    """
    total_records = len(df)
    
    # Get brand-feature combinations
    combinations = get_brand_feature_combinations(df, brand_column, feature_column)
    
    if len(combinations) == 0:
        return {
            "agent_name": "gap_agent",
            "results": {
                "total_combinations": 0,
                "identified_gaps": [],
                "total_records": total_records
            },
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Calculate expected frequencies and gap scores
    combinations = calculate_expected_frequency(combinations, total_records)
    
    # Identify gaps
    gaps = identify_gaps(combinations, threshold=gap_threshold, min_observations=1)
    
    # Get top gaps
    top_gaps = gaps.head(top_n)
    
    # Calculate confidence: ratio of valid combinations to total records
    valid_records = combinations['count'].sum()
    confidence = valid_records / total_records if total_records > 0 else 0.0
    
    # Prepare gap list
    gap_list = []
    for _, row in top_gaps.iterrows():
        gap_list.append({
            "brand": str(row['brand']),
            "feature": str(row['feature']),
            "observed_count": int(row['count']),
            "expected_count": round(float(row['expected_count']), 2),
            "gap_score": round(float(row['gap_score']), 4)
        })
    
    results = {
        "total_combinations": len(combinations),
        "identified_gaps_count": len(gaps),
        "top_gaps": gap_list,
        "total_records": total_records,
        "gap_threshold": gap_threshold
    }
    
    return {
        "agent_name": "gap_agent",
        "results": results,
        "confidence": round(confidence, 4),
        "timestamp": datetime.now().isoformat()
    }

