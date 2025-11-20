"""
Comparison Tool Page
Compare donations between different time periods
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ..services.data_service import filter_data_by_date_range, filter_data_by_categories, get_unique_categories
from ..services.metrics_service import compare_periods
from ..components.kpi_cards import display_comparison_metrics
from ..components.category_charts import create_category_bar_chart


def render_comparison_page(df: pd.DataFrame):
    """
    Render the comparison tool page.
    
    Args:
        df: Input DataFrame
    """
    st.title(":material/compare: Period Comparison Tool")
    
    if df.empty:
        st.warning("No data available to display.")
        return
    
    st.markdown("""
    Compare donation patterns between two different time periods to identify trends and changes.
    """)
    
    # Get date range from data
    min_date = df['donationdate'].min().date()
    max_date = df['donationdate'].max().date()
    
    # Period Selection
    st.header("Select Periods to Compare")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(":material/calendar_today: Period 1")
        
        period1_start = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key="period1_start"
        )
        
        period1_end = st.date_input(
            "End Date",
            value=min_date + timedelta(days=90),
            min_value=min_date,
            max_value=max_date,
            key="period1_end"
        )
    
    with col2:
        st.subheader(":material/calendar_today: Period 2")
        
        period2_start = st.date_input(
            "Start Date",
            value=min_date + timedelta(days=91),
            min_value=min_date,
            max_value=max_date,
            key="period2_start"
        )
        
        period2_end = st.date_input(
            "End Date",
            value=min_date + timedelta(days=180),
            min_value=min_date,
            max_value=max_date,
            key="period2_end"
        )
    
    # Category filters
    st.subheader("🏷️ Filter by Categories (Optional)")
    
    categories = get_unique_categories(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        period1_categories = st.multiselect(
            "Period 1 Categories",
            options=categories,
            key="period1_categories"
        )
    
    with col2:
        period2_categories = st.multiselect(
            "Period 2 Categories",
            options=categories,
            key="period2_categories"
        )
    
    # Validation
    if period1_start >= period1_end:
        st.error("Period 1: Start date must be before end date")
        return
    
    if period2_start >= period2_end:
        st.error("Period 2: Start date must be before end date")
        return
    
    # Filter data
    df1 = filter_data_by_date_range(df, period1_start, period1_end)
    df2 = filter_data_by_date_range(df, period2_start, period2_end)
    
    if period1_categories:
        df1 = filter_data_by_categories(df1, period1_categories)
    
    if period2_categories:
        df2 = filter_data_by_categories(df2, period2_categories)
    
    if df1.empty:
        st.warning("Period 1: No data found for the selected filters")
        return
    
    if df2.empty:
        st.warning("Period 2: No data found for the selected filters")
        return
    
    st.divider()
    
    # Comparison Results
    st.header(":material/analytics: Comparison Results")
    
    # Create comparison
    period1_label = f"{period1_start} to {period1_end}"
    period2_label = f"{period2_start} to {period2_end}"
    
    comparison = compare_periods(df1, df2, period1_label, period2_label)
    
    # Display comparison metrics
    display_comparison_metrics(comparison)
    
    st.divider()
    
    # Detailed Comparison Table
    st.subheader("Detailed Metrics Comparison")
    
    kpis1 = comparison['period1']['kpis']
    kpis2 = comparison['period2']['kpis']
    changes = comparison['changes']
    
    comparison_data = []
    
    metrics_info = [
        ('total_donations', 'Total Donations', ''),
        ('total_amount', 'Total Amount', 'AED '),
        ('avg_donation', 'Average Donation', 'AED '),
        ('median_donation', 'Median Donation', 'AED '),
        ('ramadan_donations', 'Ramadan Donations', ''),
        ('ramadan_amount', 'Ramadan Amount', 'AED '),
    ]
    
    for key, label, prefix in metrics_info:
        val1 = kpis1[key]
        val2 = kpis2[key]
        
        change = changes.get(key, {})
        change_pct = change.get('percentage', 0) if change else 0
        
        if 'amount' in key.lower() or 'avg' in key.lower() or 'median' in key.lower():
            val1_str = f"{prefix}{val1:,.2f}"
            val2_str = f"{prefix}{val2:,.2f}"
        else:
            val1_str = f"{prefix}{val1:,}"
            val2_str = f"{prefix}{val2:,}"
        
        comparison_data.append({
            'Metric': label,
            'Period 1': val1_str,
            'Period 2': val2_str,
            'Change (%)': f"{change_pct:+.1f}%"
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Key Insights from Comparison
    st.subheader(":material/lightbulb: Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        amount_change = changes.get('total_amount', {}).get('percentage', 0)
        if abs(amount_change) > 20:
            emoji = "🚀" if amount_change > 0 else "⚠️"
            st.info(f"{emoji} **Significant Change**\\n\\nTotal amount changed by {amount_change:+.1f}%")
        else:
            st.success("✓ **Stable Performance**\\n\\nAmount change within ±20%")
    
    with col2:
        count_change = changes.get('total_donations', {}).get('percentage', 0)
        avg_change = changes.get('avg_donation', {}).get('percentage', 0)
        
        if count_change > 0 and avg_change > 0:
            st.success("📈 **Growth in Both**\\n\\nMore donations AND higher average")
        elif count_change < 0 and avg_change > 0:
            st.warning("⚖️ **Quality over Quantity**\\n\\nFewer but larger donations")
        elif count_change > 0 and avg_change < 0:
            st.info("📊 **Volume Increase**\\n\\nMore but smaller donations")
        else:
            st.error("📉 **Decline**\\n\\nBoth count and average decreased")
    
    with col3:
        if 'ramadan_amount' in kpis1 and 'ramadan_amount' in kpis2:
            ramadan_change = changes.get('ramadan_amount', {}).get('percentage', 0)
            if abs(ramadan_change) > 10:
                st.info(f"🌙 **Ramadan Impact**\\n\\nRamadan donations {ramadan_change:+.1f}%")
    
    st.divider()
    
    # Side-by-side Category Comparison
    st.header("Category Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Period 1: {period1_label}")
        if not df1.empty:
            fig1 = create_category_bar_chart(df1, 10)
            st.plotly_chart(fig1, use_container_width=True)
            st.caption(f"Total: AED {df1['amount'].sum():,.2f} | Count: {len(df1):,}")
        else:
            st.info("No data for this period")
    
    with col2:
        st.subheader(f"Period 2: {period2_label}")
        if not df2.empty:
            fig2 = create_category_bar_chart(df2, 10)
            st.plotly_chart(fig2, use_container_width=True)
            st.caption(f"Total: AED {df2['amount'].sum():,.2f} | Count: {len(df2):,}")
        else:
            st.info("No data for this period")
    
    # Export Comparison
    with st.expander(":material/download: Export Comparison Data"):
        st.download_button(
            label="Download Period 1 Data",
            data=df1.to_csv(index=False).encode('utf-8'),
            file_name=f"period1_{period1_start}_to_{period1_end}.csv",
            mime="text/csv"
        )
        
        st.download_button(
            label="Download Period 2 Data",
            data=df2.to_csv(index=False).encode('utf-8'),
            file_name=f"period2_{period2_start}_to_{period2_end}.csv",
            mime="text/csv"
        )
