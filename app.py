"""
UAE Donations Analytics Dashboard
Main Streamlit Application

A comprehensive dashboard for analyzing donation data with:
- Interactive visualizations
- Ramadan and Islamic calendar analysis
- Temporal pattern analysis
- Donor behavior insights
- Period comparison tools
"""

import streamlit as st
from src.config.settings import (
    APP_TITLE,
    APP_ICON,
    PAGE_TITLE,
    LAYOUT,
    INITIAL_SIDEBAR_STATE
)
from src.services.data_service import load_data, get_data_summary, export_to_csv
from src.pages import (
    render_overview_page,
    render_ramadan_page,
    render_temporal_page,
    render_donors_page,
    render_comparison_page
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=APP_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

def load_custom_css():
    """Load custom CSS for better styling."""
    st.markdown("""
    <style>
        /* Main title styling */
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* Metric card styling */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom info boxes */
        .info-box {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render the sidebar with navigation and filters."""
    with st.sidebar:
        st.title(f"{APP_ICON} {APP_TITLE}")
        st.markdown("---")
        
        # Navigation
        st.header("📍 Navigation")
        page = st.radio(
            "Select Page",
            options=[
                "Overview",
                "Ramadan Analysis",
                "Temporal Analysis",
                "Donor Analysis",
                "Comparison Tool"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Theme Toggle
        st.header("🎨 Theme")
        dark_mode = st.toggle("Dark Mode", value=False)
        
        st.markdown("---")
        
        # Data Info
        st.header("ℹ️ Data Information")
        
        if 'data' in st.session_state and not st.session_state.data.empty:
            summary = get_data_summary(st.session_state.data)
            
            st.metric("Total Records", f"{summary['total_records']:,}")
            
            if summary['date_range'][0] and summary['date_range'][1]:
                st.text(f"From: {summary['date_range'][0]}")
                st.text(f"To: {summary['date_range'][1]}")
            
            st.metric("Total Amount", f"AED {summary['total_amount']:,.0f}")
            
            # Data export
            st.markdown("---")
            st.header("💾 Export Data")
            
            csv_data = export_to_csv(st.session_state.data)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="donations_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Load data to see information")
        
        st.markdown("---")
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **UAE Donations Analytics Dashboard**
            
            Version 2.0.0
            
            A comprehensive analytics platform for 
            understanding donation patterns and trends.
            
            Features:
            - Interactive visualizations
            - Ramadan analysis
            - Temporal patterns
            - Donor insights
            - Period comparison
            """)
    
    return page, dark_mode

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    # Load data
    if st.session_state.data is None:
        with st.spinner("Loading data..."):
            st.session_state.data = load_data()
    
    df = st.session_state.data
    
    # Check if data loaded successfully
    if df.empty:
        st.error("❌ Failed to load data. Please check if the data files exist.")
        st.info("""
        **Required Files:**
        - `data/General_Donation_Processed.csv` (preferred)
        - OR `data/General_Donation.csv` (fallback)
        
        **To generate processed data:**
        ```bash
        python preprocess_data.py
        ```
        """)
        return
    
    # Render sidebar and get navigation
    page, dark_mode = render_sidebar()
    
    # Store theme in session state
    st.session_state.dark_mode = dark_mode
    
    # Route to appropriate page
    if page == "Overview":
        render_overview_page(df, dark_mode)
    
    elif page == "Ramadan Analysis":
        render_ramadan_page(df, dark_mode)
    
    elif page == "Temporal Analysis":
        render_temporal_page(df, dark_mode)
    
    elif page == "Donor Analysis":
        render_donors_page(df, dark_mode)
    
    elif page == "Comparison Tool":
        render_comparison_page(df, dark_mode)

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    main()
