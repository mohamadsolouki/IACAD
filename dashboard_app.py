import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

# Load and prepare data
def load_data():
    df = pd.read_csv('data/General_Donation.csv')
    df['donationdate'] = pd.to_datetime(df['donationdate'])
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
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

df = load_data()

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "UAE Donations Analytics Dashboard"

# Define color scheme
colors = {
    'background': '#f8f9fa',
    'text': '#212529',
    'primary': '#0d6efd',
    'secondary': '#6c757d',
    'success': '#198754',
    'info': '#0dcaf0',
    'warning': '#ffc107',
    'danger': '#dc3545'
}

# Get unique values for filters
donation_types = sorted(df['donationtype'].unique())
years = sorted(df['year'].unique())
months = sorted(df['month'].unique())
quarters = sorted(df['quarter'].unique())

# App Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("🎯 UAE Donations Analytics Dashboard", 
                   className="text-center mb-4 mt-4",
                   style={'color': colors['primary'], 'fontWeight': 'bold'})
        ])
    ]),
    
    # Filters Section
    dbc.Card([
        dbc.CardBody([
            html.H4("📊 Filters & Slicers", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Donation Type:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='donation-type-filter',
                        options=[{'label': 'All Types', 'value': 'all'}] + 
                               [{'label': dt, 'value': dt} for dt in donation_types],
                        value='all',
                        multi=True,
                        placeholder="Select donation type(s)"
                    )
                ], md=3),
                dbc.Col([
                    html.Label("Year:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': 'All Years', 'value': 'all'}] + 
                               [{'label': str(y), 'value': y} for y in years],
                        value='all',
                        multi=True,
                        placeholder="Select year(s)"
                    )
                ], md=2),
                dbc.Col([
                    html.Label("Quarter:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='quarter-filter',
                        options=[{'label': 'All Quarters', 'value': 'all'}] + 
                               [{'label': f'Q{q}', 'value': q} for q in quarters],
                        value='all',
                        multi=True,
                        placeholder="Select quarter(s)"
                    )
                ], md=2),
                dbc.Col([
                    html.Label("Month:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='month-filter',
                        options=[{'label': 'All Months', 'value': 'all'}] + 
                               [{'label': datetime(2000, m, 1).strftime('%B'), 'value': m} 
                                for m in months],
                        value='all',
                        multi=True,
                        placeholder="Select month(s)"
                    )
                ], md=2),
                dbc.Col([
                    html.Label("Amount Range:", style={'fontWeight': 'bold'}),
                    dcc.RangeSlider(
                        id='amount-range-filter',
                        min=df['amount'].min(),
                        max=df['amount'].quantile(0.95),
                        value=[df['amount'].min(), df['amount'].quantile(0.95)],
                        marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ], md=3),
            ])
        ])
    ], className="mb-4", style={'backgroundColor': colors['background']}),
    
    # KPI Cards
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Donations", className="text-muted"),
                    html.H3(id='total-donations', className="text-primary"),
                    html.Small(id='donations-change', className="text-success")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Amount (AED)", className="text-muted"),
                    html.H3(id='total-amount', className="text-success"),
                    html.Small(id='amount-change', className="text-success")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Average Donation", className="text-muted"),
                    html.H3(id='avg-donation', className="text-info"),
                    html.Small(id='avg-change', className="text-success")
                ])
            ], className="text-center")
        ], md=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Unique Types", className="text-muted"),
                    html.H3(id='unique-types', className="text-warning"),
                    html.Small(id='types-info', className="text-muted")
                ])
            ], className="text-center")
        ], md=3),
    ], className="mb-4"),
    
    # Main Charts Row 1
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📈 Donation Trends Over Time", className="mb-3"),
                    dcc.Graph(id='trend-chart', config={'displayModeBar': True})
                ])
            ])
        ], md=8),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🥧 Top 10 Donation Types", className="mb-3"),
                    dcc.Graph(id='donation-types-pie', config={'displayModeBar': False})
                ])
            ])
        ], md=4),
    ], className="mb-4"),
    
    # Main Charts Row 2
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📊 Donation Distribution by Type", className="mb-3"),
                    dcc.Graph(id='donation-distribution', config={'displayModeBar': True})
                ])
            ])
        ], md=12),
    ], className="mb-4"),
    
    # Main Charts Row 3
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔥 Heat Map: Donations by Hour & Day", className="mb-3"),
                    dcc.Graph(id='heatmap-chart', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📅 Seasonality Analysis", className="mb-3"),
                    dcc.Graph(id='seasonality-chart', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Main Charts Row 4
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("💰 Amount Distribution Analysis", className="mb-3"),
                    dcc.Graph(id='amount-distribution', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📆 Monthly Comparison by Year", className="mb-3"),
                    dcc.Graph(id='monthly-comparison', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Main Charts Row 5
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🎯 Cumulative Growth Analysis", className="mb-3"),
                    dcc.Graph(id='cumulative-chart', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("🔍 Top Performers Analysis", className="mb-3"),
                    dcc.Graph(id='top-performers', config={'displayModeBar': True})
                ])
            ])
        ], md=6),
    ], className="mb-4"),
    
    # Statistics Table
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📋 Statistical Summary", className="mb-3"),
                    html.Div(id='stats-table')
                ])
            ])
        ], md=12),
    ], className="mb-4"),
    
    html.Footer([
        html.Hr(),
        html.P("UAE Donations Analytics Dashboard | Data-Driven Insights", 
               className="text-center text-muted")
    ])
    
], fluid=True, style={'backgroundColor': colors['background']})

# Callback for filtering data
@callback(
    [Output('total-donations', 'children'),
     Output('total-amount', 'children'),
     Output('avg-donation', 'children'),
     Output('unique-types', 'children'),
     Output('donations-change', 'children'),
     Output('amount-change', 'children'),
     Output('avg-change', 'children'),
     Output('types-info', 'children'),
     Output('trend-chart', 'figure'),
     Output('donation-types-pie', 'figure'),
     Output('donation-distribution', 'figure'),
     Output('heatmap-chart', 'figure'),
     Output('seasonality-chart', 'figure'),
     Output('amount-distribution', 'figure'),
     Output('monthly-comparison', 'figure'),
     Output('cumulative-chart', 'figure'),
     Output('top-performers', 'figure'),
     Output('stats-table', 'children')],
    [Input('donation-type-filter', 'value'),
     Input('year-filter', 'value'),
     Input('quarter-filter', 'value'),
     Input('month-filter', 'value'),
     Input('amount-range-filter', 'value')]
)
def update_dashboard(donation_types, years, quarters, months, amount_range):
    # Filter data
    filtered_df = df.copy()
    
    # Apply filters
    if donation_types != 'all' and donation_types:
        if isinstance(donation_types, list) and 'all' not in donation_types:
            filtered_df = filtered_df[filtered_df['donationtype'].isin(donation_types)]
    
    if years != 'all' and years:
        if isinstance(years, list) and 'all' not in years:
            filtered_df = filtered_df[filtered_df['year'].isin(years)]
    
    if quarters != 'all' and quarters:
        if isinstance(quarters, list) and 'all' not in quarters:
            filtered_df = filtered_df[filtered_df['quarter'].isin(quarters)]
    
    if months != 'all' and months:
        if isinstance(months, list) and 'all' not in months:
            filtered_df = filtered_df[filtered_df['month'].isin(months)]
    
    if amount_range:
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) & 
            (filtered_df['amount'] <= amount_range[1])
        ]
    
    # Calculate KPIs
    total_donations = f"{len(filtered_df):,}"
    total_amount = f"AED {filtered_df['amount'].sum():,.2f}"
    avg_donation = f"AED {filtered_df['amount'].mean():,.2f}"
    unique_types = f"{filtered_df['donationtype'].nunique()}"
    
    # Calculate changes (comparing to overall dataset)
    donations_pct = ((len(filtered_df) / len(df)) * 100)
    amount_pct = ((filtered_df['amount'].sum() / df['amount'].sum()) * 100)
    avg_pct = ((filtered_df['amount'].mean() / df['amount'].mean() - 1) * 100)
    
    donations_change = f"📊 {donations_pct:.1f}% of total"
    amount_change = f"💵 {amount_pct:.1f}% of total"
    avg_change = f"{'📈' if avg_pct >= 0 else '📉'} {abs(avg_pct):.1f}% vs overall avg"
    types_info = f"Out of {df['donationtype'].nunique()} total types"
    
    # 1. Trend Chart - Daily aggregated donations
    daily_trend = filtered_df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    daily_trend.columns = ['date', 'total_amount', 'count']
    
    trend_fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Total Amount', 'Daily Number of Donations'),
        vertical_spacing=0.12,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
    )
    
    trend_fig.add_trace(
        go.Scatter(x=daily_trend['date'], y=daily_trend['total_amount'],
                  mode='lines', name='Amount', fill='tozeroy',
                  line=dict(color=colors['primary'], width=2)),
        row=1, col=1
    )
    
    # Add moving average
    if len(daily_trend) > 7:
        daily_trend['ma7'] = daily_trend['total_amount'].rolling(window=7).mean()
        trend_fig.add_trace(
            go.Scatter(x=daily_trend['date'], y=daily_trend['ma7'],
                      mode='lines', name='7-Day MA',
                      line=dict(color=colors['danger'], width=2, dash='dash')),
            row=1, col=1
        )
    
    trend_fig.add_trace(
        go.Scatter(x=daily_trend['date'], y=daily_trend['count'],
                  mode='lines', name='Count', fill='tozeroy',
                  line=dict(color=colors['success'], width=2)),
        row=2, col=1
    )
    
    trend_fig.update_xaxes(title_text="Date", row=2, col=1)
    trend_fig.update_yaxes(title_text="Amount (AED)", row=1, col=1)
    trend_fig.update_yaxes(title_text="Number of Donations", row=2, col=1)
    trend_fig.update_layout(height=500, showlegend=True, hovermode='x unified')
    
    # 2. Donation Types Pie Chart
    top_types = filtered_df.groupby('donationtype')['amount'].sum().nlargest(10).reset_index()
    pie_fig = px.pie(top_types, values='amount', names='donationtype',
                     title='',
                     color_discrete_sequence=px.colors.qualitative.Set3)
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    pie_fig.update_layout(height=400, showlegend=False)
    
    # 3. Donation Distribution by Type (Bar Chart)
    type_stats = filtered_df.groupby('donationtype').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    type_stats.columns = ['donationtype', 'total_amount', 'avg_amount', 'count']
    type_stats = type_stats.sort_values('total_amount', ascending=True).tail(20)
    
    dist_fig = go.Figure()
    dist_fig.add_trace(go.Bar(
        y=type_stats['donationtype'],
        x=type_stats['total_amount'],
        name='Total Amount',
        orientation='h',
        marker=dict(color=colors['primary']),
        text=type_stats['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='auto'
    ))
    
    dist_fig.update_layout(
        height=600,
        xaxis_title='Total Amount (AED)',
        yaxis_title='Donation Type',
        showlegend=False,
        hovermode='y'
    )
    
    # 4. Heatmap - Hour vs Weekday
    heatmap_data = filtered_df.groupby(['weekday', 'hour'])['amount'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='amount')
    
    # Reorder weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex([day for day in weekday_order if day in heatmap_pivot.index])
    
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='YlOrRd',
        text=heatmap_pivot.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 8},
        colorbar=dict(title="Amount (AED)")
    ))
    
    heatmap_fig.update_layout(
        height=400,
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        xaxis=dict(tickmode='linear')
    )
    
    # 5. Seasonality Analysis - Monthly patterns
    monthly_data = filtered_df.groupby(['year', 'month']).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    seasonality_fig = px.line(monthly_data, x='month', y='amount', color='year',
                             title='',
                             labels={'month': 'Month', 'amount': 'Total Amount (AED)', 'year': 'Year'},
                             markers=True)
    seasonality_fig.update_layout(height=400, hovermode='x unified')
    seasonality_fig.update_xaxes(tickmode='linear', tick0=1, dtick=1)
    
    # 6. Amount Distribution (Histogram + Box Plot)
    amount_dist_fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Distribution of Donation Amounts', 'Box Plot'),
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3]
    )
    
    amount_dist_fig.add_trace(
        go.Histogram(x=filtered_df['amount'], nbinsx=50,
                    marker=dict(color=colors['info']),
                    name='Distribution'),
        row=1, col=1
    )
    
    amount_dist_fig.add_trace(
        go.Box(x=filtered_df['amount'], name='Box Plot',
              marker=dict(color=colors['warning'])),
        row=2, col=1
    )
    
    amount_dist_fig.update_xaxes(title_text="Amount (AED)", row=2, col=1)
    amount_dist_fig.update_yaxes(title_text="Frequency", row=1, col=1)
    amount_dist_fig.update_layout(height=500, showlegend=False)
    
    # 7. Monthly Comparison by Year
    monthly_comparison = filtered_df.groupby(['year', 'month_name', 'month']).agg({
        'amount': 'sum'
    }).reset_index()
    monthly_comparison = monthly_comparison.sort_values('month')
    
    monthly_comp_fig = px.bar(monthly_comparison, x='month_name', y='amount', color='year',
                             barmode='group',
                             title='',
                             labels={'month_name': 'Month', 'amount': 'Total Amount (AED)'})
    monthly_comp_fig.update_layout(height=400, hovermode='x unified')
    
    # 8. Cumulative Growth
    cumulative_data = filtered_df.sort_values('donationdate').copy()
    cumulative_data['cumulative_amount'] = cumulative_data['amount'].cumsum()
    cumulative_data['cumulative_count'] = range(1, len(cumulative_data) + 1)
    
    cumulative_fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    cumulative_fig.add_trace(
        go.Scatter(x=cumulative_data['donationdate'], 
                  y=cumulative_data['cumulative_amount'],
                  mode='lines', name='Cumulative Amount',
                  line=dict(color=colors['success'], width=3)),
        secondary_y=False
    )
    
    cumulative_fig.add_trace(
        go.Scatter(x=cumulative_data['donationdate'], 
                  y=cumulative_data['cumulative_count'],
                  mode='lines', name='Cumulative Count',
                  line=dict(color=colors['info'], width=2)),
        secondary_y=True
    )
    
    cumulative_fig.update_xaxes(title_text="Date")
    cumulative_fig.update_yaxes(title_text="Cumulative Amount (AED)", secondary_y=False)
    cumulative_fig.update_yaxes(title_text="Cumulative Count", secondary_y=True)
    cumulative_fig.update_layout(height=400, hovermode='x unified')
    
    # 9. Top Performers - Multiple metrics
    top_performers = filtered_df.groupby('donationtype').agg({
        'amount': ['sum', 'mean', 'count', 'std']
    }).reset_index()
    top_performers.columns = ['donationtype', 'total', 'average', 'count', 'std']
    top_performers['coefficient_of_variation'] = (top_performers['std'] / top_performers['average']) * 100
    top_performers = top_performers.sort_values('total', ascending=False).head(15)
    
    top_perf_fig = go.Figure()
    top_perf_fig.add_trace(go.Bar(
        x=top_performers['donationtype'],
        y=top_performers['total'],
        name='Total Amount',
        marker=dict(color=colors['primary']),
        text=top_performers['total'].apply(lambda x: f'{x:,.0f}'),
        textposition='outside'
    ))
    
    top_perf_fig.update_layout(
        height=400,
        xaxis_title='Donation Type',
        yaxis_title='Total Amount (AED)',
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    # 10. Statistics Table
    stats_data = {
        'Metric': ['Total Donations', 'Total Amount (AED)', 'Average Amount', 'Median Amount',
                  'Std Deviation', 'Min Amount', 'Max Amount', 'Q1 (25%)', 'Q3 (75%)',
                  'Skewness', 'Kurtosis'],
        'Value': [
            f"{len(filtered_df):,}",
            f"{filtered_df['amount'].sum():,.2f}",
            f"{filtered_df['amount'].mean():,.2f}",
            f"{filtered_df['amount'].median():,.2f}",
            f"{filtered_df['amount'].std():,.2f}",
            f"{filtered_df['amount'].min():,.2f}",
            f"{filtered_df['amount'].max():,.2f}",
            f"{filtered_df['amount'].quantile(0.25):,.2f}",
            f"{filtered_df['amount'].quantile(0.75):,.2f}",
            f"{stats.skew(filtered_df['amount']):.4f}",
            f"{stats.kurtosis(filtered_df['amount']):.4f}"
        ]
    }
    
    stats_table = dbc.Table.from_dataframe(
        pd.DataFrame(stats_data),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )
    
    return (total_donations, total_amount, avg_donation, unique_types,
            donations_change, amount_change, avg_change, types_info,
            trend_fig, pie_fig, dist_fig, heatmap_fig, seasonality_fig,
            amount_dist_fig, monthly_comp_fig, cumulative_fig, top_perf_fig,
            stats_table)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
