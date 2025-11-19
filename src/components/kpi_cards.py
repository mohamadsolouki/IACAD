"""
KPI Cards Component
Display key metrics in card format
"""

import streamlit as st
from typing import Optional


def display_kpi_cards(kpis: dict, col_count: int = 4):
    """
    Display KPI metrics in card format.
    
    Args:
        kpis: Dictionary with KPI values
        col_count: Number of columns to display
    """
    if not kpis:
        st.warning("No KPI data available")
        return
    
    # First row - Main metrics
    cols = st.columns(3)
    
    with cols[0]:
        st.metric(
            label="Total Donations",
            value=f"{kpis['total_donations']:,}",
            delta=None
        )
    
    with cols[1]:
        st.metric(
            label="Total Amount",
            value=f"AED {kpis['total_amount']:,.2f}",
            delta=None
        )
    
    with cols[2]:
        st.metric(
            label="Average Donation",
            value=f"AED {kpis['avg_donation']:,.2f}",
            delta=None
        )


def display_ramadan_kpis(kpis: dict):
    """
    Display Ramadan-specific KPI metrics.
    
    Args:
        kpis: Dictionary with KPI values
    """
    if not kpis:
        return
    
    cols = st.columns(3)
    
    with cols[0]:
        st.metric(
            label="Ramadan Donations",
            value=f"{kpis['ramadan_donations']:,}",
            delta=f"{kpis['ramadan_percentage']:.1f}% of total"
        )
    
    with cols[1]:
        st.metric(
            label="Ramadan Amount",
            value=f"AED {kpis['ramadan_amount']:,.2f}",
            delta=None
        )
    
    with cols[2]:
        ramadan_avg = kpis['ramadan_avg']
        non_ramadan_avg = kpis['non_ramadan_avg']
        delta = ramadan_avg - non_ramadan_avg if non_ramadan_avg > 0 else 0
        delta_pct = (delta / non_ramadan_avg * 100) if non_ramadan_avg > 0 else 0
        
        st.metric(
            label="Ramadan Avg Donation",
            value=f"AED {ramadan_avg:,.2f}",
            delta=f"{delta_pct:+.1f}% vs non-Ramadan"
        )


def display_comparison_metrics(comparison: dict):
    """
    Display side-by-side comparison metrics.
    
    Args:
        comparison: Comparison dictionary from metrics_service.compare_periods
    """
    period1 = comparison['period1']
    period2 = comparison['period2']
    changes = comparison['changes']
    
    st.subheader(f"{period1['label']} vs {period2['label']}")
    
    cols = st.columns(4)
    
    metrics_to_show = [
        ('total_donations', 'Total Donations', ''),
        ('total_amount', 'Total Amount', 'AED '),
        ('avg_donation', 'Avg Donation', 'AED '),
        ('ramadan_donations', 'Ramadan Donations', '')
    ]
    
    for col, (key, label, prefix) in zip(cols, metrics_to_show):
        with col:
            val2 = period2['kpis'][key]
            change_pct = changes[key]['percentage']
            
            st.metric(
                label=label,
                value=f"{prefix}{val2:,.2f}" if 'amount' in key.lower() else f"{val2:,}",
                delta=f"{change_pct:+.1f}%"
            )


def display_stat_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None
):
    """
    Display a single statistic card.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Change indicator (optional)
        help_text: Tooltip text (optional)
    """
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )
