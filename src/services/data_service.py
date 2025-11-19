"""
Data Service
Handles all data loading, processing, and transformation
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Optional
from ..config.settings import DATA_PATH, RAW_DATA_PATH, DATA_CACHE_TTL


@st.cache_data(ttl=DATA_CACHE_TTL)
def load_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load preprocessed donation data with caching.
    
    Args:
        file_path: Path to the data file. If None, uses default DATA_PATH
        
    Returns:
        DataFrame with processed donation data
    """
    if file_path is None:
        file_path = DATA_PATH
    
    try:
        # Check if processed file exists
        if not file_path.exists():
            st.warning(f"Processed data file not found: {file_path}")
            st.info("Attempting to load raw data as fallback...")
            
            # Try to load raw data as fallback
            if RAW_DATA_PATH.exists():
                return _load_raw_data_fallback()
            else:
                st.error("Neither processed nor raw data file found!")
                st.info("Please run: `python preprocess_data.py` to generate the processed dataset.")
                return pd.DataFrame()
        
        # Load processed data
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Convert date columns
        df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['donationdate'])
        
        # Create date column (date only, no time)
        df['date'] = df['donationdate'].dt.date
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


def _load_raw_data_fallback() -> pd.DataFrame:
    """
    Load raw data and create minimal required columns.
    Used as fallback when processed data is not available.
    """
    df = pd.read_csv(RAW_DATA_PATH, encoding='utf-8')
    df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df = df.dropna(subset=['donationdate', 'amount'])
    
    # Add minimal required columns
    df['year'] = df['donationdate'].dt.year
    df['month'] = df['donationdate'].dt.month
    df['month_name'] = df['donationdate'].dt.strftime('%B')
    df['quarter'] = df['donationdate'].dt.quarter
    df['day'] = df['donationdate'].dt.day
    df['weekday'] = df['donationdate'].dt.day_name()
    df['week'] = df['donationdate'].dt.isocalendar().week
    df['hour'] = df['donationdate'].dt.hour
    df['date'] = df['donationdate'].dt.date
    
    # Add empty Hijri columns
    df['is_ramadan'] = False
    df['islamic_event'] = None
    df['hijri_month'] = None
    df['hijri_month_name'] = None
    df['donationtype_en'] = df.get('donationtype', '')
    
    st.warning("⚠️ Using raw data without Hijri calendar and translations.")
    st.info("For full features, please run: `python preprocess_data.py`")
    
    return df


def filter_data_by_date_range(
    df: pd.DataFrame, 
    start_date, 
    end_date
) -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: Input DataFrame
        start_date: Start date (datetime or date object)
        end_date: End date (datetime or date object)
        
    Returns:
        Filtered DataFrame
    """
    mask = (df['donationdate'].dt.date >= start_date) & \
           (df['donationdate'].dt.date <= end_date)
    return df[mask].copy()


def filter_data_by_categories(
    df: pd.DataFrame, 
    categories: list,
    column: str = 'donationtype'
) -> pd.DataFrame:
    """
    Filter DataFrame by donation categories.
    
    Args:
        df: Input DataFrame
        categories: List of categories to keep
        column: Column name to filter on
        
    Returns:
        Filtered DataFrame
    """
    if not categories:
        return df
    
    # Try English column first if available
    if 'donationtype_en' in df.columns:
        column = 'donationtype_en'
    
    return df[df[column].isin(categories)].copy()


def get_date_range(df: pd.DataFrame) -> tuple:
    """
    Get the min and max dates from the DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (min_date, max_date)
    """
    if df.empty:
        return None, None
    
    min_date = df['donationdate'].min().date()
    max_date = df['donationdate'].max().date()
    
    return min_date, max_date


def get_unique_categories(df: pd.DataFrame) -> list:
    """
    Get list of unique donation categories.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Sorted list of unique categories
    """
    if df.empty:
        return []
    
    # Try English column first if available
    column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
    
    categories = df[column].dropna().unique().tolist()
    return sorted(categories)


def export_to_csv(df: pd.DataFrame) -> str:
    """
    Export DataFrame to CSV string.
    
    Args:
        df: DataFrame to export
        
    Returns:
        CSV string
    """
    return df.to_csv(index=False).encode('utf-8')


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics about the dataset.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {}
    
    return {
        'total_records': len(df),
        'date_range': get_date_range(df),
        'total_amount': df['amount'].sum(),
        'unique_donors': df['id'].nunique() if 'id' in df.columns else 0,
        'unique_categories': len(get_unique_categories(df)),
        'ramadan_records': df['is_ramadan'].sum() if 'is_ramadan' in df.columns else 0,
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }
