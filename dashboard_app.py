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
from hijri_converter import Hijri, Gregorian

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_PATH = Path('data/General_Donation.csv')
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
# HIJRI CALENDAR FUNCTIONS
# ============================================================================

def get_hijri_date(gregorian_date):
    """Convert Gregorian date to Hijri date."""
    try:
        g = Gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
        h = g.to_hijri()
        return h
    except:
        return None

def is_ramadan(gregorian_date):
    """Check if a Gregorian date falls in Ramadan."""
    hijri = get_hijri_date(gregorian_date)
    if hijri:
        return hijri.month == 9
    return False

def get_hijri_month_name(month_num):
    """Get Hijri month name."""
    months = {
        1: 'Muharram', 2: 'Safar', 3: 'Rabi al-Awwal', 4: 'Rabi al-Thani',
        5: 'Jumada al-Awwal', 6: 'Jumada al-Thani', 7: 'Rajab', 8: 'Shaban',
        9: 'Ramadan', 10: 'Shawwal', 11: 'Dhul Qadah', 12: 'Dhul Hijjah'
    }
    return months.get(month_num, 'Unknown')

def identify_islamic_events(gregorian_date):
    """Identify Islamic events for a given date."""
    hijri = get_hijri_date(gregorian_date)
    if not hijri:
        return None
    
    if hijri.month == 9:
        if 1 <= hijri.day <= 10:
            return 'Ramadan (First 10 Days)'
        elif 11 <= hijri.day <= 20:
            return 'Ramadan (Middle 10 Days)'
        else:
            return 'Ramadan (Last 10 Days)'
    elif hijri.month == 10 and hijri.day <= 3:
        return 'Eid al-Fitr'
    elif hijri.month == 12 and 8 <= hijri.day <= 13:
        return 'Hajj & Eid al-Adha'
    elif hijri.month == 1 and hijri.day == 10:
        return 'Day of Ashura'
    elif hijri.month == 3 and hijri.day == 12:
        return 'Mawlid al-Nabi'
    
    return None

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_and_process_data(file_path: Path) -> pd.DataFrame:
    """Load and process donation data with Hijri calendar integration."""
    try:
        df = pd.read_csv(file_path)
        
        df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        df = df.dropna(subset=['donationdate', 'amount'])
        
        # Extract time dimensions
        df['year'] = df['donationdate'].dt.year
        df['month'] = df['donationdate'].dt.month
        df['month_name'] = df['donationdate'].dt.strftime('%B')
        df['quarter'] = df['donationdate'].dt.quarter
        df['day'] = df['donationdate'].dt.day
        df['weekday'] = df['donationdate'].dt.day_name()
        df['week'] = df['donationdate'].dt.isocalendar().week
        df['hour'] = df['donationdate'].dt.hour
        df['date'] = df['donationdate'].dt.date
        
        # Add Hijri calendar information
        print("Adding Hijri calendar information...")
        df['is_ramadan'] = df['donationdate'].apply(lambda x: is_ramadan(x.date()))
        df['islamic_event'] = df['donationdate'].apply(lambda x: identify_islamic_events(x.date()))
        df['hijri_month'] = df['donationdate'].apply(lambda x: get_hijri_date(x.date()).month if get_hijri_date(x.date()) else None)
        df['hijri_month_name'] = df['hijri_month'].apply(lambda x: get_hijri_month_name(x) if x else None)
        
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
    
    category_data = df.groupby('donationtype').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    category_data = category_data.nlargest(top_n, 'amount')
    category_data = category_data.sort_values('amount', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=category_data['donationtype'],
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
        textfont={"size": 9},
        colorbar=dict(title="Amount (AED)")
    ))
    
    fig.update_layout(
        title="Donation Heatmap: Day of Week vs Month",
        xaxis_title="Month",
        yaxis_title="Day of Week",
        template=get_plot_template(dark_mode),
        height=400,
        margin=dict(l=100, r=50, t=60, b=50)
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
        'color': colors['text']
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
    
    html.Div([
        create_navbar(),
        
        dbc.Container([
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
                    
                    # Category Distribution
                    html.Div(id='category-card', className="mb-4"),
                    
                    # Two Column Charts
                    dbc.Row([
                        dbc.Col([
                            html.Div(id='distribution-card', className="mb-4"),
                        ], md=6),
                        dbc.Col([
                            html.Div(id='quarterly-card', className="mb-4"),
                        ], md=6),
                    ]),
                    
                    # Heatmap
                    html.Div(id='heatmap-card', className="mb-4"),
                    
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
            
        ], fluid=True, id='main-container'),
    ], id='app-container')
])

# ============================================================================
# CALLBACKS
# ============================================================================

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
    Output('footer-text', 'style'),
    Input('dark-mode-store', 'data')
)
def update_footer_style(dark_mode):
    """Update footer style based on theme."""
    colors = get_theme_colors(dark_mode)
    return {'color': colors['text_secondary']}

@callback(
    [Output('date-range', 'start_date'),
     Output('date-range', 'end_date'),
     Output('donation-type-filter', 'options'),
     Output('amount-range', 'min'),
     Output('amount-range', 'max'),
     Output('amount-range', 'value')],
    Input('reset-filters', 'n_clicks'),
    prevent_initial_call=False
)
def initialize_filters(n_clicks):
    """Initialize filter values."""
    start_date = df['donationdate'].min().date()
    end_date = df['donationdate'].max().date()
    
    donation_types = [{'label': dt, 'value': dt} for dt in sorted(df['donationtype'].unique())]
    
    amount_min = float(df['amount'].min())
    amount_max = float(df['amount'].max())
    
    return start_date, end_date, donation_types, amount_min, amount_max, [amount_min, amount_max]

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
    filtered_df = df.copy()
    
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['donationdate'] >= start_date) & 
            (filtered_df['donationdate'] <= end_date)
        ]
    
    if donation_types:
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
        filtered_df = pd.read_json(filtered_data, orient='split')
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
     Output('category-card', 'children'),
     Output('distribution-card', 'children'),
     Output('quarterly-card', 'children'),
     Output('heatmap-card', 'children'),
     Output('hourly-card', 'children')],
    [Input('filtered-data-store', 'data'),
     Input('dark-mode-store', 'data')]
)
def update_charts(filtered_data, dark_mode):
    """Update all charts with filtered data."""
    if filtered_data is None:
        filtered_df = df
    else:
        filtered_df = pd.read_json(filtered_data, orient='split')
        filtered_df['donationdate'] = pd.to_datetime(filtered_df['donationdate'])
        filtered_df['date'] = filtered_df['donationdate'].dt.date
    
    return (
        create_chart_card(create_time_series_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_ramadan_comparison_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_islamic_events_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_hijri_months_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_category_distribution(filtered_df, 10, dark_mode), dark_mode),
        create_chart_card(create_distribution_chart(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_quarterly_comparison(filtered_df, dark_mode), dark_mode),
        create_chart_card(create_monthly_heatmap(filtered_df, dark_mode), dark_mode),
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
        filtered_df = pd.read_json(filtered_data, orient='split')
        record_count = len(filtered_df)
    
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"{record_count:,} records", last_updated

# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
