"""
Data Validation and Cleaning Module

This module validates data integrity, handles missing values, and ensures
data quality for downstream analysis. All operations are deterministic.
"""

import pandas as pd
from typing import Dict, List, Optional


def get_data_summary(df: pd.DataFrame) -> Dict:
    """
    Get basic statistics about the dataset.
    
    Args:
        df: Pandas DataFrame to analyze
    
    Returns:
        Dictionary with summary statistics
    """
    return {
        "total_records": len(df),
        "total_columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values_per_column": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict()
    }


def clean_missing_values(df: pd.DataFrame, strategy: str = "drop_rows") -> pd.DataFrame:
    """
    Handle missing values in the DataFrame.
    
    Args:
        df: Pandas DataFrame to clean
        strategy: Strategy for handling missing values
                 - "drop_rows": Remove rows with any missing values
                 - "drop_columns": Remove columns with any missing values
                 - "keep": Do nothing (return as-is)
    
    Returns:
        Cleaned DataFrame
    """
    if strategy == "drop_rows":
        cleaned_df = df.dropna()
    elif strategy == "drop_columns":
        cleaned_df = df.dropna(axis=1)
    elif strategy == "keep":
        cleaned_df = df.copy()
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    
    return cleaned_df


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Check if DataFrame contains all required columns.
    
    Args:
        df: Pandas DataFrame to validate
        required_columns: List of column names that must be present
    
    Returns:
        True if all required columns exist, False otherwise
    """
    existing_columns = set(df.columns)
    required_set = set(required_columns)
    
    return required_set.issubset(existing_columns)


def get_missing_columns(df: pd.DataFrame, required_columns: List[str]) -> List[str]:
    """
    Get list of required columns that are missing from DataFrame.
    
    Args:
        df: Pandas DataFrame to check
        required_columns: List of column names that should be present
    
    Returns:
        List of missing column names
    """
    existing_columns = set(df.columns)
    required_set = set(required_columns)
    
    return list(required_set - existing_columns)


def validate_data_types(df: pd.DataFrame, column_types: Dict[str, str]) -> Dict[str, bool]:
    """
    Validate that specified columns have expected data types.
    
    Args:
        df: Pandas DataFrame to validate
        column_types: Dictionary mapping column names to expected types
                     (e.g., {"price": "float64", "brand": "object"})
    
    Returns:
        Dictionary mapping column names to validation results (True/False)
    """
    results = {}
    
    for column, expected_type in column_types.items():
        if column not in df.columns:
            results[column] = False
            continue
        
        actual_type = str(df[column].dtype)
        results[column] = (actual_type == expected_type)
    
    return results


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows from DataFrame.
    
    Args:
        df: Pandas DataFrame to deduplicate
    
    Returns:
        DataFrame with duplicates removed
    """
    return df.drop_duplicates()


def validate_and_clean(df: pd.DataFrame, 
                       required_columns: Optional[List[str]] = None,
                       cleaning_strategy: str = "drop_rows",
                       remove_dupes: bool = True) -> pd.DataFrame:
    """
    Comprehensive validation and cleaning pipeline.
    
    Args:
        df: Pandas DataFrame to validate and clean
        required_columns: Optional list of required column names
        cleaning_strategy: Strategy for handling missing values
        remove_dupes: Whether to remove duplicate rows
    
    Returns:
        Validated and cleaned DataFrame
    
    Raises:
        ValueError: If required columns are missing
    """
    # Check required columns
    if required_columns:
        if not validate_required_columns(df, required_columns):
            missing = get_missing_columns(df, required_columns)
            raise ValueError(f"Missing required columns: {missing}")
    
    # Remove duplicates first
    if remove_dupes:
        df = remove_duplicates(df)
    
    # Clean missing values
    df = clean_missing_values(df, strategy=cleaning_strategy)
    
    # Final check - ensure we still have data
    if df.empty:
        raise ValueError("DataFrame is empty after cleaning")
    
    return df

