"""
Category and Distribution Charts
Charts showing donation categories and distributions
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ..config.theme import get_theme_colors, get_plot_template, get_chart_colors
from ..config.settings import DEFAULT_CHART_HEIGHT, TOP_N_CATEGORIES


def create_category_distribution(
    df: pd.DataFrame, 
    top_n: int = TOP_N_CATEGORIES, 
    dark_mode: bool = False
) -> go.Figure:
    """
    Create category distribution pie chart.
    
    Args:
        df: Input DataFrame
        top_n: Number of top categories to show
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
    
    category_data = df.groupby(column)['amount'].sum().nlargest(top_n).reset_index()
    
    colors = get_chart_colors(dark_mode)
    
    fig = go.Figure(data=[go.Pie(
        labels=category_data[column],
        values=category_data['amount'],
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Amount: AED %{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=f"Top {top_n} Donation Categories",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig


def create_category_bar_chart(
    df: pd.DataFrame, 
    top_n: int = TOP_N_CATEGORIES,
    dark_mode: bool = False
) -> go.Figure:
    """
    Create horizontal bar chart for categories.
    
    Args:
        df: Input DataFrame
        top_n: Number of top categories to show
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    column = 'donationtype_en' if 'donationtype_en' in df.columns else 'donationtype'
    
    category_data = df.groupby(column).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    category_data.columns = [column, 'total_amount', 'count']
    category_data = category_data.nlargest(top_n, 'total_amount')
    category_data = category_data.sort_values('total_amount')
    
    colors = get_theme_colors(dark_mode)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=category_data[column],
        x=category_data['total_amount'],
        orientation='h',
        marker_color=colors['primary'],
        text=category_data['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Total: AED %{x:,.0f}<br>Count: %{customdata:,}<extra></extra>',
        customdata=category_data['count']
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Donation Categories by Amount",
        xaxis_title="Total Amount (AED)",
        yaxis_title="Category",
        template=get_plot_template(dark_mode),
        height=max(DEFAULT_CHART_HEIGHT, top_n * 30)
    )
    
    return fig


def create_amount_distribution(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Create amount distribution histogram.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    colors = get_theme_colors(dark_mode)
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['amount'],
        nbinsx=50,
        marker_color=colors['info'],
        name='Distribution'
    ))
    
    fig.update_layout(
        title="Donation Amount Distribution",
        xaxis_title="Amount (AED)",
        yaxis_title="Frequency",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    return fig


def create_amount_range_distribution(df: pd.DataFrame, dark_mode: bool = False) -> go.Figure:
    """
    Create grouped amount range distribution.
    
    Args:
        df: Input DataFrame
        dark_mode: Whether to use dark theme
        
    Returns:
        Plotly Figure object
    """
    # Define amount ranges
    bins = [0, 100, 500, 1000, 5000, 10000, float('inf')]
    labels = ['0-100', '100-500', '500-1K', '1K-5K', '5K-10K', '10K+']
    
    df_copy = df.copy()
    df_copy['amount_range'] = pd.cut(df_copy['amount'], bins=bins, labels=labels)
    
    range_stats = df_copy.groupby('amount_range', observed=True).agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    range_stats.columns = ['range', 'total_amount', 'count']
    
    colors = get_chart_colors(dark_mode)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=range_stats['range'],
        y=range_stats['count'],
        marker_color=colors[0],
        text=range_stats['count'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        name='Count'
    ))
    
    fig.update_layout(
        title="Donation Count by Amount Range",
        xaxis_title="Amount Range (AED)",
        yaxis_title="Number of Donations",
        template=get_plot_template(dark_mode),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig
