"""
Donor Analysis Page
Detailed donor behavior and segmentation analysis
"""

import streamlit as st
import pandas as pd
from ..services.metrics_service import calculate_donor_statistics, get_top_donors
from ..components.donor_charts import (
    create_top_donors_chart,
    create_donor_behavior_analysis,
    create_donor_retention_chart,
    create_donation_frequency_distribution
)


def render_donors_page(df: pd.DataFrame, dark_mode: bool = False):
    """
    Render the donor analysis page.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
    """
    st.title("👥 Donor Analysis")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    if 'id' not in df.columns:
        st.warning("Donor ID information not available in the dataset.")
        return
    
    st.markdown("""
    Understand donor behavior, identify top contributors, and analyze donation patterns.
    """)
    
    # Donor Statistics
    st.header("Donor Statistics")
    
    donor_stats = calculate_donor_statistics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Donors",
            value=f"{donor_stats['total_donors']:,}"
        )
    
    with col2:
        st.metric(
            label="Repeat Donors",
            value=f"{donor_stats['repeat_donors']:,}",
            delta=f"{(donor_stats['repeat_donors'] / donor_stats['total_donors'] * 100) if donor_stats['total_donors'] > 0 else 0:.1f}%"
        )
    
    with col3:
        st.metric(
            label="One-Time Donors",
            value=f"{donor_stats['one_time_donors']:,}",
            delta=f"{(donor_stats['one_time_donors'] / donor_stats['total_donors'] * 100) if donor_stats['total_donors'] > 0 else 0:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Avg Donations/Donor",
            value=f"{donor_stats['avg_donations_per_donor']:.1f}"
        )
    
    st.divider()
    
    # Top Donors
    st.header("Top Donors")
    
    top_n = st.slider("Number of top donors to show", 5, 50, 10, key="top_donors_slider")
    
    fig = create_top_donors_chart(df, top_n, dark_mode)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top Donors Table
    with st.expander("📊 Top Donors Details"):
        top_donors_df = get_top_donors(df, top_n)
        
        if not top_donors_df.empty:
            top_donors_df['rank'] = range(1, len(top_donors_df) + 1)
            top_donors_df['donor_id'] = top_donors_df['donor_id'].apply(lambda x: f"Donor {hash(x) % 10000}")
            top_donors_df['total_amount'] = top_donors_df['total_amount'].apply(lambda x: f"AED {x:,.2f}")
            top_donors_df['avg_amount'] = top_donors_df['avg_amount'].apply(lambda x: f"AED {x:,.2f}")
            
            display_df = top_donors_df[['rank', 'donor_id', 'total_amount', 'donation_count', 'avg_amount']]
            display_df.columns = ['Rank', 'Donor', 'Total Amount', 'Donations', 'Avg Amount']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Donor Behavior Segmentation
    st.header("Donor Behavior Segmentation")
    
    fig = create_donor_behavior_analysis(df, dark_mode)
    st.plotly_chart(fig, use_container_width=True)
    
    # Segmentation insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Segment Definitions")
        st.markdown("""
        - **One-time**: 1 donation
        - **Occasional**: 2-4 donations
        - **Regular**: 5-9 donations
        - **Frequent**: 10+ donations
        """)
    
    with col2:
        st.subheader("Key Insights")
        
        donor_counts = df.groupby('id').size()
        repeat_rate = (donor_counts > 1).sum() / len(donor_counts) * 100
        
        st.info(f"""
        **Repeat Donor Rate**: {repeat_rate:.1f}%
        
        {repeat_rate:.1f}% of donors have made multiple donations, 
        indicating {"strong" if repeat_rate > 30 else "moderate" if repeat_rate > 15 else "developing"} donor retention.
        """)
    
    st.divider()
    
    # Donation Frequency Distribution
    st.header("Donation Frequency Distribution")
    
    fig = create_donation_frequency_distribution(df, dark_mode)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Donor Retention Over Time
    if 'year' in df.columns:
        st.header("Donor Retention Over Time")
        
        fig = create_donor_retention_chart(df, dark_mode)
        st.plotly_chart(fig, use_container_width=True)
        
        # Year-over-year retention analysis
        with st.expander("📈 Year-over-Year Retention Analysis"):
            yearly_donors = df.groupby('year')['id'].nunique().reset_index()
            yearly_donors.columns = ['Year', 'Unique Donors']
            
            # Calculate growth
            yearly_donors['Growth'] = yearly_donors['Unique Donors'].pct_change() * 100
            yearly_donors['Growth'] = yearly_donors['Growth'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
            
            st.dataframe(yearly_donors, use_container_width=True, hide_index=True)
    
    # Donor Deep Dive
    with st.expander("🔍 Donor Deep Dive"):
        st.subheader("Donor Statistics by Category")
        
        if 'donationtype' in df.columns:
            column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
            
            category_donor_stats = df.groupby(column).agg({
                'id': 'nunique',
                'amount': ['sum', 'mean', 'count']
            }).reset_index()
            
            category_donor_stats.columns = ['Category', 'Unique Donors', 'Total Amount', 'Avg Amount', 'Donations']
            category_donor_stats['Avg Amount'] = category_donor_stats['Avg Amount'].apply(lambda x: f"AED {x:,.2f}")
            category_donor_stats['Total Amount'] = category_donor_stats['Total Amount'].apply(lambda x: f"AED {x:,.2f}")
            category_donor_stats = category_donor_stats.sort_values('Unique Donors', ascending=False)
            
            st.dataframe(category_donor_stats.head(15), use_container_width=True, hide_index=True)
