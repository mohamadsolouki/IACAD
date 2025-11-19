"""
Ramadan Analysis Charts
Charts specific to Ramadan analysis
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from ..config.theme import get_theme_colors, get_plot_template, get_chart_colors
from ..config.settings import DEFAULT_CHART_HEIGHT


def create_ramadan_comparison_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Create Ramadan vs Non-Ramadan comparison.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
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
        title="Ramadan vs Non-Ramadan Comparison",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    return fig


def create_islamic_events_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Create Islamic events distribution chart.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    if 'islamic_event' not in df.columns:
        return go.Figure()
    
    # Filter out null events and get top events
    events_df = df[df['islamic_event'].notna()].copy()
    
    if events_df.empty:
        return go.Figure()
    
    event_stats = events_df.groupby('islamic_event').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    event_stats.columns = ['event', 'total_amount', 'avg_amount', 'count']
    event_stats = event_stats.nlargest(10, 'total_amount')
    
    colors = get_chart_colors(dark_mode)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Total Donations by Islamic Event', 'Average Donation by Event'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    fig.add_trace(
        go.Bar(
            x=event_stats['event'],
            y=event_stats['total_amount'],
            marker_color=colors[0],
            name='Total Amount',
            text=event_stats['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(
            x=event_stats['event'],
            y=event_stats['avg_amount'],
            marker_color=colors[1],
            name='Avg Amount',
            text=event_stats['avg_amount'].apply(lambda x: f'AED {x:,.0f}'),
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Donations During Islamic Events",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_hijri_months_chart(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Create Hijri months analysis chart.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    if 'hijri_month_name' not in df.columns:
        return go.Figure()
    
    hijri_df = df[df['hijri_month_name'].notna()].copy()
    
    if hijri_df.empty:
        return go.Figure()
    
    monthly_stats = hijri_df.groupby('hijri_month_name').agg({
        'amount': ['sum', 'mean', 'count']
    }).reset_index()
    
    monthly_stats.columns = ['month', 'total_amount', 'avg_amount', 'count']
    
    colors = get_chart_colors(dark_mode)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_stats['month'],
        y=monthly_stats['total_amount'],
        marker_color=colors[2],
        text=monthly_stats['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Total: AED %{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Donations by Hijri Month",
        xaxis_title="Hijri Month",
        yaxis_title="Total Amount (AED)",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig
