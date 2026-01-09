"""
Data Ingestion Module

This module handles reading CSV files and loading data into Pandas DataFrames.
Simple, straightforward CSV reading with basic error handling.
"""

import pandas as pd
from pathlib import Path
from typing import Optional


def read_csv_file(file_path: str) -> Optional[pd.DataFrame]:
    """
    Read a CSV file and return a Pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file (string or Path object)
    
    Returns:
        DataFrame containing the CSV data, or None if reading fails
    
    Raises:
        FileNotFoundError: If the file does not exist
        pd.errors.EmptyDataError: If the file is empty
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        if df.empty:
            raise pd.errors.EmptyDataError(f"CSV file is empty: {file_path}")
        
        return df
    
    except pd.errors.EmptyDataError:
        raise
    except Exception as e:
        raise ValueError(f"Error reading CSV file {file_path}: {str(e)}")


def validate_csv_format(df: pd.DataFrame) -> bool:
    """
    Basic validation that the DataFrame has data.
    
    Args:
        df: Pandas DataFrame to validate
    
    Returns:
        True if DataFrame is valid, False otherwise
    """
    if df is None:
        return False
    
    if df.empty:
        return False
    
    if len(df.columns) == 0:
        return False
    
    return True

