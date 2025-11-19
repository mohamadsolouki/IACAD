"""
UAE Donations Analytics Dashboard
A comprehensive dashboard for analyzing donation data with interactive visualizations,
dark mode support, and Islamic calendar integration.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from pathlib import Path
from io import StringIO

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_PATH = Path('data/General_Donation_Processed.csv')
RAW_DATA_PATH = Path('data/General_Donation.csv')
APP_TITLE = "UAE Donations Analytics Dashboard"
PORT = 8050

# Light Theme Colors
LIGHT_THEME = {
    'primary': '#2563eb',
    'secondary': '#64748b',
    'success': '#10b981',
    'info': '#06b6d4',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'background': '#f8fafc',
    'card_bg': '#ffffff',
    'text': '#0f172a',
    'text_secondary': '#64748b',
    'border': '#e2e8f0',
    'shadow': 'rgba(0, 0, 0, 0.1)',
}

# Dark Theme Colors
DARK_THEME = {
    'primary': '#3b82f6',
    'secondary': '#94a3b8',
    'success': '#34d399',
    'info': '#22d3ee',
    'warning': '#fbbf24',
    'danger': '#f87171',
    'background': '#0f172a',
    'card_bg': '#1e293b',
    'text': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'border': '#334155',
    'shadow': 'rgba(0, 0, 0, 0.3)',
}

# Chart color palettes
LIGHT_CHART_COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899', '#f97316']
DARK_CHART_COLORS = ['#3b82f6', '#34d399', '#fbbf24', '#f87171', '#22d3ee', '#a78bfa', '#f472b6', '#fb923c']

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_and_process_data(file_path: Path) -> pd.DataFrame:
    """Load preprocessed donation data."""
    try:
        # Check if processed file exists
        if not file_path.exists():
            print(f"Processed data file not found: {file_path}")
            print(f"Please run 'python preprocess_data.py' first to generate the processed dataset.")
            
            # Try to load raw data as fallback
            if RAW_DATA_PATH.exists():
                print(f"Loading raw data from {RAW_DATA_PATH} as fallback...")
                df = pd.read_csv(RAW_DATA_PATH, encoding='utf-8')
                df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                df = df.dropna(subset=['donationdate', 'amount'])
                
                # Add minimal required columns
                df['year'] = df['donationdate'].dt.year
                df['month'] = df['donationdate'].dt.month
                df['month_name'] = df['donationdate'].dt.strftime('%B')
                df['quarter'] = df['donationdate'].dt.quarter
                df['day'] = df['donationdate'].dt.day
                df['weekday'] = df['donationdate'].dt.day_name()
                df['week'] = df['donationdate'].dt.isocalendar().week
                df['hour'] = df['donationdate'].dt.hour
                df['date'] = df['donationdate'].dt.date
                
                # Add empty Hijri columns
                df['is_ramadan'] = False
                df['islamic_event'] = None
                df['hijri_month'] = None
                df['hijri_month_name'] = None
                df['donationtype_en'] = df['donationtype']
                
                print("WARNING: Using raw data without Hijri calendar and translations.")
                print("For full features, please run: python preprocess_data.py")
                return df
            else:
                raise FileNotFoundError(f"Neither processed nor raw data file found!")
        
        # Load processed data
        print(f"Loading preprocessed data from {file_path}...")
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Convert date columns
        df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
        
        # Drop rows with invalid dates
        df = df.dropna(subset=['donationdate'])
        
        # Create date column (date only, no time)
        df['date'] = df['donationdate'].dt.date
        
        print(f"✓ Loaded {len(df):,} preprocessed records")
        print(f"✓ Ramadan donations: {df['is_ramadan'].sum():,} ({df['is_ramadan'].sum() / len(df) * 100:.1f}%)")
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate key performance indicators."""
    ramadan_df = df[df['is_ramadan'] == True]
    non_ramadan_df = df[df['is_ramadan'] == False]
    
    return {
        'total_donations': len(df),
        'total_amount': df['amount'].sum(),
        'avg_donation': df['amount'].mean(),
        'unique_donors': df['id'].nunique(),
        'unique_types': df['donationtype'].nunique(),
        'ramadan_donations': len(ramadan_df),
        'ramadan_amount': ramadan_df['amount'].sum() if len(ramadan_df) > 0 else 0,
        'ramadan_percentage': (len(ramadan_df) / len(df) * 100) if len(df) > 0 else 0,
        'ramadan_avg': ramadan_df['amount'].mean() if len(ramadan_df) > 0 else 0,
        'non_ramadan_avg': non_ramadan_df['amount'].mean() if len(non_ramadan_df) > 0 else 0,
    }

def calculate_growth_rate(df: pd.DataFrame, period: str = 'month') -> float:
    """Calculate growth rate for a given period."""
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

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def get_theme_colors(dark_mode: bool) -> dict:
    """Get theme colors based on mode."""
    return DARK_THEME if dark_mode else LIGHT_THEME

def get_chart_colors(dark_mode: bool) -> list:
    """Get chart color palette based on mode."""
    return DARK_CHART_COLORS if dark_mode else LIGHT_CHART_COLORS

def get_plot_template(dark_mode: bool) -> str:
    """Get plotly template based on theme."""
    return 'plotly_dark' if dark_mode else 'plotly_white'

def create_time_series_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create enhanced time series with Ramadan highlighting."""
    daily_data = df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count',
        'is_ramadan': 'first'
    }).reset_index()
    
    colors = get_theme_colors(dark_mode)
    
    fig = go.Figure()
    
    # Separate Ramadan and non-Ramadan periods
    ramadan_data = daily_data[daily_data['is_ramadan'] == True]
    non_ramadan_data = daily_data[daily_data['is_ramadan'] == False]
    
    # Non-Ramadan data
    fig.add_trace(go.Scatter(
        x=non_ramadan_data['date'],
        y=non_ramadan_data['amount'],
        mode='lines',
        name='Regular Days',
        line=dict(color=colors['primary'], width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(list(int(colors['primary'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}"
    ))
    
    # Ramadan data with highlighting
    fig.add_trace(go.Scatter(
        x=ramadan_data['date'],
        y=ramadan_data['amount'],
        mode='lines',
        name='Ramadan',
        line=dict(color=colors['warning'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(list(int(colors['warning'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
    ))
    
    fig.update_layout(
        title="Donation Trends Over Time (Ramadan Highlighted)",
        xaxis_title="Date",
        yaxis_title="Amount (AED)",
        hovermode='x unified',
        template=get_plot_template(dark_mode),
        height=450,
        margin=dict(l=50, r=50, t=60, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_ramadan_comparison_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create Ramadan vs Non-Ramadan comparison."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Group by Ramadan status
    comparison = df.groupby('is_ramadan').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    comparison.columns = ['is_ramadan', 'total_amount', 'avg_amount', 'count']
    comparison['period'] = comparison['is_ramadan'].map({True: 'Ramadan', False: 'Non-Ramadan'})
    
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Total Amount', 'Average Donation', 'Number of Donations'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=comparison['period'],
            y=comparison['total_amount'],
            marker_color=[chart_colors[3], chart_colors[0]],
            text=comparison['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
            textposition='outside',
            showlegend=False
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=comparison['period'],
            y=comparison['avg_amount'],
            marker_color=[chart_colors[3], chart_colors[0]],
            text=comparison['avg_amount'].apply(lambda x: f'AED {x:,.2f}'),
            textposition='outside',
            showlegend=False
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=comparison['period'],
            y=comparison['count'],
            marker_color=[chart_colors[3], chart_colors[0]],
            text=comparison['count'].apply(lambda x: f'{x:,}'),
            textposition='outside',
            showlegend=False
        ),
        row=1, col=3
    )
    
    fig.update_layout(
        title_text="Ramadan Impact Analysis",
        template=get_plot_template(dark_mode),
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_islamic_events_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create chart showing donations during Islamic events."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Filter events
    event_df = df[df['islamic_event'].notna()].copy()
    
    if len(event_df) == 0:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No Islamic events data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=colors['text_secondary'])
        )
        fig.update_layout(
            template=get_plot_template(dark_mode),
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    event_summary = event_df.groupby('islamic_event').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    event_summary.columns = ['event', 'total', 'average', 'count']
    event_summary = event_summary.sort_values('total', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=event_summary['event'],
        x=event_summary['total'],
        orientation='h',
        marker=dict(
            color=event_summary['total'],
            colorscale='Sunset',
            showscale=False
        ),
        text=event_summary['total'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Total: AED %{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Donations During Islamic Events",
        xaxis_title="Total Amount (AED)",
        yaxis_title="",
        template=get_plot_template(dark_mode),
        height=400,
        margin=dict(l=200, r=50, t=60, b=50)
    )
    
    return fig

def create_hijri_months_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create chart showing donations by Hijri month."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    hijri_data = df[df['hijri_month_name'].notna()].groupby('hijri_month_name').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    # Order by Hijri calendar
    month_order = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani',
                   'Jumada al-Awwal', 'Jumada al-Thani', 'Rajab', 'Shaban',
                   'Ramadan', 'Shawwal', 'Dhul Qadah', 'Dhul Hijjah']
    
    hijri_data['month_order'] = hijri_data['hijri_month_name'].map({m: i for i, m in enumerate(month_order)})
    hijri_data = hijri_data.sort_values('month_order')
    
    # Highlight Ramadan
    colors_list = [chart_colors[3] if m == 'Ramadan' else chart_colors[0] for m in hijri_data['hijri_month_name']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hijri_data['hijri_month_name'],
        y=hijri_data['amount'],
        marker_color=colors_list,
        text=hijri_data['amount'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Amount: AED %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Donations by Hijri Month (Ramadan Highlighted)",
        xaxis_title="Hijri Month",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(dark_mode),
        height=450,
        margin=dict(l=50, r=50, t=60, b=100),
        xaxis=dict(tickangle=-45)
    )
    
    return fig

def create_category_distribution(df: pd.DataFrame, top_n: int = 10, dark_mode: bool = False) -> go.Figure:
    """Create horizontal bar chart for donation types."""
    colors = get_theme_colors(dark_mode)
    
    # Use English translations if available, otherwise use original
    category_col = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
    
    category_data = df.groupby(category_col).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    category_data = category_data.nlargest(top_n, 'amount')
    category_data = category_data.sort_values('amount', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=category_data[category_col],
        x=category_data['amount'],
        orientation='h',
        marker=dict(
            color=category_data['amount'],
            colorscale='Viridis',
            showscale=False
        ),
        text=category_data['amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Donation Categories by Amount",
        xaxis_title="Total Amount (AED)",
        yaxis_title="",
        template=get_plot_template(dark_mode),
        height=500,
        margin=dict(l=200, r=50, t=60, b=50)
    )
    
    return fig

def create_monthly_heatmap(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create heatmap showing donation patterns."""
    heatmap_data = df.groupby(['month_name', 'weekday'])['amount'].sum().reset_index()
    pivot = heatmap_data.pivot(index='weekday', columns='month_name', values='amount')
    
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex([day for day in weekday_order if day in pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='Plasma',
        text=pivot.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 11},
        colorbar=dict(title="Amount (AED)")
    ))
    
    fig.update_layout(
        title="Donation Heatmap: Day of Week vs Month",
        xaxis_title="Month",
        yaxis_title="Day of Week",
        template=get_plot_template(dark_mode),
        height=600,
        margin=dict(l=120, r=50, t=60, b=50)
    )
    
    return fig

def create_hourly_pattern(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create chart showing donation patterns by hour."""
    colors = get_theme_colors(dark_mode)
    
    hourly_data = df.groupby('hour').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Donation Amount by Hour', 'Number of Donations by Hour'),
        vertical_spacing=0.15
    )
    
    fig.add_trace(
        go.Bar(
            x=hourly_data['hour'],
            y=hourly_data['amount'],
            marker_color=colors['primary'],
            name='Amount'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=hourly_data['hour'],
            y=hourly_data['id'],
            marker_color=colors['success'],
            name='Count'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
    fig.update_yaxes(title_text="Amount (AED)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_layout(
        title_text="Donation Patterns by Hour of Day",
        template=get_plot_template(dark_mode),
        height=600,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_distribution_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create histogram showing donation amount distribution."""
    colors = get_theme_colors(dark_mode)
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['amount'],
        nbinsx=50,
        marker_color=colors['primary'],
        opacity=0.7,
        name='Distribution'
    ))
    
    fig.update_layout(
        title="Distribution of Donation Amounts",
        xaxis_title="Amount (AED)",
        yaxis_title="Frequency",
        template=get_plot_template(dark_mode),
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return fig

def create_time_weekday_heatmap(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create heatmap showing donation patterns by hour and weekday."""
    heatmap_data = df.groupby(['weekday', 'hour'])['amount'].sum().reset_index()
    pivot = heatmap_data.pivot(index='weekday', columns='hour', values='amount')
    
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex([day for day in weekday_order if day in pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='RdYlGn',
        text=pivot.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Amount (AED)")
    ))
    
    fig.update_layout(
        title="Donation Heatmap: Hour of Day vs Weekday",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        template=get_plot_template(dark_mode),
        height=600,
        margin=dict(l=120, r=50, t=60, b=50)
    )
    
    return fig

def create_yearly_monthly_analysis(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create comprehensive year-month analysis with count and average."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    yearly_monthly = df.groupby(['year', 'month']).agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    yearly_monthly.columns = ['year', 'month', 'total', 'average', 'count']
    yearly_monthly['year_month'] = yearly_monthly['year'].astype(str) + '-' + yearly_monthly['month'].astype(str).str.zfill(2)
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Total Amount by Year-Month', 'Number of Donations', 'Average Donation Amount'),
        vertical_spacing=0.1,
        row_heights=[0.33, 0.33, 0.34]
    )
    
    # Total amount
    fig.add_trace(
        go.Scatter(
            x=yearly_monthly['year_month'],
            y=yearly_monthly['total'],
            mode='lines+markers',
            name='Total',
            line=dict(color=chart_colors[0], width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor=f"rgba{tuple(list(int(chart_colors[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
        ),
        row=1, col=1
    )
    
    # Count
    fig.add_trace(
        go.Bar(
            x=yearly_monthly['year_month'],
            y=yearly_monthly['count'],
            name='Count',
            marker_color=chart_colors[1]
        ),
        row=2, col=1
    )
    
    # Average
    fig.add_trace(
        go.Scatter(
            x=yearly_monthly['year_month'],
            y=yearly_monthly['average'],
            mode='lines+markers',
            name='Average',
            line=dict(color=chart_colors[3], width=2),
            marker=dict(size=6)
        ),
        row=3, col=1
    )
    
    fig.update_xaxes(title_text="Year-Month", row=3, col=1, tickangle=-45)
    fig.update_yaxes(title_text="Amount (AED)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="Avg (AED)", row=3, col=1)
    
    fig.update_layout(
        title_text="Year-Month Analysis: Amount, Count, and Average",
        template=get_plot_template(dark_mode),
        height=900,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=100)
    )
    
    return fig

def create_yearly_summary(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create yearly summary with multiple metrics."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    yearly = df.groupby('year').agg({
        'amount': ['sum', 'mean', 'median'],
        'id': 'count'
    }).reset_index()
    
    yearly.columns = ['year', 'total', 'average', 'median', 'count']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Total Amount by Year', 'Number of Donations', 'Average Donation', 'Median Donation'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=yearly['year'],
            y=yearly['total'],
            marker_color=chart_colors[0],
            text=yearly['total'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=yearly['year'],
            y=yearly['count'],
            marker_color=chart_colors[1],
            text=yearly['count'].apply(lambda x: f'{x:,}'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Bar(
            x=yearly['year'],
            y=yearly['average'],
            marker_color=chart_colors[2],
            text=yearly['average'].apply(lambda x: f'{x:.2f}'),
            textposition='outside'
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=yearly['year'],
            y=yearly['median'],
            marker_color=chart_colors[3],
            text=yearly['median'].apply(lambda x: f'{x:.2f}'),
            textposition='outside'
        ),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_xaxes(title_text="Year", row=2, col=2)
    
    fig.update_yaxes(title_text="Amount (AED)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    fig.update_yaxes(title_text="Avg (AED)", row=2, col=1)
    fig.update_yaxes(title_text="Median (AED)", row=2, col=2)
    
    fig.update_layout(
        title_text="Yearly Summary Analysis",
        template=get_plot_template(dark_mode),
        height=600,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_donor_behavior_analysis(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Analyze donor behavior patterns."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Group by donor
    donor_stats = df.groupby('id').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    donor_stats.columns = ['donor_id', 'total_donated', 'avg_donation', 'donation_count']
    
    # Categorize donors
    donor_stats['category'] = pd.cut(
        donor_stats['donation_count'],
        bins=[0, 1, 5, 10, float('inf')],
        labels=['One-time', 'Occasional (2-5)', 'Regular (6-10)', 'Frequent (10+)']
    )
    
    category_summary = donor_stats.groupby('category').agg({
        'donor_id': 'count',
        'total_donated': 'sum',
        'avg_donation': 'mean'
    }).reset_index()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Donor Categories', 'Total Amount by Category'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Pie(
            labels=category_summary['category'],
            values=category_summary['donor_id'],
            marker=dict(colors=chart_colors),
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>Donors: %{value}<br>Percentage: %{percent}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=category_summary['category'],
            y=category_summary['total_donated'],
            marker_color=chart_colors,
            text=category_summary['total_donated'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Donor Category", row=1, col=2)
    fig.update_yaxes(title_text="Total Amount (AED)", row=1, col=2)
    
    fig.update_layout(
        title_text="Donor Behavior Analysis",
        template=get_plot_template(dark_mode),
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_top_donors_chart(df: pd.DataFrame, dark_mode: bool = False, top_n: int = 10) -> go.Figure:
    """Show top donors by total amount."""
    colors = get_theme_colors(dark_mode)
    
    top_donors = df.groupby('id').agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    top_donors.columns = ['donor_id', 'total_amount', 'donation_count']
    top_donors = top_donors.nlargest(top_n, 'total_amount')
    top_donors = top_donors.sort_values('total_amount', ascending=True)
    
    # Anonymize donor IDs
    top_donors['donor_label'] = ['Donor ' + str(i) for i in range(1, len(top_donors) + 1)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_donors['donor_label'],
        x=top_donors['total_amount'],
        orientation='h',
        marker=dict(
            color=top_donors['total_amount'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Amount (AED)")
        ),
        text=top_donors['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Total: AED %{x:,.0f}<br>Donations: %{customdata}<extra></extra>',
        customdata=top_donors['donation_count']
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Donors by Total Amount",
        xaxis_title="Total Amount (AED)",
        yaxis_title="",
        template=get_plot_template(dark_mode),
        height=500,
        margin=dict(l=100, r=50, t=60, b=50)
    )
    
    return fig

def create_amount_range_distribution(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create distribution by amount ranges."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Create amount ranges
    df_copy = df.copy()
    df_copy['amount_range'] = pd.cut(
        df_copy['amount'],
        bins=[0, 20, 50, 100, 200, 500, 1000, float('inf')],
        labels=['0-20', '21-50', '51-100', '101-200', '201-500', '501-1000', '1000+']
    )
    
    range_summary = df_copy.groupby('amount_range', observed=False).agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    range_summary.columns = ['range', 'total_amount', 'count']
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Count by Amount Range', 'Total Amount by Range'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=range_summary['range'],
            y=range_summary['count'],
            marker_color=chart_colors[1],
            text=range_summary['count'].apply(lambda x: f'{x:,}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=range_summary['range'],
            y=range_summary['total_amount'],
            marker_color=chart_colors[0],
            text=range_summary['total_amount'].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(title_text="Amount Range (AED)", row=1, col=1)
    fig.update_xaxes(title_text="Amount Range (AED)", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Total Amount (AED)", row=1, col=2)
    
    fig.update_layout(
        title_text="Donation Amount Range Analysis",
        template=get_plot_template(dark_mode),
        height=400,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_growth_trend_analysis(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create cumulative growth and trend analysis."""
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Daily cumulative
    daily_data = df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index().sort_values('date')
    
    daily_data['cumulative_amount'] = daily_data['amount'].cumsum()
    daily_data['cumulative_count'] = daily_data['id'].cumsum()
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cumulative Amount Over Time', 'Cumulative Donation Count'),
        vertical_spacing=0.12
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['cumulative_amount'],
            mode='lines',
            name='Cumulative Amount',
            line=dict(color=chart_colors[0], width=2),
            fill='tozeroy',
            fillcolor=f"rgba{tuple(list(int(chart_colors[0].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_data['date'],
            y=daily_data['cumulative_count'],
            mode='lines',
            name='Cumulative Count',
            line=dict(color=chart_colors[1], width=2),
            fill='tozeroy',
            fillcolor=f"rgba{tuple(list(int(chart_colors[1].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.2])}"
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Cumulative Amount (AED)", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative Count", row=2, col=1)
    
    fig.update_layout(
        title_text="Cumulative Growth Analysis",
        template=get_plot_template(dark_mode),
        height=600,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_quarterly_comparison(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """Create quarterly comparison chart."""
    chart_colors = get_chart_colors(dark_mode)
    
    quarterly_data = df.groupby(['year', 'quarter']).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    quarterly_data['period'] = quarterly_data['year'].astype(str) + ' Q' + quarterly_data['quarter'].astype(str)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=quarterly_data['period'],
        y=quarterly_data['amount'],
        marker_color=chart_colors,
        text=quarterly_data['amount'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
    ))
    
    fig.update_layout(
        title="Quarterly Donation Totals",
        xaxis_title="Quarter",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(dark_mode),
        height=400,
        margin=dict(l=50, r=50, t=60, b=50)
    )
    
    return fig

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def create_kpi_card(title: str, value: str, icon: str, color: str = 'primary', 
                    trend: str = None, trend_value: str = None, dark_mode: bool = False) -> dbc.Card:
    """Create a KPI card component."""
    colors = get_theme_colors(dark_mode)
    
    card_content = [
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-2x", style={'color': colors[color]}),
            ], style={'text-align': 'center', 'margin-bottom': '10px'}),
            html.H6(title, className="text-center mb-2", 
                   style={'font-size': '0.9rem', 'color': colors['text_secondary']}),
            html.H3(value, className="text-center mb-0", 
                   style={'font-weight': 'bold', 'color': colors[color]}),
        ])
    ]
    
    if trend and trend_value:
        trend_color = colors['success'] if trend == 'up' else colors['danger']
        trend_icon = 'fa-arrow-up' if trend == 'up' else 'fa-arrow-down'
        
        card_content[0].children.append(
            html.Div([
                html.I(className=f"fas {trend_icon}", style={'color': trend_color, 'font-size': '0.8rem'}),
                html.Span(f" {trend_value}", style={'color': trend_color, 'font-size': '0.8rem', 'margin-left': '5px'})
            ], className="text-center mt-2")
        )
    
    card_style = {
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'box-shadow': f"0 2px 8px {colors['shadow']}",
        'color': colors['text']
    }
    
    return dbc.Card(card_content, className="h-100", style=card_style)

def create_filter_section(dark_mode: bool = False) -> dbc.Card:
    """Create filter section for the dashboard."""
    colors = get_theme_colors(dark_mode)
    
    card_style = {
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'box-shadow': f"0 2px 8px {colors['shadow']}",
        'color': colors['text'],
        'position': 'sticky',
        'top': '20px',
        'z-index': '100'
    }
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="mb-3", style={'color': colors['text']}),
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range", className="fw-bold mb-2", style={'color': colors['text']}),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        display_format='YYYY-MM-DD',
                        style={'width': '100%'}
                    ),
                ], md=12),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Donation Type", className="fw-bold mb-2 mt-3", style={'color': colors['text']}),
                    dcc.Dropdown(
                        id='donation-type-filter',
                        options=[],
                        multi=True,
                        placeholder="All Types",
                    ),
                ], md=12),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Amount Range (AED)", className="fw-bold mb-2 mt-3", style={'color': colors['text']}),
                    dcc.RangeSlider(
                        id='amount-range',
                        min=0,
                        max=1000,
                        step=10,
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ], md=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Checklist(
                        options=[{"label": " Ramadan Only", "value": "ramadan"}],
                        value=[],
                        id="ramadan-filter",
                        className="mt-3",
                        style={'color': colors['text']}
                    ),
                ], md=12),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Apply Filters", id="apply-filters", color="primary", className="mt-3 w-100"),
                    dbc.Button("Reset Filters", id="reset-filters", color="secondary", className="mt-2 w-100", outline=True),
                ], md=12),
            ]),
        ])
    ], className="mb-4", style=card_style)

def create_navbar(dark_mode: bool = False) -> dbc.Navbar:
    """Create navigation bar."""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                APP_TITLE
            ], className="ms-2", style={'font-size': '1.5rem', 'font-weight': 'bold'}),
            dbc.Nav([
                dbc.NavItem(
                    dbc.Button([
                        html.I(className="fas fa-moon" if not dark_mode else "fas fa-sun", id="theme-icon"),
                    ], id="theme-toggle", color="light", outline=True, className="me-2")
                ),
                dbc.NavItem(dbc.Button([
                    html.I(className="fas fa-sync-alt me-1"),
                    "Refresh"
                ], id="refresh-button", color="light", outline=True)),
            ], navbar=True),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4",
        style={'box-shadow': '0 2px 4px rgba(0,0,0,.2)'}
    )

# ============================================================================
# INITIALIZE APP
# ============================================================================

df = load_and_process_data(DATA_PATH)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title=APP_TITLE
)

server = app.server

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Store(id='dark-mode-store', data=False),
    dcc.Store(id='filtered-data-store'),
    dcc.Store(id='comparison-period-1', data=None),
    dcc.Store(id='comparison-period-2', data=None),
    
    html.Div([
        create_navbar(),
        
        dbc.Container([
            # Tabs for different pages
            dbc.Tabs([
                dbc.Tab(label="📊 Dashboard", tab_id="dashboard"),
                dbc.Tab(label="🔄 Compare", tab_id="compare"),
            ], id="page-tabs", active_tab="dashboard", className="mb-4"),
            
            html.Div(id='page-content')
            
        ], fluid=True, id='main-container'),
    ], id='app-container')
])

# Dashboard page layout
def create_dashboard_layout():
    return html.Div([
        # KPI Cards Row
        html.Div(id='kpi-cards', className="mb-4"),
        
        # Main Content
        dbc.Row([
            # Filters Column
            dbc.Col([
                html.Div(id='filter-section')
            ], md=3),
                
                # Charts Column
                dbc.Col([
                    # Time Series Chart
                    html.Div(id='time-series-card', className="mb-4"),
                    
                    # Ramadan Analysis Row
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='ramadan-comparison-card', className="mb-4"),
                        ], md=12),
                    ]),
                    
                    # Islamic Events and Hijri Months
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='islamic-events-card', className="mb-4"),
                        ], md=6),
                        dbc.Col([
                            html.Div(id='hijri-months-card', className="mb-4"),
                        ], md=6),
                    ]),
                    
                    # Yearly and Monthly Analysis
                    html.H4("📊 Temporal Analysis", className="mt-4 mb-3", id='temporal-header'),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='yearly-summary-card', className="mb-4"),
                        ], md=12),
                    ]),
                    
                    html.Div(id='yearly-monthly-card', className="mb-4"),
                    
                    # Heatmaps Section
                    html.H4("🔥 Heatmap Analysis", className="mt-4 mb-3", id='heatmap-header'),
                    
                    html.Div(id='time-weekday-heatmap-card', className="mb-4"),
                    html.Div(id='heatmap-card', className="mb-4"),
                    
                    # Category and Distribution
                    html.H4("📈 Category & Distribution Analysis", className="mt-4 mb-3", id='category-header'),
                    
                    html.Div(id='category-card', className="mb-4"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='distribution-card', className="mb-4"),
                        ], md=6),
                        dbc.Col([
                            html.Div(id='amount-range-card', className="mb-4"),
                        ], md=6),
                    ]),
                    
                    # Growth and Trends
                    html.H4("📈 Growth & Trend Analysis", className="mt-4 mb-3", id='growth-header'),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='growth-trend-card', className="mb-4"),
                        ], md=6),
                        dbc.Col([
                            html.Div(id='quarterly-card', className="mb-4"),
                        ], md=6),
                    ]),
                    
                    # Hourly Pattern
                    html.Div(id='hourly-card', className="mb-4"),
                    
                ], md=9),
            ]),
            
            # Footer
            html.Footer([
                html.Hr(),
                html.P([
                    "UAE Donations Analytics Dashboard | ",
                    html.I(className="fas fa-database me-1"),
                    html.Span(id='record-count'),
                    " | Last Updated: ",
                    html.Span(id='last-updated')
                ], className="text-center", id='footer-text')
            ], className="mt-4 mb-3")
        ])

# Comparison page layout
def create_comparison_layout():
    return html.Div([
        html.H3("🔄 Compare Periods", className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Period 1"),
                    dbc.CardBody([
                        html.Label("Select Date Range", className="fw-bold mb-2"),
                        dcc.DatePickerRange(
                            id='compare-date-range-1',
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'}
                        ),
                        html.Label("Donation Type", className="fw-bold mb-2 mt-3"),
                        dcc.Dropdown(
                            id='compare-donation-type-1',
                            options=[],
                            multi=True,
                            placeholder="All Types",
                        ),
                    ])
                ], className="mb-3")
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Period 2"),
                    dbc.CardBody([
                        html.Label("Select Date Range", className="fw-bold mb-2"),
                        dcc.DatePickerRange(
                            id='compare-date-range-2',
                            display_format='YYYY-MM-DD',
                            style={'width': '100%'}
                        ),
                        html.Label("Donation Type", className="fw-bold mb-2 mt-3"),
                        dcc.Dropdown(
                            id='compare-donation-type-2',
                            options=[],
                            multi=True,
                            placeholder="All Types",
                        ),
                    ])
                ], className="mb-3")
            ], md=6),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Button("Compare", id="compare-button", color="primary", className="w-100 mb-4"),
            ], md=12),
        ]),
        
        # Comparison Results
        html.Div(id='comparison-results')
    ])

# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('page-tabs', 'active_tab')
)
def render_page_content(active_tab):
    """Render page content based on active tab."""
    if active_tab == "compare":
        return create_comparison_layout()
    else:
        return create_dashboard_layout()

@callback(
    [Output('dark-mode-store', 'data'),
     Output('theme-icon', 'className')],
    Input('theme-toggle', 'n_clicks'),
    State('dark-mode-store', 'data'),
    prevent_initial_call=True
)
def toggle_theme(n_clicks, current_mode):
    """Toggle between light and dark mode."""
    new_mode = not current_mode
    icon_class = "fas fa-sun" if new_mode else "fas fa-moon"
    return new_mode, icon_class

@callback(
    Output('app-container', 'style'),
    Input('dark-mode-store', 'data')
)
def update_app_background(dark_mode):
    """Update app background based on theme."""
    colors = get_theme_colors(dark_mode)
    return {
        'background-color': colors['background'],
        'min-height': '100vh',
        'transition': 'background-color 0.3s ease'
    }

@callback(
    Output('main-container', 'style'),
    Input('dark-mode-store', 'data')
)
def update_container_style(dark_mode):
    """Update container style based on theme."""
    colors = get_theme_colors(dark_mode)
    return {
        'background-color': colors['background'],
        'color': colors['text'],
        'padding': '20px'
    }

@callback(
    [Output('footer-text', 'style'),
     Output('temporal-header', 'style'),
     Output('heatmap-header', 'style'),
     Output('category-header', 'style'),
     Output('growth-header', 'style')],
    Input('dark-mode-store', 'data')
)
def update_text_styles(dark_mode):
    """Update text styles based on theme."""
    colors = get_theme_colors(dark_mode)
    header_style = {'color': colors['text']}
    footer_style = {'color': colors['text_secondary']}
    return footer_style, header_style, header_style, header_style, header_style

@callback(
    [Output('date-range', 'start_date'),
     Output('date-range', 'end_date'),
     Output('donation-type-filter', 'options'),
     Output('donation-type-filter', 'value'),
     Output('amount-range', 'min'),
     Output('amount-range', 'max'),
     Output('amount-range', 'value'),
     Output('ramadan-filter', 'value')],
    Input('reset-filters', 'n_clicks'),
    prevent_initial_call=False
)
def initialize_filters(n_clicks):
    """Initialize filter values."""
    try:
        start_date = df['donationdate'].min().date()
        end_date = df['donationdate'].max().date()
        
        # Use English translations if available
        if 'donationtype_en' in df.columns and df['donationtype_en'].notna().any():
            unique_types = df['donationtype_en'].dropna().unique()
            donation_types = [{'label': str(dt), 'value': str(dt)} for dt in sorted(unique_types)]
        else:
            unique_types = df['donationtype'].dropna().unique()
            donation_types = [{'label': str(dt), 'value': str(dt)} for dt in sorted(unique_types)]
        
        amount_min = float(df['amount'].min())
        amount_max = float(df['amount'].max())
        
        return start_date, end_date, donation_types, None, amount_min, amount_max, [amount_min, amount_max], []
    except Exception as e:
        print(f"Error initializing filters: {e}")
        import datetime
        today = datetime.date.today()
        return today, today, [], None, 0, 1000, [0, 1000], []

@callback(
    Output('filtered-data-store', 'data'),
    [Input('apply-filters', 'n_clicks'),
     Input('reset-filters', 'n_clicks')],
    [State('date-range', 'start_date'),
     State('date-range', 'end_date'),
     State('donation-type-filter', 'value'),
     State('amount-range', 'value'),
     State('ramadan-filter', 'value')],
    prevent_initial_call=False
)
def filter_data(apply_clicks, reset_clicks, start_date, end_date, donation_types, amount_range, ramadan_filter):
    """Filter data based on user selections."""
    from dash import ctx
    
    # Check which button was clicked
    if ctx.triggered_id == 'reset-filters':
        # Return full dataset on reset
        return df.to_json(date_format='iso', orient='split')
    
    filtered_df = df.copy()
    
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['donationdate'] >= start_date) & 
            (filtered_df['donationdate'] <= end_date)
        ]
    
    if donation_types:
        # Filter by English translations if available
        if 'donationtype_en' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['donationtype_en'].isin(donation_types)]
        else:
            filtered_df = filtered_df[filtered_df['donationtype'].isin(donation_types)]
    
    if amount_range:
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) & 
            (filtered_df['amount'] <= amount_range[1])
        ]
    
    if ramadan_filter and 'ramadan' in ramadan_filter:
        filtered_df = filtered_df[filtered_df['is_ramadan'] == True]
    
    return filtered_df.to_json(date_format='iso', orient='split')

@callback(
    Output('filter-section', 'children'),
    Input('dark-mode-store', 'data')
)
def update_filter_section(dark_mode):
    """Update filter section based on theme."""
    return create_filter_section(dark_mode)

@callback(
    Output('kpi-cards', 'children'),
    [Input('filtered-data-store', 'data'),
     Input('dark-mode-store', 'data')]
)
def update_kpi_cards(filtered_data, dark_mode):
    """Update KPI cards with filtered data."""
    if filtered_data is None:
        filtered_df = df
    else:
        filtered_df = pd.read_json(StringIO(filtered_data), orient='split')
        filtered_df['donationdate'] = pd.to_datetime(filtered_df['donationdate'])
    
    kpis = calculate_kpis(filtered_df)
    growth_rate = calculate_growth_rate(filtered_df, 'month')
    trend = 'up' if growth_rate > 0 else 'down'
    
    return dbc.Row([
        dbc.Col([
            create_kpi_card(
                "Total Donations",
                f"{kpis['total_donations']:,}",
                "fa-hand-holding-heart",
                "primary",
                dark_mode=dark_mode
            )
        ], lg=2, md=4, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Total Amount",
                f"AED {kpis['total_amount']:,.0f}",
                "fa-coins",
                "success",
                trend,
                f"{abs(growth_rate):.1f}%",
                dark_mode
            )
        ], lg=2, md=4, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Average Donation",
                f"AED {kpis['avg_donation']:,.2f}",
                "fa-chart-line",
                "info",
                dark_mode=dark_mode
            )
        ], lg=2, md=4, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Ramadan Donations",
                f"{kpis['ramadan_donations']:,} ({kpis['ramadan_percentage']:.1f}%)",
                "fa-moon",
                "warning",
                dark_mode=dark_mode
            )
        ], lg=3, md=6, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Ramadan Amount",
                f"AED {kpis['ramadan_amount']:,.0f}",
                "fa-star-and-crescent",
                "danger",
                dark_mode=dark_mode
            )
        ], lg=3, md=6, sm=6, className="mb-3"),
    ])

def create_chart_card(chart_fig, dark_mode):
    """Helper to create a styled card for charts."""
    colors = get_theme_colors(dark_mode)
    card_style = {
        'background-color': colors['card_bg'],
        'border': f"1px solid {colors['border']}",
        'box-shadow': f"0 2px 8px {colors['shadow']}",
    }
    return dbc.Card([
        dbc.CardBody([
            dcc.Graph(figure=chart_fig, config={'displayModeBar': False})
        ])
    ], style=card_style)

@callback(
    [Output('time-series-card', 'children'),
     Output('ramadan-comparison-card', 'children'),
     Output('islamic-events-card', 'children'),
     Output('hijri-months-card', 'children'),
     Output('yearly-summary-card', 'children'),
     Output('yearly-monthly-card', 'children'),
     Output('time-weekday-heatmap-card', 'children'),
     Output('heatmap-card', 'children'),
     Output('category-card', 'children'),
     Output('distribution-card', 'children'),
     Output('amount-range-card', 'children'),
     Output('growth-trend-card', 'children'),
     Output('quarterly-card', 'children'),
     Output('hourly-card', 'children')],
    [Input('filtered-data-store', 'data'),
     Input('dark-mode-store', 'data')]
)
def update_charts(filtered_data, dark_mode):
    """Update all charts with filtered data."""
    if filtered_data is None:
        filtered_df = df
    else:
        filtered_df = pd.read_json(StringIO(filtered_data), orient='split')
        filtered_df['donationdate'] = pd.to_datetime(filtered_df['donationdate'])
        filtered_df['date'] = filtered_df['donationdate'].dt.date
    
    return (
        create_chart_card(create_time_series_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_ramadan_comparison_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_islamic_events_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_hijri_months_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_yearly_summary(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_yearly_monthly_analysis(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_time_weekday_heatmap(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_monthly_heatmap(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_category_distribution(filtered_df, 10, dark_mode), dark_mode),
        create_chart_card(create_distribution_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_amount_range_distribution(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_growth_trend_analysis(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_quarterly_comparison(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_hourly_pattern(filtered_df, dark_mode), dark_mode)
    )

@callback(
    [Output('record-count', 'children'),
     Output('last-updated', 'children')],
    Input('filtered-data-store', 'data')
)
def update_footer(filtered_data):
    """Update footer information."""
    if filtered_data is None:
        record_count = len(df)
    else:
        filtered_df = pd.read_json(StringIO(filtered_data), orient='split')
        record_count = len(filtered_df)
    
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"{record_count:,} records", last_updated

# ============================================================================
# COMPARISON PAGE CALLBACKS
# ============================================================================

@callback(
    [Output('compare-date-range-1', 'start_date'),
     Output('compare-date-range-1', 'end_date'),
     Output('compare-date-range-2', 'start_date'),
     Output('compare-date-range-2', 'end_date'),
     Output('compare-donation-type-1', 'options'),
     Output('compare-donation-type-2', 'options')],
    Input('page-tabs', 'active_tab')
)
def initialize_comparison_filters(active_tab):
    """Initialize comparison filters."""
    if active_tab != "compare":
        return None, None, None, None, [], []
    
    # Get date range
    start_date = df['donationdate'].min().date()
    end_date = df['donationdate'].max().date()
    mid_date = start_date + (end_date - start_date) / 2
    
    # Use English translations if available
    if 'donationtype_en' in df.columns:
        donation_types = [{'label': dt, 'value': dt} for dt in sorted(df['donationtype_en'].unique()) if pd.notna(dt)]
    else:
        donation_types = [{'label': dt, 'value': dt} for dt in sorted(df['donationtype'].unique())]
    
    return start_date, mid_date, mid_date, end_date, donation_types, donation_types

@callback(
    Output('comparison-results', 'children'),
    Input('compare-button', 'n_clicks'),
    [State('compare-date-range-1', 'start_date'),
     State('compare-date-range-1', 'end_date'),
     State('compare-donation-type-1', 'value'),
     State('compare-date-range-2', 'start_date'),
     State('compare-date-range-2', 'end_date'),
     State('compare-donation-type-2', 'value'),
     State('dark-mode-store', 'data')],
    prevent_initial_call=True
)
def compare_periods(n_clicks, start1, end1, types1, start2, end2, types2, dark_mode):
    """Compare two time periods."""
    if not all([start1, end1, start2, end2]):
        return html.Div("Please select date ranges for both periods.", className="alert alert-warning")
    
    # Filter data for period 1
    df1 = df[(df['donationdate'] >= start1) & (df['donationdate'] <= end1)].copy()
    if types1:
        col = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
        df1 = df1[df1[col].isin(types1)]
    
    # Filter data for period 2
    df2 = df[(df['donationdate'] >= start2) & (df['donationdate'] <= end2)].copy()
    if types2:
        col = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
        df2 = df2[df2[col].isin(types2)]
    
    # Calculate metrics
    kpis1 = calculate_kpis(df1)
    kpis2 = calculate_kpis(df2)
    
    colors = get_theme_colors(dark_mode)
    chart_colors = get_chart_colors(dark_mode)
    
    # Create comparison visualization
    metrics = ['total_donations', 'total_amount', 'avg_donation', 'ramadan_donations', 'ramadan_amount']
    metric_labels = ['Total Donations', 'Total Amount (AED)', 'Avg Donation (AED)', 'Ramadan Donations', 'Ramadan Amount (AED)']
    
    period1_values = [kpis1[m] for m in metrics]
    period2_values = [kpis2[m] for m in metrics]
    
    fig = go.Figure(data=[
        go.Bar(name=f'Period 1 ({start1} to {end1})', x=metric_labels, y=period1_values, marker_color=chart_colors[0]),
        go.Bar(name=f'Period 2 ({start2} to {end2})', x=metric_labels, y=period2_values, marker_color=chart_colors[1])
    ])
    
    fig.update_layout(
        title='Period Comparison',
        barmode='group',
        template=get_plot_template(dark_mode),
        height=500,
        xaxis_tickangle=-45
    )
    
    # Calculate percentage changes
    changes = []
    for i, metric in enumerate(metrics):
        val1 = kpis1[metric]
        val2 = kpis2[metric]
        if val1 > 0:
            change = ((val2 - val1) / val1) * 100
            changes.append({
                'metric': metric_labels[i],
                'period1': f"{val1:,.2f}" if metric in ['avg_donation'] else f"{val1:,.0f}",
                'period2': f"{val2:,.2f}" if metric in ['avg_donation'] else f"{val2:,.0f}",
                'change': f"{change:+.1f}%",
                'color': colors['success'] if change > 0 else colors['danger']
            })
    
    # Create comparison table
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Metric"),
                html.Th("Period 1"),
                html.Th("Period 2"),
                html.Th("Change"),
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td(change['metric']),
                html.Td(change['period1']),
                html.Td(change['period2']),
                html.Td(change['change'], style={'color': change['color'], 'font-weight': 'bold'}),
            ]) for change in changes
        ])
    ], bordered=True, hover=True, responsive=True, className="mb-4")
    
    return html.Div([
        create_chart_card(fig, dark_mode),
        html.H4("Detailed Comparison", className="mt-4 mb-3"),
        table,
        dbc.Row([
            dbc.Col([
                create_chart_card(create_category_distribution(df1, 10, dark_mode), dark_mode),
            ], md=6),
            dbc.Col([
                create_chart_card(create_category_distribution(df2, 10, dark_mode), dark_mode),
            ], md=6),
        ]),
    ])

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
