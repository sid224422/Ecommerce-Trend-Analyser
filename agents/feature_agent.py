"""
Feature Analysis Agent

Deterministic agent that extracts and counts most common product features.
Analyzes feature columns or feature strings in the dataset.
"""

import pandas as pd
from typing import Dict, List
from datetime import datetime


def extract_features_from_column(df: pd.DataFrame, feature_column: str) -> pd.Series:
    """
    Extract individual features from a feature column.
    Assumes features are separated by common delimiters.
    
    Args:
        df: Pandas DataFrame with feature data
        feature_column: Name of the column containing features
    
    Returns:
        Series with individual feature counts
    """
    if feature_column not in df.columns:
        raise ValueError(f"Column '{feature_column}' not found in DataFrame")
    
    # Handle features as strings (comma, semicolon, or pipe separated)
    all_features = []
    
    for value in df[feature_column].dropna():
        if pd.notna(value):
            # Try common delimiters
            if isinstance(value, str):
                # Split by comma, semicolon, or pipe
                features = value.replace(';', ',').replace('|', ',').split(',')
                features = [f.strip().lower() for f in features if f.strip()]
                all_features.extend(features)
            else:
                # If not a string, convert to string and add as single feature
                all_features.append(str(value).lower().strip())
    
    if not all_features:
        return pd.Series(dtype=int)
    
    # Count feature occurrences
    feature_counts = pd.Series(all_features).value_counts()
    return feature_counts


def extract_features_from_multiple_columns(df: pd.DataFrame, feature_columns: List[str]) -> pd.Series:
    """
    Extract features from multiple boolean/categorical columns.
    
    Args:
        df: Pandas DataFrame with feature columns
        feature_columns: List of column names that represent features
    
    Returns:
        Series with feature counts
    """
    feature_counts = {}
    
    for col in feature_columns:
        if col not in df.columns:
            continue
        
        # Count non-null, non-zero, non-empty values as feature presence
        if df[col].dtype == 'bool' or df[col].dtype == 'int64':
            count = (df[col] != 0).sum()
            feature_counts[col] = count
        else:
            # For categorical/string columns, count unique non-empty values
            unique_values = df[col].dropna().unique()
            for value in unique_values:
                if pd.notna(value) and value != '' and value != '0':
                    feature_name = f"{col}: {value}"
                    count = (df[col] == value).sum()
                    feature_counts[feature_name] = count
    
    return pd.Series(feature_counts)


def get_top_features(feature_counts: pd.Series, top_n: int = 15) -> Dict[str, int]:
    """
    Get top N features by count.
    
    Args:
        feature_counts: Series with feature counts
        top_n: Number of top features to return
    
    Returns:
        Dictionary mapping feature names to counts
    """
    top_features = feature_counts.head(top_n)
    return top_features.to_dict()


def analyze_features(df: pd.DataFrame, 
                    feature_column: str = None,
                    feature_columns: List[str] = None,
                    top_n: int = 15) -> Dict:
    """
    Main analysis function for feature agent.
    
    Args:
        df: Pandas DataFrame with market data
        feature_column: Single column containing feature strings (optional)
        feature_columns: List of columns representing features (optional)
        top_n: Number of top features to include in results
    
    Returns:
        Structured JSON output with feature analysis results
    """
    total_records = len(df)
    
    # Determine extraction method
    if feature_column:
        feature_counts = extract_features_from_column(df, feature_column)
    elif feature_columns:
        feature_counts = extract_features_from_multiple_columns(df, feature_columns)
    else:
        # Try to auto-detect: look for columns with 'feature' in name
        feature_cols = [col for col in df.columns if 'feature' in col.lower()]
        if feature_cols:
            feature_counts = extract_features_from_column(df, feature_cols[0])
        else:
            raise ValueError("No feature column specified and none auto-detected")
    
    if len(feature_counts) == 0:
        return {
            "agent_name": "feature_agent",
            "results": {
                "total_features": 0,
                "top_features": [],
                "total_records": total_records
            },
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
    
    # Get top features
    top_features = get_top_features(feature_counts, top_n)
    
    # Calculate confidence scores for top features
    total_feature_mentions = feature_counts.sum()
    confidence_scores = {}
    
    for feature, count in top_features.items():
        confidence = count / total_records if total_records > 0 else 0.0
        confidence_scores[feature] = confidence
    
    # Overall confidence: coverage of top features
    overall_confidence = sum(confidence_scores.values())
    
    # Prepare results
    feature_list = []
    for feature, count in top_features.items():
        feature_list.append({
            "feature": feature,
            "count": int(count),
            "confidence": round(confidence_scores.get(feature, 0.0), 4)
        })
    
    results = {
        "total_unique_features": len(feature_counts),
        "top_features": feature_list,
        "total_records": total_records,
        "total_feature_mentions": int(total_feature_mentions)
    }
    
    return {
        "agent_name": "feature_agent",
        "results": results,
        "confidence": round(min(overall_confidence, 1.0), 4),
        "timestamp": datetime.now().isoformat()
    }

