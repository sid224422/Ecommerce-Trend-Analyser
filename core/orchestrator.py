"""
Agent Orchestration Module

Simple orchestration function to run all analytical agents and collect results.
"""

import pandas as pd
from typing import Dict, Optional
from datetime import datetime

from agents.brand_agent import analyze_brands
from agents.pricing_agent import analyze_pricing
from agents.feature_agent import analyze_features
from agents.gap_agent import analyze_gaps


def run_all_agents(
    df: pd.DataFrame,
    brand_column: str = "brand",
    price_column: str = "price",
    feature_column: str = "feature",
    top_n_brands: int = 10,
    top_n_features: int = 15,
    gap_threshold: float = -0.5
) -> Dict:
    """
    Run all analytical agents on validated DataFrame and collect outputs.
    
    Args:
        df: Validated pandas DataFrame with market data
        brand_column: Name of brand column (default: "brand")
        price_column: Name of price column (default: "price")
        feature_column: Name of feature column (default: "feature")
        top_n_brands: Number of top brands to return (default: 10)
        top_n_features: Number of top features to return (default: 15)
        gap_threshold: Threshold for gap identification (default: -0.5)
    
    Returns:
        Dictionary containing all agent outputs and metadata
    """
    # Run all agents
    brand_result = analyze_brands(df, brand_column=brand_column, top_n=top_n_brands)
    pricing_result = analyze_pricing(df, price_column=price_column)
    feature_result = analyze_features(df, feature_column=feature_column, top_n=top_n_features)
    gap_result = analyze_gaps(
        df,
        brand_column=brand_column,
        feature_column=feature_column,
        gap_threshold=gap_threshold
    )
    
    # Collect all outputs
    results = {
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "brand": brand_result,
            "pricing": pricing_result,
            "feature": feature_result,
            "gap": gap_result
        },
        "total_records": len(df)
    }
    
    return results

