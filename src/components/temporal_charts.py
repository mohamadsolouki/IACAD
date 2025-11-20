"""
Temporal Analysis Charts
Charts showing temporal patterns (hourly, daily, monthly)
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ..config.theme import get_theme_colors, get_plot_template, get_chart_colors
from ..config.settings import DEFAULT_CHART_HEIGHT, HEATMAP_HEIGHT


def create_monthly_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create monthly donation heatmap.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'year' not in df.columns or 'month_name' not in df.columns:
        return go.Figure()
    
    monthly_data = df.groupby(['year', 'month_name'])['amount'].sum().reset_index()
    
    # Pivot for heatmap
    heatmap_data = monthly_data.pivot(index='month_name', columns='year', values='amount')
    
    # Order months correctly
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    heatmap_data = heatmap_data.reindex([m for m in month_order if m in heatmap_data.index])
    
    colors = get_theme_colors()
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlOrRd',
        text=heatmap_data.values,
        texttemplate='%{text:,.0f}',
        textfont={"size": 10},
        hovertemplate='Year: %{x}<br>Month: %{y}<br>Amount: AED %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Monthly Donation Heatmap (AED)",
        xaxis_title="Year",
        yaxis_title="Month",
        template=get_plot_template(),
        height=HEATMAP_HEIGHT
    )
    
    return fig


def create_hourly_pattern(df: pd.DataFrame) -> go.Figure:
    """
    Create hourly donation pattern chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'hour' not in df.columns:
        return go.Figure()
    
    hourly_data = df.groupby('hour').agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    hourly_data.columns = ['hour', 'total_amount', 'count']
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hourly_data['hour'],
        y=hourly_data['total_amount'],
        marker_color=colors['primary'],
        name='Total Amount',
        hovertemplate='Hour: %{x}<br>Amount: AED %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Donations by Hour of Day",
        xaxis_title="Hour (24-hour format)",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT
    )
    
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=1)
    
    return fig


def create_weekday_pattern(df: pd.DataFrame) -> go.Figure:
    """
    Create weekday donation pattern chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'weekday' not in df.columns:
        return go.Figure()
    
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    weekday_data = df.groupby('weekday').agg({
        'amount': ['sum', 'mean'],
        'id': 'count'
    }).reset_index()
    
    weekday_data.columns = ['weekday', 'total_amount', 'avg_amount', 'count']
    weekday_data['weekday'] = pd.Categorical(weekday_data['weekday'], categories=weekday_order, ordered=True)
    weekday_data = weekday_data.sort_values('weekday')
    
    colors = get_chart_colors()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=weekday_data['weekday'],
        y=weekday_data['total_amount'],
        marker_color=colors[1],
        name='Total Amount',
        text=weekday_data['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Total: AED %{y:,.0f}<br>Count: %{customdata:,}<extra></extra>',
        customdata=weekday_data['count']
    ))
    
    fig.update_layout(
        title="Donations by Day of Week",
        xaxis_title="Day of Week",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig


def create_time_weekday_heatmap(df: pd.DataFrame) -> go.Figure:
    """
    Create hour x weekday heatmap.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'hour' not in df.columns or 'weekday' not in df.columns:
        return go.Figure()
    
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = df.groupby(['weekday', 'hour'])['amount'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='weekday', columns='hour', values='amount').fillna(0)
    heatmap_pivot = heatmap_pivot.reindex([d for d in weekday_order if d in heatmap_pivot.index])
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_pivot.values,
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        colorscale='Viridis',
        hovertemplate='Day: %{y}<br>Hour: %{x}<br>Amount: AED %{z:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Donation Heatmap: Day of Week × Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        template=get_plot_template(),
        height=HEATMAP_HEIGHT
    )
    
    return fig


def create_yearly_monthly_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Create year-over-year monthly comparison.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'year' not in df.columns or 'month_name' not in df.columns:
        return go.Figure()
    
    monthly_yearly = df.groupby(['year', 'month_name'])['amount'].sum().reset_index()
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    colors = get_chart_colors()
    
    fig = go.Figure()
    
    for idx, year in enumerate(sorted(monthly_yearly['year'].unique())):
        year_data = monthly_yearly[monthly_yearly['year'] == year]
        year_data['month_name'] = pd.Categorical(year_data['month_name'], categories=month_order, ordered=True)
        year_data = year_data.sort_values('month_name')
        
        fig.add_trace(go.Scatter(
            x=year_data['month_name'],
            y=year_data['amount'],
            mode='lines+markers',
            name=str(year),
            line=dict(color=colors[idx % len(colors)], width=2),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Monthly Donations Year-over-Year Comparison",
        xaxis_title="Month",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT,
        hovermode='x unified'
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig
