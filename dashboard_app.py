"""
UAE Donations Analytics Dashboard
A comprehensive dashboard for analyzing donation data with interactive visualizations.
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

# ============================================================================
# CONFIGURATION
# ============================================================================

DATA_PATH = Path('data/General_Donation.csv')
APP_TITLE = "UAE Donations Analytics Dashboard"
PORT = 8050

# Color schemes
COLORS = {
    'primary': '#0d6efd',
    'secondary': '#6c757d',
    'success': '#198754',
    'info': '#0dcaf0',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'light': '#f8f9fa',
    'dark': '#212529',
    'card_bg': '#ffffff',
    'border': '#dee2e6',
}

# Chart color palette
CHART_COLORS = ['#0d6efd', '#198754', '#ffc107', '#dc3545', '#0dcaf0', '#6610f2', '#d63384', '#fd7e14']

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_and_process_data(file_path: Path) -> pd.DataFrame:
    """
    Load and process donation data with proper error handling.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Processed DataFrame with additional time dimensions
    """
    try:
        df = pd.read_csv(file_path)
        
        # Convert and validate data types
        df['donationdate'] = pd.to_datetime(df['donationdate'], errors='coerce')
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # Remove rows with invalid data
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
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

# ============================================================================
# METRICS CALCULATION
# ============================================================================

def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate key performance indicators."""
    return {
        'total_donations': len(df),
        'total_amount': df['amount'].sum(),
        'avg_donation': df['amount'].mean(),
        'unique_donors': df['id'].nunique(),
        'unique_types': df['donationtype'].nunique(),
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

def create_time_series_chart(df: pd.DataFrame, metric: str = 'amount') -> go.Figure:
    """Create time series chart for donations over time."""
    daily_data = df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = go.Figure()
    
    if metric == 'amount':
        fig.add_trace(go.Scatter(
            x=daily_data['date'],
            y=daily_data['amount'],
            mode='lines',
            name='Daily Amount',
            line=dict(color=COLORS['primary'], width=2),
            fill='tozeroy',
            fillcolor='rgba(13, 110, 253, 0.1)'
        ))
        fig.update_yaxes(title_text="Amount (AED)")
    else:
        fig.add_trace(go.Scatter(
            x=daily_data['date'],
            y=daily_data['id'],
            mode='lines',
            name='Daily Count',
            line=dict(color=COLORS['success'], width=2),
            fill='tozeroy',
            fillcolor='rgba(25, 135, 84, 0.1)'
        ))
        fig.update_yaxes(title_text="Number of Donations")
    
    fig.update_layout(
        title="Donation Trends Over Time",
        xaxis_title="Date",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def create_category_distribution(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Create horizontal bar chart for donation types."""
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
            colorscale='Blues',
            showscale=False
        ),
        text=category_data['amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Donation Categories by Amount",
        xaxis_title="Total Amount (AED)",
        yaxis_title="",
        template='plotly_white',
        height=500,
        margin=dict(l=200, r=50, t=50, b=50)
    )
    
    return fig

def create_monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create heatmap showing donation patterns by month and weekday."""
    heatmap_data = df.groupby(['month_name', 'weekday'])['amount'].sum().reset_index()
    
    # Create pivot table
    pivot = heatmap_data.pivot(index='weekday', columns='month_name', values='amount')
    
    # Reorder weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = pivot.reindex([day for day in weekday_order if day in pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale='YlOrRd',
        text=pivot.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Amount (AED)")
    ))
    
    fig.update_layout(
        title="Donation Heatmap: Day of Week vs Month",
        xaxis_title="Month",
        yaxis_title="Day of Week",
        template='plotly_white',
        height=400,
        margin=dict(l=100, r=50, t=50, b=50)
    )
    
    return fig

def create_hourly_pattern(df: pd.DataFrame) -> go.Figure:
    """Create chart showing donation patterns by hour of day."""
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
            marker_color=COLORS['primary'],
            name='Amount'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=hourly_data['hour'],
            y=hourly_data['id'],
            marker_color=COLORS['success'],
            name='Count'
        ),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
    fig.update_yaxes(title_text="Amount (AED)", row=1, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    
    fig.update_layout(
        title_text="Donation Patterns by Hour of Day",
        template='plotly_white',
        height=600,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create histogram showing donation amount distribution."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['amount'],
        nbinsx=50,
        marker_color=COLORS['primary'],
        opacity=0.7,
        name='Distribution'
    ))
    
    fig.update_layout(
        title="Distribution of Donation Amounts",
        xaxis_title="Amount (AED)",
        yaxis_title="Frequency",
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

def create_quarterly_comparison(df: pd.DataFrame) -> go.Figure:
    """Create quarterly comparison chart."""
    quarterly_data = df.groupby(['year', 'quarter']).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    quarterly_data['period'] = quarterly_data['year'].astype(str) + ' Q' + quarterly_data['quarter'].astype(str)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=quarterly_data['period'],
        y=quarterly_data['amount'],
        marker_color=CHART_COLORS,
        text=quarterly_data['amount'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside',
    ))
    
    fig.update_layout(
        title="Quarterly Donation Totals",
        xaxis_title="Quarter",
        yaxis_title="Total Amount (AED)",
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return fig

# ============================================================================
# DASHBOARD COMPONENTS
# ============================================================================

def create_kpi_card(title: str, value: str, icon: str, color: str = 'primary', 
                    trend: str = None, trend_value: str = None) -> dbc.Card:
    """Create a KPI card component."""
    card_content = [
        dbc.CardBody([
            html.Div([
                html.I(className=f"fas {icon} fa-2x", style={'color': COLORS[color]}),
            ], style={'text-align': 'center', 'margin-bottom': '10px'}),
            html.H6(title, className="text-muted text-center mb-2", style={'font-size': '0.9rem'}),
            html.H3(value, className="text-center mb-0", style={'font-weight': 'bold', 'color': COLORS[color]}),
        ])
    ]
    
    if trend and trend_value:
        trend_color = COLORS['success'] if trend == 'up' else COLORS['danger']
        trend_icon = 'fa-arrow-up' if trend == 'up' else 'fa-arrow-down'
        
        card_content[0].children.append(
            html.Div([
                html.I(className=f"fas {trend_icon}", style={'color': trend_color, 'font-size': '0.8rem'}),
                html.Span(f" {trend_value}", style={'color': trend_color, 'font-size': '0.8rem', 'margin-left': '5px'})
            ], className="text-center mt-2")
        )
    
    return dbc.Card(card_content, className="shadow-sm h-100")

def create_filter_section() -> dbc.Card:
    """Create filter section for the dashboard."""
    return dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range", className="fw-bold mb-2"),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        display_format='YYYY-MM-DD',
                        style={'width': '100%'}
                    ),
                ], md=6),
                dbc.Col([
                    html.Label("Donation Type", className="fw-bold mb-2"),
                    dcc.Dropdown(
                        id='donation-type-filter',
                        options=[],
                        multi=True,
                        placeholder="All Types",
                    ),
                ], md=6),
            ]),
            dbc.Row([
                dbc.Col([
                    html.Label("Amount Range (AED)", className="fw-bold mb-2 mt-3"),
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
                    dbc.Button("Apply Filters", id="apply-filters", color="primary", className="mt-3 w-100"),
                    dbc.Button("Reset Filters", id="reset-filters", color="secondary", className="mt-2 w-100", outline=True),
                ], md=12),
            ]),
        ])
    ], className="shadow-sm mb-4")

def create_navbar() -> dbc.Navbar:
    """Create navigation bar."""
    return dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand([
                html.I(className="fas fa-chart-line me-2"),
                APP_TITLE
            ], className="ms-2", style={'font-size': '1.5rem', 'font-weight': 'bold'}),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink([
                    html.I(className="fas fa-sync-alt me-1"),
                    "Refresh"
                ], id="refresh-button", href="#")),
            ], navbar=True),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-4",
        style={'box-shadow': '0 2px 4px rgba(0,0,0,.1)'}
    )

# ============================================================================
# INITIALIZE APP
# ============================================================================

# Load data
df = load_and_process_data(DATA_PATH)

# Initialize Dash app
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

server = app.server  # For deployment

# ============================================================================
# LAYOUT
# ============================================================================

app.layout = dbc.Container([
    create_navbar(),
    
    # Store for filtered data
    dcc.Store(id='filtered-data-store'),
    
    # KPI Cards Row
    dbc.Row([
        dbc.Col([
            html.Div(id='kpi-cards')
        ], md=12)
    ], className="mb-4"),
    
    # Main Content
    dbc.Row([
        # Filters Column
        dbc.Col([
            create_filter_section(),
        ], md=3),
        
        # Charts Column
        dbc.Col([
            # Time Series Chart
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='time-series-chart', config={'displayModeBar': False})
                ])
            ], className="shadow-sm mb-4"),
            
            # Category Distribution
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='category-chart', config={'displayModeBar': False})
                ])
            ], className="shadow-sm mb-4"),
            
            # Two Column Charts
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='distribution-chart', config={'displayModeBar': False})
                        ])
                    ], className="shadow-sm mb-4"),
                ], md=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(id='quarterly-chart', config={'displayModeBar': False})
                        ])
                    ], className="shadow-sm mb-4"),
                ], md=6),
            ]),
            
            # Heatmap
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='heatmap-chart', config={'displayModeBar': False})
                ])
            ], className="shadow-sm mb-4"),
            
            # Hourly Pattern
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(id='hourly-chart', config={'displayModeBar': False})
                ])
            ], className="shadow-sm mb-4"),
            
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
        ], className="text-center text-muted")
    ], className="mt-4 mb-3")
    
], fluid=True, style={'background-color': COLORS['light'], 'min-height': '100vh', 'padding': '20px'})

# ============================================================================
# CALLBACKS
# ============================================================================

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
     State('amount-range', 'value')],
    prevent_initial_call=False
)
def filter_data(apply_clicks, reset_clicks, start_date, end_date, donation_types, amount_range):
    """Filter data based on user selections."""
    filtered_df = df.copy()
    
    # Date range filter
    if start_date and end_date:
        filtered_df = filtered_df[
            (filtered_df['donationdate'] >= start_date) & 
            (filtered_df['donationdate'] <= end_date)
        ]
    
    # Donation type filter
    if donation_types:
        filtered_df = filtered_df[filtered_df['donationtype'].isin(donation_types)]
    
    # Amount range filter
    if amount_range:
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) & 
            (filtered_df['amount'] <= amount_range[1])
        ]
    
    return filtered_df.to_json(date_format='iso', orient='split')

@callback(
    Output('kpi-cards', 'children'),
    Input('filtered-data-store', 'data')
)
def update_kpi_cards(filtered_data):
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
                "primary"
            )
        ], md=2, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Total Amount",
                f"AED {kpis['total_amount']:,.0f}",
                "fa-coins",
                "success",
                trend,
                f"{abs(growth_rate):.1f}%"
            )
        ], md=3, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Average Donation",
                f"AED {kpis['avg_donation']:,.2f}",
                "fa-chart-line",
                "info"
            )
        ], md=2, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Unique Donors",
                f"{kpis['unique_donors']:,}",
                "fa-users",
                "warning"
            )
        ], md=2, sm=6, className="mb-3"),
        dbc.Col([
            create_kpi_card(
                "Donation Types",
                f"{kpis['unique_types']:,}",
                "fa-list",
                "danger"
            )
        ], md=3, sm=6, className="mb-3"),
    ])

@callback(
    [Output('time-series-chart', 'figure'),
     Output('category-chart', 'figure'),
     Output('distribution-chart', 'figure'),
     Output('quarterly-chart', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('hourly-chart', 'figure')],
    Input('filtered-data-store', 'data')
)
def update_charts(filtered_data):
    """Update all charts with filtered data."""
    if filtered_data is None:
        filtered_df = df
    else:
        filtered_df = pd.read_json(filtered_data, orient='split')
        filtered_df['donationdate'] = pd.to_datetime(filtered_df['donationdate'])
        
        # Recreate date column
        filtered_df['date'] = filtered_df['donationdate'].dt.date
    
    return (
        create_time_series_chart(filtered_df),
        create_category_distribution(filtered_df),
        create_distribution_chart(filtered_df),
        create_quarterly_comparison(filtered_df),
        create_monthly_heatmap(filtered_df),
        create_hourly_pattern(filtered_df)
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
