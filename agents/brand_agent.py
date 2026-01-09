"""
Brand Analysis Agent

Deterministic agent that analyzes brand distribution in the dataset.
Computes top brands, counts, and confidence scores.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime


def count_brands(df: pd.DataFrame, brand_column: str) -> pd.Series:
    """
    Count occurrences of each brand in the dataset.
    
    Args:
        df: Pandas DataFrame with brand data
        brand_column: Name of the column containing brand names
    
    Returns:
        Series with brand counts, sorted in descending order
    """
    if brand_column not in df.columns:
        raise ValueError(f"Column '{brand_column}' not found in DataFrame")
    
    brand_counts = df[brand_column].value_counts()
    return brand_counts


def get_top_brands(brand_counts: pd.Series, top_n: int = 10) -> Dict[str, int]:
    """
    Get top N brands by count.
    
    Args:
        brand_counts: Series with brand counts
        top_n: Number of top brands to return
    
    Returns:
        Dictionary mapping brand names to counts
    """
    top_brands = brand_counts.head(top_n)
    return top_brands.to_dict()


def calculate_brand_confidence(brand_counts: pd.Series, total_records: int) -> Dict[str, float]:
    """
    Calculate confidence score for each brand.
    Confidence = count / total_records
    
    Args:
        brand_counts: Series with brand counts
        total_records: Total number of records in dataset
    
    Returns:
        Dictionary mapping brand names to confidence scores
    """
    if total_records == 0:
        return {}
    
    confidence_scores = (brand_counts / total_records).to_dict()
    return confidence_scores


def analyze_brands(df: pd.DataFrame, brand_column: str = "brand", top_n: int = 10) -> Dict:
    """
    Main analysis function for brand agent.
    
    Args:
        df: Pandas DataFrame with market data
        brand_column: Name of the column containing brand names
        top_n: Number of top brands to include in results
    
    Returns:
        Structured JSON output with brand analysis results
    """
    total_records = len(df)
    
    # Count brands
    brand_counts = count_brands(df, brand_column)
    
    # Get top brands
    top_brands = get_top_brands(brand_counts, top_n)
    
    # Calculate confidence for top brands
    top_brand_counts = pd.Series(top_brands)
    confidence_scores = calculate_brand_confidence(top_brand_counts, total_records)
    
    # Calculate overall confidence (weighted average of top brands)
    overall_confidence = sum(confidence_scores.values())
    
    # Prepare results
    brand_list = []
    for brand, count in top_brands.items():
        brand_list.append({
            "brand": brand,
            "count": int(count),
            "confidence": round(confidence_scores.get(brand, 0.0), 4)
        })
    
    results = {
        "total_unique_brands": len(brand_counts),
        "top_brands": brand_list,
        "total_records": total_records
    }
    
    return {
        "agent_name": "brand_agent",
        "results": results,
        "confidence": round(min(overall_confidence, 1.0), 4),
        "timestamp": datetime.now().isoformat()
    }

