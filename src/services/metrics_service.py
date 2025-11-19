"""
Metrics Service
Handles all KPI calculations and statistical analysis
"""

import pandas as pd
import numpy as np
from scipy import stats
import streamlit as st
from typing import Dict, Optional
from ..config.settings import CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)
def calculate_kpis(df: pd.DataFrame) -> Dict:
    """
    Calculate key performance indicators.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with KPI metrics
    """
    if df.empty:
        return _empty_kpis()
    
    ramadan_df = df[df['is_ramadan'] == True] if 'is_ramadan' in df.columns else pd.DataFrame()
    non_ramadan_df = df[df['is_ramadan'] == False] if 'is_ramadan' in df.columns else df
    
    return {
        'total_donations': len(df),
        'total_amount': df['amount'].sum(),
        'avg_donation': df['amount'].mean(),
        'median_donation': df['amount'].median(),
        'std_donation': df['amount'].std(),
        'unique_donors': df['id'].nunique() if 'id' in df.columns else 0,
        'unique_types': df['donationtype'].nunique() if 'donationtype' in df.columns else 0,
        'ramadan_donations': len(ramadan_df),
        'ramadan_amount': ramadan_df['amount'].sum() if len(ramadan_df) > 0 else 0,
        'ramadan_percentage': (len(ramadan_df) / len(df) * 100) if len(df) > 0 else 0,
        'ramadan_avg': ramadan_df['amount'].mean() if len(ramadan_df) > 0 else 0,
        'non_ramadan_avg': non_ramadan_df['amount'].mean() if len(non_ramadan_df) > 0 else 0,
        'max_donation': df['amount'].max(),
        'min_donation': df['amount'].min(),
    }


def _empty_kpis() -> Dict:
    """Return empty KPI dictionary."""
    return {
        'total_donations': 0,
        'total_amount': 0,
        'avg_donation': 0,
        'median_donation': 0,
        'std_donation': 0,
        'unique_donors': 0,
        'unique_types': 0,
        'ramadan_donations': 0,
        'ramadan_amount': 0,
        'ramadan_percentage': 0,
        'ramadan_avg': 0,
        'non_ramadan_avg': 0,
        'max_donation': 0,
        'min_donation': 0,
    }


@st.cache_data(ttl=CACHE_TTL)
def calculate_growth_rate(df: pd.DataFrame, period: str = 'month') -> float:
    """
    Calculate growth rate for a given period.
    
    Args:
        df: Input DataFrame
        period: 'month' or 'year'
        
    Returns:
        Growth rate as percentage
    """
    if df.empty or len(df) < 2:
        return 0.0
    
    try:
        if period == 'month':
            grouped = df.groupby(df['donationdate'].dt.to_period('M'))['amount'].sum()
        elif period == 'year':
            grouped = df.groupby(df['donationdate'].dt.to_period('Y'))['amount'].sum()
        else:
            return 0.0
        
        if len(grouped) < 2:
            return 0.0
        
        current = grouped.iloc[-1]
        previous = grouped.iloc[-2]
        
        if previous == 0:
            return 0.0
        
        return ((current - previous) / previous) * 100
    except Exception:
        return 0.0


@st.cache_data(ttl=CACHE_TTL)
def calculate_donor_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate donor-related statistics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with donor statistics
    """
    if df.empty or 'id' not in df.columns:
        return {
            'total_donors': 0,
            'repeat_donors': 0,
            'one_time_donors': 0,
            'avg_donations_per_donor': 0,
            'top_donor_amount': 0,
            'top_donor_count': 0
        }
    
    donor_stats = df.groupby('id').agg({
        'amount': ['sum', 'count', 'mean']
    })
    
    donor_stats.columns = ['total_amount', 'donation_count', 'avg_amount']
    
    return {
        'total_donors': len(donor_stats),
        'repeat_donors': len(donor_stats[donor_stats['donation_count'] > 1]),
        'one_time_donors': len(donor_stats[donor_stats['donation_count'] == 1]),
        'avg_donations_per_donor': donor_stats['donation_count'].mean(),
        'top_donor_amount': donor_stats['total_amount'].max(),
        'top_donor_count': donor_stats['donation_count'].max(),
        'median_donations_per_donor': donor_stats['donation_count'].median(),
    }


@st.cache_data(ttl=CACHE_TTL)
def calculate_time_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate time-based statistics.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary with time statistics
    """
    if df.empty:
        return {}
    
    daily_amounts = df.groupby('date')['amount'].sum()
    
    return {
        'busiest_day': df.groupby('date').size().idxmax(),
        'highest_amount_day': daily_amounts.idxmax(),
        'avg_daily_amount': daily_amounts.mean(),
        'avg_daily_donations': len(df) / len(df['date'].unique()),
        'busiest_month': df.groupby('month_name').size().idxmax() if 'month_name' in df.columns else None,
        'busiest_weekday': df.groupby('weekday').size().idxmax() if 'weekday' in df.columns else None,
    }


@st.cache_data(ttl=CACHE_TTL)
def calculate_category_statistics(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Calculate statistics by donation category.
    
    Args:
        df: Input DataFrame
        top_n: Number of top categories to return
        
    Returns:
        DataFrame with category statistics
    """
    if df.empty:
        return pd.DataFrame()
    
    column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
    
    category_stats = df.groupby(column).agg({
        'amount': ['sum', 'mean', 'count'],
        'id': 'nunique'
    }).reset_index()
    
    category_stats.columns = ['category', 'total_amount', 'avg_amount', 'count', 'unique_donors']
    category_stats['percentage'] = (category_stats['total_amount'] / category_stats['total_amount'].sum()) * 100
    
    return category_stats.nlargest(top_n, 'total_amount')


def compare_periods(
    df1: pd.DataFrame, 
    df2: pd.DataFrame,
    period1_label: str = "Period 1",
    period2_label: str = "Period 2"
) -> Dict:
    """
    Compare KPIs between two periods.
    
    Args:
        df1: DataFrame for period 1
        df2: DataFrame for period 2
        period1_label: Label for period 1
        period2_label: Label for period 2
        
    Returns:
        Dictionary with comparison metrics
    """
    kpis1 = calculate_kpis(df1)
    kpis2 = calculate_kpis(df2)
    
    comparison = {
        'period1': {
            'label': period1_label,
            'kpis': kpis1
        },
        'period2': {
            'label': period2_label,
            'kpis': kpis2
        },
        'changes': {}
    }
    
    # Calculate percentage changes
    for key in ['total_donations', 'total_amount', 'avg_donation', 'ramadan_donations', 'ramadan_amount']:
        val1 = kpis1[key]
        val2 = kpis2[key]
        
        if val1 > 0:
            change = ((val2 - val1) / val1) * 100
        else:
            change = 0.0
        
        comparison['changes'][key] = {
            'absolute': val2 - val1,
            'percentage': change
        }
    
    return comparison


@st.cache_data(ttl=CACHE_TTL)
def get_top_donors(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get top donors by total donation amount.
    
    Args:
        df: Input DataFrame
        top_n: Number of top donors to return
        
    Returns:
        DataFrame with top donor statistics
    """
    if df.empty or 'id' not in df.columns:
        return pd.DataFrame()
    
    top_donors = df.groupby('id').agg({
        'amount': ['sum', 'count', 'mean'],
    }).reset_index()
    
    top_donors.columns = ['donor_id', 'total_amount', 'donation_count', 'avg_amount']
    
    return top_donors.nlargest(top_n, 'total_amount')
