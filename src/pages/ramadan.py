"""
Ramadan Analysis Page
Detailed analysis of Ramadan donation patterns
"""

import streamlit as st
import pandas as pd
from ..services.metrics_service import calculate_kpis
from ..components.kpi_cards import display_ramadan_kpis
from ..components.ramadan_charts import (
    create_ramadan_comparison_chart,
    create_islamic_events_chart,
    create_hijri_months_chart
)


def render_ramadan_page(df: pd.DataFrame):
    """
    Render the Ramadan analysis page.
    
    Args:
        df: Input DataFrame
    """
    st.title(":material/nightlight: Ramadan & Islamic Calendar Analysis")
    
    # Display Ramadan themed image
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/images/2.jpeg", use_container_width=True)
        except:
            pass  # Skip if image not found
    
    st.markdown("---")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    # Check if Ramadan data is available
    if 'is_ramadan' not in df.columns:
        st.warning("Ramadan data not available. Please run preprocessing with Hijri calendar integration.")
        return
    
    ramadan_count = df['is_ramadan'].sum()
    
    if ramadan_count == 0:
        st.info("No Ramadan donations found in the dataset.")
        return
    
    # KPIs
    st.header("Ramadan Impact Overview")
    kpis = calculate_kpis(df)
    display_ramadan_kpis(kpis)
    
    # Key insights
    st.subheader(":material/search: Key Insights")
    
    ramadan_df = df[df['is_ramadan'] == True]
    non_ramadan_df = df[df['is_ramadan'] == False]
    
    ramadan_avg = ramadan_df['amount'].mean()
    non_ramadan_avg = non_ramadan_df['amount'].mean()
    increase = ((ramadan_avg - non_ramadan_avg) / non_ramadan_avg * 100) if non_ramadan_avg > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **Ramadan Boost**
        
        Average donations during Ramadan are **{increase:+.1f}%** {"higher" if increase > 0 else "lower"} 
        than non-Ramadan periods.
        """)
    
    with col2:
        ramadan_pct = (len(ramadan_df) / len(df) * 100)
        st.info(f"""
        **Donation Concentration**
        
        **{ramadan_pct:.1f}%** of all donations occur during Ramadan, 
        representing **{len(ramadan_df):,}** donations.
        """)
    
    with col3:
        ramadan_amount_pct = (ramadan_df['amount'].sum() / df['amount'].sum() * 100)
        st.info(f"""
        **Financial Impact**
        
        Ramadan donations account for **{ramadan_amount_pct:.1f}%** 
        of total donation amount.
        """)
    
    st.divider()
    
    # Ramadan Comparison Chart
    st.header("Ramadan vs Non-Ramadan Comparison")
    fig = create_ramadan_comparison_chart(df)
    st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Category Performance During Ramadan
    if 'donationtype' in df.columns or 'donationtype_en' in df.columns:
        st.header("Category Performance: Ramadan vs Non-Ramadan")
        
        column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
        
        ramadan_cats = ramadan_df.groupby(column)['amount'].agg(['sum', 'count']).reset_index()
        non_ramadan_cats = non_ramadan_df.groupby(column)['amount'].agg(['sum', 'count']).reset_index()
        
        ramadan_cats.columns = ['Category', 'Ramadan_Amount', 'Ramadan_Count']
        non_ramadan_cats.columns = ['Category', 'NonRamadan_Amount', 'NonRamadan_Count']
        
        comparison = pd.merge(ramadan_cats, non_ramadan_cats, on='Category', how='outer').fillna(0)
        comparison['Ramadan_Avg'] = comparison['Ramadan_Amount'] / comparison['Ramadan_Count'].replace(0, 1)
        comparison['NonRamadan_Avg'] = comparison['NonRamadan_Amount'] / comparison['NonRamadan_Count'].replace(0, 1)
        comparison['Increase_%'] = ((comparison['Ramadan_Avg'] - comparison['NonRamadan_Avg']) / comparison['NonRamadan_Avg'].replace(0, 1) * 100).round(1)
        
        top_increased = comparison.nlargest(5, 'Increase_%')[['Category', 'Increase_%']]
        
        st.subheader("Top Categories with Ramadan Boost")
        for idx, row in top_increased.iterrows():
            if row['Increase_%'] > 0:
                st.success(f"**{row['Category']}**: +{row['Increase_%']:.1f}% increase during Ramadan")
    
    st.divider()
    
    # Islamic Events Analysis
    if 'islamic_event' in df.columns:
        st.header("Donations During Islamic Events")
        
        events_df = df[df['islamic_event'].notna()]
        
        if not events_df.empty:
            fig = create_islamic_events_chart(df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Event details table
            with st.expander(":material/analytics: Islamic Events Details"):
                event_stats = events_df.groupby('islamic_event').agg({
                    'amount': ['sum', 'mean', 'count']
                }).reset_index()
                
                event_stats.columns = ['Event', 'Total Amount', 'Avg Amount', 'Count']
                event_stats['Total Amount'] = event_stats['Total Amount'].apply(lambda x: f"AED {x:,.2f}")
                event_stats['Avg Amount'] = event_stats['Avg Amount'].apply(lambda x: f"AED {x:,.2f}")
                
                st.dataframe(event_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No specific Islamic event data available in the dataset.")
    
    st.divider()
    
    # Hijri Calendar Analysis
    if 'hijri_month_name' in df.columns:
        st.header("Donations by Hijri Month")
        
        hijri_df = df[df['hijri_month_name'].notna()]
        
        if not hijri_df.empty:
            fig = create_hijri_months_chart(df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Hijri month details
            with st.expander(":material/analytics: Hijri Month Details"):
                hijri_stats = hijri_df.groupby('hijri_month_name').agg({
                    'amount': ['sum', 'mean', 'count']
                }).reset_index()
                
                hijri_stats.columns = ['Hijri Month', 'Total Amount', 'Avg Amount', 'Count']
                hijri_stats['Total Amount'] = hijri_stats['Total Amount'].apply(lambda x: f"AED {x:,.2f}")
                hijri_stats['Avg Amount'] = hijri_stats['Avg Amount'].apply(lambda x: f"AED {x:,.2f}")
                hijri_stats = hijri_stats.sort_values('Count', ascending=False)
                
                st.dataframe(hijri_stats, use_container_width=True, hide_index=True)
        else:
            st.info("No Hijri calendar data available in the dataset.")
    
    # Ramadan Data Explorer
    with st.expander(":material/search: Ramadan Data Explorer"):
        st.subheader("Ramadan Donations Sample")
        
        display_cols = ['donationdate', 'amount', 'donationtype']
        if 'donationtype_en' in ramadan_df.columns:
            display_cols.append('donationtype_en')
        if 'hijri_month_name' in ramadan_df.columns:
            display_cols.append('hijri_month_name')
        
        available_cols = [col for col in display_cols if col in ramadan_df.columns]
        
        st.dataframe(
            ramadan_df[available_cols].head(100),
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Showing first 100 of {len(ramadan_df):,} Ramadan donations")
