"""
Time Series Charts
Charts showing donation trends over time
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from ..config.theme import get_theme_colors, get_plot_template, get_chart_colors
from ..config.settings import DEFAULT_CHART_HEIGHT


def create_time_series_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create enhanced time series with Ramadan highlighting.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    daily_data = df.groupby('date').agg({
        'amount': 'sum',
        'id': 'count',
        'is_ramadan': 'first'
    }).reset_index()
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    # Separate Ramadan and non-Ramadan periods
    ramadan_data = daily_data[daily_data['is_ramadan'] == True]
    non_ramadan_data = daily_data[daily_data['is_ramadan'] == False]
    
    # Non-Ramadan data
    if not non_ramadan_data.empty:
        fig.add_trace(go.Scatter(
            x=non_ramadan_data['date'],
            y=non_ramadan_data['amount'],
            mode='lines',
            name='Regular Days',
            line=dict(color=colors['primary'], width=2),
            fill='tozeroy',
            fillcolor=f"rgba({int(colors['primary'][1:3], 16)}, {int(colors['primary'][3:5], 16)}, {int(colors['primary'][5:7], 16)}, 0.1)"
        ))
    
    # Ramadan data with highlighting
    if not ramadan_data.empty:
        fig.add_trace(go.Scatter(
            x=ramadan_data['date'],
            y=ramadan_data['amount'],
            mode='lines',
            name='Ramadan',
            line=dict(color=colors['warning'], width=3),
            fill='tozeroy',
            fillcolor=f"rgba({int(colors['warning'][1:3], 16)}, {int(colors['warning'][3:5], 16)}, {int(colors['warning'][5:7], 16)}, 0.2)"
        ))
    
    fig.update_layout(
        title="Donation Trends Over Time (Ramadan Highlighted)",
        xaxis_title="Date",
        yaxis_title="Amount (AED)",
        hovermode='x unified',
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT,
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


def create_cumulative_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create cumulative donation amount chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    daily_data = df.groupby('date')['amount'].sum().reset_index()
    daily_data['cumulative'] = daily_data['amount'].cumsum()
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['cumulative'],
        mode='lines',
        name='Cumulative Amount',
        line=dict(color=colors['success'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba({int(colors['success'][1:3], 16)}, {int(colors['success'][3:5], 16)}, {int(colors['success'][5:7], 16)}, 0.2)"
    ))
    
    fig.update_layout(
        title="Cumulative Donation Amount",
        xaxis_title="Date",
        yaxis_title="Cumulative Amount (AED)",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT,
        hovermode='x unified'
    )
    
    return fig


def create_moving_average_chart(
    df: pd.DataFrame, 
    window: int = 7
) -> go.Figure:
    """
    Create moving average chart.
    
    Args:
        df: Input DataFrame
        window: Window size for moving average
        
    Returns:
        Plotly Figure object
    """
    daily_data = df.groupby('date')['amount'].sum().reset_index()
    daily_data['moving_avg'] = daily_data['amount'].rolling(window=window).mean()
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    # Daily data
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['amount'],
        mode='lines',
        name='Daily Amount',
        line=dict(color=colors['secondary'], width=1),
        opacity=0.5
    ))
    
    # Moving average
    fig.add_trace(go.Scatter(
        x=daily_data['date'],
        y=daily_data['moving_avg'],
        mode='lines',
        name=f'{window}-Day Moving Average',
        line=dict(color=colors['primary'], width=3)
    ))
    
    fig.update_layout(
        title=f"Donation Trends with {window}-Day Moving Average",
        xaxis_title="Date",
        yaxis_title="Amount (AED)",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT,
        hovermode='x unified'
    )
    
    return fig
