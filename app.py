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

def load_custom_css(dark_mode: bool = False):
    """Load custom CSS for better styling."""
    bg_color = "#0e1117" if dark_mode else "#ffffff"
    text_color = "#fafafa" if dark_mode else "#0e1117"
    sidebar_bg = "#1e1e1e" if dark_mode else "#f5f5f5"
    card_bg = "#262730" if dark_mode else "#ffffff"
    border_color = "#3a3a3a" if dark_mode else "#e6e6e6"
    
    st.markdown(f"""
    <style>
        /* Main app background */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {text_color};
        }}
        
        /* Metric card styling */
        [data-testid="stMetricValue"] {{
            font-size: 1.8rem;
            color: {text_color};
        }}
        
        [data-testid="stMetricLabel"] {{
            color: {text_color};
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Compact metric styling */
        div[data-testid="stMetric"] {{
            background-color: {card_bg};
            padding: 0.8rem;
            border-radius: 0.5rem;
            border: 1px solid {border_color};
        }}
        
        /* Radio button styling */
        div[role="radiogroup"] label {{
            padding: 0.4rem 0;
        }}
        
        /* Divider styling */
        hr {{
            margin: 0.8rem 0;
            border-color: {border_color};
        }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render the sidebar with navigation and filters."""
    with st.sidebar:
        # App Title
        st.markdown(f"### {APP_ICON} {APP_TITLE}")
        
        # Theme Toggle (at top for easy access)
        dark_mode = st.toggle(":material/dark_mode: Dark Mode", value=st.session_state.get('dark_mode', False))
        
        st.divider()
        
        # Navigation
        st.markdown("**:material/menu: Navigation**")
        page = st.radio(
            "Select Page",
            options=[
                ":material/dashboard: Overview",
                ":material/nightlight: Ramadan Analysis",
                ":material/schedule: Temporal Analysis",
                ":material/group: Donor Analysis",
                ":material/compare: Comparison Tool"
            ],
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        # Extract page name without icon
        page = page.split(" ", 1)[1]
        
        st.divider()
        
        # Data Summary (compact)
        if 'data' in st.session_state and not st.session_state.data.empty:
            summary = get_data_summary(st.session_state.data)
            
            st.markdown("**:material/analytics: Data Summary**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Records", f"{summary['total_records']:,}", label_visibility="visible")
            with col2:
                st.metric("Amount", f"{summary['total_amount']/1000000:.1f}M", 
                         label_visibility="visible",
                         help=f"AED {summary['total_amount']:,.0f}")
            
            # Date range in compact format
            if summary['date_range'][0] and summary['date_range'][1]:
                st.caption(f":material/calendar_month: {summary['date_range'][0]} → {summary['date_range'][1]}")
            
            st.divider()
            
            # Export button (compact)
            csv_data = export_to_csv(st.session_state.data)
            st.download_button(
                label=":material/download: Export CSV",
                data=csv_data,
                file_name="donations_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Footer with version info
        st.divider()
        with st.expander(":material/info: About & Info"):
            st.markdown("""
            **UAE Donations Analytics**  
            *Version 2.0.0*
            
            Comprehensive analytics platform for donation patterns and trends.
            
            **Features:**
            - :material/dashboard: Interactive visualizations
            - :material/nightlight: Ramadan analysis
            - :material/schedule: Temporal patterns
            - :material/group: Donor insights
            - :material/compare: Period comparison
            """)
    
    return page, dark_mode

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Load data
    if st.session_state.data is None:
        with st.spinner("Loading data..."):
            st.session_state.data = load_data()
    
    df = st.session_state.data
    
    # Render sidebar and get navigation
    page, dark_mode = render_sidebar()
    
    # Update dark mode in session state
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    # Load custom CSS with dark mode
    load_custom_css(dark_mode)
    
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
