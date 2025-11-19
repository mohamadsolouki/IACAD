"""
Temporal Analysis Page
Detailed temporal patterns and trends
"""

import streamlit as st
import pandas as pd
from ..components.temporal_charts import (
    create_monthly_heatmap,
    create_hourly_pattern,
    create_weekday_pattern,
    create_time_weekday_heatmap,
    create_yearly_monthly_analysis
)


def render_temporal_page(df: pd.DataFrame, dark_mode: bool = False):
    """
    Render the temporal analysis page.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
    """
    st.title(":material/schedule: Temporal Analysis")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    st.markdown("""
    Analyze donation patterns across different time dimensions: 
    hours, days, weeks, months, and years.
    """)
    
    # Monthly Heatmap
    st.header("Monthly Donation Heatmap")
    st.markdown("See how donations vary across months and years")
    
    if 'year' in df.columns and 'month_name' in df.columns:
        fig = create_monthly_heatmap(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Year and month data not available.")
    
    st.divider()
    
    # Year-over-Year Comparison
    st.header("Year-over-Year Monthly Comparison")
    
    if 'year' in df.columns and 'month_name' in df.columns:
        fig = create_yearly_monthly_analysis(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Year and month data not available.")
    
    st.divider()
    
    # Day Patterns
    st.header("Day-of-Week Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weekly Pattern")
        if 'weekday' in df.columns:
            fig = create_weekday_pattern(df, dark_mode)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Weekday data not available.")
    
    with col2:
        st.subheader("Busiest Days")
        if 'weekday' in df.columns:
            weekday_stats = df.groupby('weekday').agg({
                'amount': ['sum', 'mean', 'count']
            }).reset_index()
            weekday_stats.columns = ['Day', 'Total', 'Average', 'Count']
            
            busiest = weekday_stats.nlargest(1, 'Total')['Day'].values[0]
            highest_avg = weekday_stats.nlargest(1, 'Average')['Day'].values[0]
            most_donations = weekday_stats.nlargest(1, 'Count')['Day'].values[0]
            
            st.metric("Highest Total", busiest)
            st.metric("Highest Average", highest_avg)
            st.metric("Most Donations", most_donations)
        else:
            st.warning("Weekday data not available.")
    
    st.divider()
    
    # Hour Patterns
    st.header("Hourly Patterns")
    
    if 'hour' in df.columns:
        fig = create_hourly_pattern(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
        
        # Hourly insights
        with st.expander(":material/access_time: Hourly Insights"):
            hourly_stats = df.groupby('hour')['amount'].agg(['sum', 'mean', 'count']).reset_index()
            hourly_stats.columns = ['Hour', 'Total Amount', 'Avg Amount', 'Count']
            
            peak_hour = int(hourly_stats.nlargest(1, 'Total Amount')['Hour'].values[0])
            peak_count_hour = int(hourly_stats.nlargest(1, 'Count')['Hour'].values[0])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Peak Donation Hour (Amount)", f"{peak_hour:02d}:00")
            
            with col2:
                st.metric("Peak Donation Hour (Count)", f"{peak_count_hour:02d}:00")
            
            st.dataframe(hourly_stats, use_container_width=True, hide_index=True)
    else:
        st.warning("Hour data not available.")
    
    st.divider()
    
    # Time × Weekday Heatmap
    st.header("Hour × Day of Week Heatmap")
    st.markdown("Identify the busiest time slots throughout the week")
    
    if 'hour' in df.columns and 'weekday' in df.columns:
        fig = create_time_weekday_heatmap(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Hour and weekday data not available.")
    
    # Temporal Statistics
    with st.expander(":material/analytics: Temporal Statistics Summary"):
        if 'year' in df.columns:
            st.subheader("Yearly Statistics")
            yearly_stats = df.groupby('year').agg({
                'amount': ['sum', 'mean', 'count'],
                'id': 'nunique'
            }).reset_index()
            yearly_stats.columns = ['Year', 'Total Amount', 'Avg Amount', 'Count', 'Unique Donors']
            yearly_stats['Total Amount'] = yearly_stats['Total Amount'].apply(lambda x: f"AED {x:,.2f}")
            yearly_stats['Avg Amount'] = yearly_stats['Avg Amount'].apply(lambda x: f"AED {x:,.2f}")
            
            st.dataframe(yearly_stats, use_container_width=True, hide_index=True)
        
        if 'quarter' in df.columns:
            st.subheader("Quarterly Statistics")
            quarterly_stats = df.groupby(['year', 'quarter']).agg({
                'amount': ['sum', 'mean', 'count']
            }).reset_index()
            quarterly_stats.columns = ['Year', 'Quarter', 'Total Amount', 'Avg Amount', 'Count']
            quarterly_stats['Total Amount'] = quarterly_stats['Total Amount'].apply(lambda x: f"AED {x:,.2f}")
            quarterly_stats['Avg Amount'] = quarterly_stats['Avg Amount'].apply(lambda x: f"AED {x:,.2f}")
            
            st.dataframe(quarterly_stats.tail(12), use_container_width=True, hide_index=True)
