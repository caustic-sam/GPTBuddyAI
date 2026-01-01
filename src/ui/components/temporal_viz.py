"""
Temporal Visualization Components

Time-based visualizations showing evolution:
- Conversation activity timeline
- Topic evolution over time
- Knowledge accumulation curve
- Temporal heatmap (day/hour patterns)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
from pathlib import Path


def load_conversation_timeline() -> pd.DataFrame:
    """Load and prepare conversation data for timeline visualization

    Returns:
        DataFrame with temporal data
    """
    parquet_file = Path("artifacts/openai.parquet")

    if not parquet_file.exists():
        return None

    try:
        df = pd.read_parquet(parquet_file)

        # Convert timestamps
        if 'create_time' in df.columns:
            df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce')
            df = df.dropna(subset=['create_time'])

        # Filter to user messages
        if 'author' in df.columns:
            df = df[df['author'] == 'user']

        return df

    except Exception as e:
        st.error(f"Failed to load conversation data: {e}")
        return None


def render_activity_timeline(df: pd.DataFrame) -> go.Figure:
    """Create timeline showing conversation activity over time

    Args:
        df: Conversation DataFrame with create_time column

    Returns:
        Plotly figure
    """
    if df is None or len(df) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No conversation data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    # Group by month
    df['month'] = df['create_time'].dt.to_period('M').astype(str)
    monthly = df.groupby('month').size().reset_index(name='messages')

    # Create line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=monthly['month'],
        y=monthly['messages'],
        mode='lines+markers',
        line=dict(color='#4A90E2', width=3),
        marker=dict(size=8, color='#4A90E2'),
        fill='tozeroy',
        fillcolor='rgba(74, 144, 226, 0.2)',
        hovertemplate='<b>%{x}</b><br>Messages: %{y:,}<extra></extra>'
    ))

    # Add trend line
    if len(monthly) > 3:
        z = np.polyfit(range(len(monthly)), monthly['messages'], 1)
        p = np.poly1d(z)
        trend_y = p(range(len(monthly)))

        fig.add_trace(go.Scatter(
            x=monthly['month'],
            y=trend_y,
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='Trend',
            hoverinfo='skip'
        ))

    fig.update_layout(
        title={
            'text': f'Conversation Activity Timeline ({len(df):,} total messages)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Month',
        yaxis_title='Message Count',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    return fig


def render_weekly_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create heatmap showing activity by day of week and hour

    Args:
        df: Conversation DataFrame with create_time column

    Returns:
        Plotly figure
    """
    if df is None or len(df) == 0:
        return None

    # Extract day of week and hour
    df['day_of_week'] = df['create_time'].dt.day_name()
    df['hour'] = df['create_time'].dt.hour

    # Pivot table: day x hour
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = df.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)

    # Reindex to ensure all days present
    pivot = pivot.reindex(day_order, fill_value=0)

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=day_order,
        colorscale='Blues',
        hovertemplate='<b>%{y}</b> at %{x}<br>Messages: %{z}<extra></extra>',
        colorbar=dict(title="Messages")
    ))

    fig.update_layout(
        title={
            'text': 'Activity Heatmap (Day × Hour)',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_cumulative_knowledge(df: pd.DataFrame) -> go.Figure:
    """Create cumulative knowledge accumulation curve

    Args:
        df: Conversation DataFrame with create_time column

    Returns:
        Plotly figure
    """
    if df is None or len(df) == 0:
        return None

    # Sort by time
    df_sorted = df.sort_values('create_time')

    # Calculate cumulative count
    df_sorted['cumulative'] = range(1, len(df_sorted) + 1)

    # Sample for performance (show every Nth point for large datasets)
    sample_rate = max(1, len(df_sorted) // 500)
    df_sampled = df_sorted.iloc[::sample_rate]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_sampled['create_time'],
        y=df_sampled['cumulative'],
        mode='lines',
        line=dict(color='#66BB6A', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 187, 106, 0.2)',
        hovertemplate='<b>%{x}</b><br>Total Messages: %{y:,}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': 'Cumulative Knowledge Accumulation',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Date',
        yaxis_title='Cumulative Messages',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    return fig


def render_topic_evolution(df: pd.DataFrame) -> go.Figure:
    """Create stacked area chart showing topic evolution over time

    Args:
        df: Conversation DataFrame with cluster labels and timestamps

    Returns:
        Plotly figure
    """
    if df is None or len(df) == 0 or 'cluster' not in df.columns:
        return None

    # Load cluster labels
    label_file = Path("artifacts/cluster_labels.json")
    if label_file.exists():
        import json
        with open(label_file) as f:
            labels = json.load(f)
    else:
        labels = {}

    # Group by month and cluster
    df['month'] = df['create_time'].dt.to_period('M').astype(str)

    # Get top 5 clusters
    top_clusters = df['cluster'].value_counts().head(5).index.tolist()
    df_filtered = df[df['cluster'].isin(top_clusters)]

    # Pivot: month x cluster
    pivot = df_filtered.groupby(['month', 'cluster']).size().unstack(fill_value=0)

    # Create stacked area chart
    fig = go.Figure()

    for cluster_id in top_clusters:
        if cluster_id not in pivot.columns:
            continue

        label = labels.get(str(cluster_id), f"Cluster {cluster_id}")

        fig.add_trace(go.Scatter(
            x=pivot.index,
            y=pivot[cluster_id],
            mode='lines',
            stackgroup='one',
            name=label,
            hovertemplate=f'<b>{label}</b><br>%{{x}}: %{{y}} messages<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': 'Topic Evolution Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Month',
        yaxis_title='Message Count',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )

    return fig


def render_temporal_dashboard():
    """Render complete temporal visualization dashboard"""

    st.markdown("### 📅 Temporal Analysis Dashboard")

    # Load data
    df = load_conversation_timeline()

    if df is None or len(df) == 0:
        st.warning("⚠️ No conversation data available for temporal analysis")
        st.info("💡 Ingest your conversations: `python src/ingest/ingest_openai.py`")
        return

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Messages", f"{len(df):,}")

    with col2:
        min_date = df['create_time'].min()
        max_date = df['create_time'].max()
        date_range = f"{min_date.year}-{max_date.year}"
        st.metric("Time Span", date_range)

    with col3:
        days_active = (max_date - min_date).days
        avg_per_day = len(df) / max(days_active, 1)
        st.metric("Avg/Day", f"{avg_per_day:.1f}")

    with col4:
        # Find peak month
        monthly = df.groupby(df['create_time'].dt.to_period('M')).size()
        peak_month = monthly.idxmax()
        st.metric("Peak Month", str(peak_month))

    st.markdown("---")

    # Activity timeline
    st.plotly_chart(
        render_activity_timeline(df),
        use_container_width=True
    )

    st.markdown("---")

    # Two columns: Cumulative + Heatmap
    col1, col2 = st.columns(2)

    with col1:
        cumulative_fig = render_cumulative_knowledge(df)
        if cumulative_fig:
            st.plotly_chart(cumulative_fig, use_container_width=True)

    with col2:
        heatmap_fig = render_weekly_heatmap(df)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)

    st.markdown("---")

    # Topic evolution (if cluster data available)
    topic_fig = render_topic_evolution(df)
    if topic_fig:
        st.plotly_chart(topic_fig, use_container_width=True)
    else:
        st.info("💡 Run topic discovery to see topic evolution: `python src/analytics/topic_discovery.py`")
