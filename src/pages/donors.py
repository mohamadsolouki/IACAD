"""
Donor Analysis Page
Detailed donor behavior and segmentation analysis
"""

import streamlit as st
import pandas as pd
from ..services.metrics_service import calculate_donor_statistics, get_top_donors
from ..components.donor_charts import create_top_donors_chart


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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="Total Donors",
            value=f"{donor_stats['total_donors']:,}"
        )
    
    with col2:
        st.metric(
            label="Total Donations",
            value=f"{len(df):,}"
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
