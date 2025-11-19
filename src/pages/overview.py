"""
Overview Page
Main dashboard overview with key metrics and trends
"""

import streamlit as st
import pandas as pd
from ..services.metrics_service import calculate_kpis, calculate_growth_rate
from ..components.kpi_cards import display_kpi_cards, display_ramadan_kpis
from ..components.time_series_charts import (
    create_time_series_chart,
    create_cumulative_chart,
    create_moving_average_chart
)
from ..components.category_charts import (
    create_category_distribution,
    create_category_bar_chart,
    create_amount_distribution
)


def render_overview_page(df: pd.DataFrame, dark_mode: bool = False):
    """
    Render the overview dashboard page.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
    """
    st.title(":material/dashboard: Dashboard Overview")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    # KPIs Section with Data Summary
    st.header("Key Performance Indicators & Data Summary")
    kpis = calculate_kpis(df)
    display_kpi_cards(kpis)
    
    # Additional Data Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    
    with col2:
        st.metric("Max Donation", f"AED {df['amount'].max():,.0f}")
    
    with col3:
        st.metric("Median Donation", f"AED {df['amount'].median():,.0f}")
    
    with col4:
        st.metric("Std Deviation", f"AED {df['amount'].std():,.0f}")
    
    # Growth metrics
    st.subheader("Growth Metrics")
    cols = st.columns(2)
    
    with cols[0]:
        monthly_growth = calculate_growth_rate(df, 'month')
        st.metric(
            label="Month-over-Month Growth",
            value=f"{monthly_growth:+.1f}%",
            delta=None
        )
    
    with cols[1]:
        yearly_growth = calculate_growth_rate(df, 'year')
        st.metric(
            label="Year-over-Year Growth",
            value=f"{yearly_growth:+.1f}%",
            delta=None
        )
    
    st.divider()
    
    # Ramadan Highlights
    if 'is_ramadan' in df.columns and df['is_ramadan'].sum() > 0:
        st.header(":material/nightlight: Ramadan Highlights")
        display_ramadan_kpis(kpis)
        st.divider()
    
    # Time Series Charts
    st.header("Donation Trends")
    
    tab1, tab2, tab3 = st.tabs(["Time Series", "Cumulative", "Moving Average"])
    
    with tab1:
        fig = create_time_series_chart(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_cumulative_chart(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        window = st.slider("Moving Average Window (days)", 3, 30, 7)
        fig = create_moving_average_chart(df, window, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Category Analysis
    st.header("Category Analysis")
    
    top_n = st.slider("Number of categories to show", 5, 20, 10, key="category_slider")
    
    fig = create_category_distribution(df, top_n, dark_mode)
    st.plotly_chart(fig, use_container_width=True)
    
    fig = create_category_bar_chart(df, top_n, dark_mode)
    st.plotly_chart(fig, use_container_width=True)
