"""
Donor Analysis Charts
Charts focused on donor behavior and patterns
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ..config.theme import get_theme_colors, get_plot_template, get_chart_colors
from ..config.settings import DEFAULT_CHART_HEIGHT, TOP_N_DONORS


def create_top_donors_chart(
    df: pd.DataFrame,
    top_n: int = TOP_N_DONORS
) -> go.Figure:
    """
    Create top donors chart.
    
    Args:
        df: Input DataFrame
        top_n: Number of top donors to show
        
    Returns:
        Plotly Figure object
    """
    if 'id' not in df.columns:
        return go.Figure()
    
    donor_data = df.groupby('id').agg({
        'amount': ['sum', 'count', 'mean']
    }).reset_index()
    
    donor_data.columns = ['donor_id', 'total_amount', 'donation_count', 'avg_amount']
    donor_data = donor_data.nlargest(top_n, 'total_amount')
    donor_data['donor_label'] = [f"Donor {i+1}" for i in range(len(donor_data))]
    
    colors = get_theme_colors()
    chart_colors = get_chart_colors()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f'Top {top_n} Donors by Amount', f'Top {top_n} Donors by Count'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # By total amount
    fig.add_trace(
        go.Bar(
            x=donor_data['donor_label'],
            y=donor_data['total_amount'],
            marker_color=chart_colors[0],
            text=donor_data['total_amount'].apply(lambda x: f'AED {x:,.0f}'),
            textposition='outside',
            name='Total Amount'
        ),
        row=1, col=1
    )
    
    # By donation count
    fig.add_trace(
        go.Bar(
            x=donor_data['donor_label'],
            y=donor_data['donation_count'],
            marker_color=chart_colors[1],
            text=donor_data['donation_count'].apply(lambda x: f'{x:,}'),
            textposition='outside',
            name='Donation Count'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT,
        showlegend=False
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_donor_behavior_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Create donor behavior segmentation chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'id' not in df.columns:
        return go.Figure()
    
    donor_stats = df.groupby('id').agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    donor_stats.columns = ['donor_id', 'total_amount', 'donation_count']
    
    # Segment donors
    donor_stats['segment'] = 'One-time'
    donor_stats.loc[donor_stats['donation_count'] >= 2, 'segment'] = 'Occasional (2-4)'
    donor_stats.loc[donor_stats['donation_count'] >= 5, 'segment'] = 'Regular (5-9)'
    donor_stats.loc[donor_stats['donation_count'] >= 10, 'segment'] = 'Frequent (10+)'
    
    segment_stats = donor_stats.groupby('segment').agg({
        'donor_id': 'count',
        'total_amount': 'sum',
        'donation_count': 'sum'
    }).reset_index()
    
    segment_stats.columns = ['segment', 'donor_count', 'total_amount', 'total_donations']
    
    colors = get_chart_colors()
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Donors by Segment', 'Amount by Segment'),
        specs=[[{'type': 'pie'}, {'type': 'pie'}]]
    )
    
    fig.add_trace(
        go.Pie(
            labels=segment_stats['segment'],
            values=segment_stats['donor_count'],
            marker=dict(colors=colors),
            textinfo='label+percent',
            name='Donor Count'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Pie(
            labels=segment_stats['segment'],
            values=segment_stats['total_amount'],
            marker=dict(colors=colors),
            textinfo='label+percent',
            name='Total Amount'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Donor Behavior Segmentation",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig


def create_donor_retention_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create donor retention/repeat rate chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'id' not in df.columns or 'year' not in df.columns:
        return go.Figure()
    
    # Calculate donors per year
    yearly_donors = df.groupby(['year', 'id']).size().reset_index()
    yearly_donors = yearly_donors.groupby('year')['id'].nunique().reset_index()
    yearly_donors.columns = ['year', 'unique_donors']
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=yearly_donors['year'],
        y=yearly_donors['unique_donors'],
        marker_color=colors['success'],
        text=yearly_donors['unique_donors'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        name='Unique Donors'
    ))
    
    fig.update_layout(
        title="Unique Donors by Year",
        xaxis_title="Year",
        yaxis_title="Number of Unique Donors",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig


def create_donation_frequency_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create donation frequency distribution chart.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Plotly Figure object
    """
    if 'id' not in df.columns:
        return go.Figure()
    
    donor_counts = df.groupby('id').size().reset_index()
    donor_counts.columns = ['donor_id', 'donation_count']
    
    # Create frequency distribution
    freq_dist = donor_counts['donation_count'].value_counts().sort_index().reset_index()
    freq_dist.columns = ['donations', 'donor_count']
    freq_dist = freq_dist[freq_dist['donations'] <= 20]  # Limit to 20 for readability
    
    colors = get_theme_colors()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=freq_dist['donations'],
        y=freq_dist['donor_count'],
        marker_color=colors['info'],
        text=freq_dist['donor_count'].apply(lambda x: f'{x:,}'),
        textposition='outside',
        name='Donor Count'
    ))
    
    fig.update_layout(
        title="Donation Frequency Distribution",
        xaxis_title="Number of Donations",
        yaxis_title="Number of Donors",
        template=get_plot_template(),
        height=DEFAULT_CHART_HEIGHT
    )
    
    return fig
