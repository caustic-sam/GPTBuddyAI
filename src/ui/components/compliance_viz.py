"""
Compliance Visualization Components

Advanced visualizations for compliance analysis:
- Compliance heatmap (control families)
- Coverage timeline
- Priority matrix
- Gap waterfall chart
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, List, Any
from collections import defaultdict


def render_compliance_heatmap(classification: Dict[str, List[str]]) -> go.Figure:
    """Create heatmap showing control coverage by family

    Args:
        classification: Dict with 'implemented', 'partial', 'gaps' lists

    Returns:
        Plotly figure
    """
    # Extract all controls and group by family
    all_controls = (
        classification.get('implemented', []) +
        classification.get('partial', []) +
        classification.get('gaps', [])
    )

    # Group by family
    families = defaultdict(lambda: {'implemented': 0, 'partial': 0, 'gaps': 0, 'total': 0})

    for control in all_controls:
        # Extract family (first part before dash)
        family = control.split('-')[0] if '-' in control else 'OTHER'

        # Determine status
        if control in classification.get('implemented', []):
            families[family]['implemented'] += 1
        elif control in classification.get('partial', []):
            families[family]['partial'] += 1
        elif control in classification.get('gaps', []):
            families[family]['gaps'] += 1

        families[family]['total'] += 1

    # Convert to DataFrame
    family_names = sorted(families.keys())
    data = []

    for family in family_names:
        stats = families[family]
        total = stats['total']

        data.append({
            'Family': family,
            'Implemented': stats['implemented'],
            'Partial': stats['partial'],
            'Gaps': stats['gaps'],
            'Total': total,
            'Coverage %': (stats['implemented'] / total * 100) if total > 0 else 0
        })

    df = pd.DataFrame(data)

    # Create heatmap matrix (family x status)
    matrix_data = []
    for _, row in df.iterrows():
        matrix_data.append([row['Implemented'], row['Partial'], row['Gaps']])

    # Create figure
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=['✅ Implemented', '⚠️ Partial', '❌ Gaps'],
        y=df['Family'].tolist(),
        colorscale=[
            [0, '#D32F2F'],      # Red (gaps)
            [0.5, '#FFA726'],    # Orange (partial)
            [1, '#66BB6A']       # Green (implemented)
        ],
        text=matrix_data,
        texttemplate='%{text}',
        textfont={"size": 14, "color": "white"},
        hovertemplate='<b>%{y}</b><br>%{x}: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': 'NIST Control Coverage Heatmap',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Status',
        yaxis_title='Control Family',
        height=max(400, len(family_names) * 30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_coverage_gauge(summary: Dict[str, int]) -> go.Figure:
    """Create gauge chart showing overall coverage

    Args:
        summary: Dict with 'implemented', 'partial', 'gaps' counts

    Returns:
        Plotly figure
    """
    total = summary.get('implemented', 0) + summary.get('partial', 0) + summary.get('gaps', 0)
    implemented = summary.get('implemented', 0)
    coverage_pct = (implemented / total * 100) if total > 0 else 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=coverage_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Coverage %", 'font': {'size': 20}},
        delta={'reference': 80, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#66BB6A"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#FFCDD2'},
                {'range': [50, 80], 'color': '#FFE082'},
                {'range': [80, 100], 'color': '#C8E6C9'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_priority_matrix(recommendations: List[Dict[str, Any]]) -> go.Figure:
    """Create priority matrix scatter plot

    Args:
        recommendations: List of recommendation dicts

    Returns:
        Plotly figure
    """
    if not recommendations:
        # Empty placeholder
        fig = go.Figure()
        fig.add_annotation(
            text="No recommendations to visualize",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig

    # Map priority to numeric impact score
    priority_map = {'High': 3, 'Medium': 2, 'Low': 1}

    # Extract data
    controls = []
    priorities = []
    priority_scores = []
    colors = []
    hover_texts = []

    for rec in recommendations[:50]:  # Limit to 50 for readability
        control_id = rec.get('control_id', 'Unknown')
        priority = rec.get('priority', 'Low')
        action = rec.get('action', 'No action')
        reason = rec.get('reason', 'No reason')

        controls.append(control_id)
        priorities.append(priority)
        priority_scores.append(priority_map.get(priority, 1))

        # Color by priority
        if priority == 'High':
            colors.append('#D32F2F')
        elif priority == 'Medium':
            colors.append('#FFA726')
        else:
            colors.append('#66BB6A')

        hover_texts.append(f"<b>{control_id}</b><br>Priority: {priority}<br>Action: {action}")

    # Create scatter plot
    # X-axis: Index (just for spreading), Y-axis: Priority score
    fig = go.Figure()

    for priority_val in [3, 2, 1]:
        priority_label = {3: 'High', 2: 'Medium', 1: 'Low'}[priority_val]
        mask = [p == priority_val for p in priority_scores]

        x_vals = [i for i, m in enumerate(mask) if m]
        y_vals = [priority_val] * len(x_vals)
        texts = [controls[i] for i, m in enumerate(mask) if m]
        hovers = [hover_texts[i] for i, m in enumerate(mask) if m]
        cols = [colors[i] for i, m in enumerate(mask) if m]

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode='markers+text',
            marker=dict(size=12, color=cols),
            text=texts,
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hovers,
            name=priority_label
        ))

    fig.update_layout(
        title={
            'text': 'Remediation Priority Matrix',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        yaxis={
            'title': 'Priority',
            'tickmode': 'array',
            'tickvals': [1, 2, 3],
            'ticktext': ['Low', 'Medium', 'High'],
            'range': [0.5, 3.5]
        },
        xaxis={'visible': False},
        height=500,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_gap_waterfall(summary: Dict[str, int]) -> go.Figure:
    """Create waterfall chart showing gap analysis

    Args:
        summary: Dict with 'implemented', 'partial', 'gaps' counts

    Returns:
        Plotly figure
    """
    total = summary.get('implemented', 0) + summary.get('partial', 0) + summary.get('gaps', 0)
    implemented = summary.get('implemented', 0)
    partial = summary.get('partial', 0)
    gaps = summary.get('gaps', 0)

    fig = go.Figure(go.Waterfall(
        name="Gap Analysis",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["Total Controls", "✅ Implemented", "⚠️ Partial", "❌ Remaining Gaps"],
        y=[total, implemented, partial, -(implemented + partial)],
        text=[total, implemented, partial, gaps],
        textposition="outside",
        decreasing={"marker": {"color": "#D32F2F"}},
        increasing={"marker": {"color": "#66BB6A"}},
        totals={"marker": {"color": "#1976D2"}},
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title={
            'text': 'Compliance Gap Waterfall',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def render_family_coverage_bars(classification: Dict[str, List[str]]) -> go.Figure:
    """Create stacked bar chart of family coverage

    Args:
        classification: Dict with 'implemented', 'partial', 'gaps' lists

    Returns:
        Plotly figure
    """
    # Group by family
    all_controls = (
        classification.get('implemented', []) +
        classification.get('partial', []) +
        classification.get('gaps', [])
    )

    families = defaultdict(lambda: {'implemented': 0, 'partial': 0, 'gaps': 0})

    for control in all_controls:
        family = control.split('-')[0] if '-' in control else 'OTHER'

        if control in classification.get('implemented', []):
            families[family]['implemented'] += 1
        elif control in classification.get('partial', []):
            families[family]['partial'] += 1
        elif control in classification.get('gaps', []):
            families[family]['gaps'] += 1

    # Prepare data
    family_names = sorted(families.keys())
    implemented_counts = [families[f]['implemented'] for f in family_names]
    partial_counts = [families[f]['partial'] for f in family_names]
    gap_counts = [families[f]['gaps'] for f in family_names]

    # Create stacked bars
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='✅ Implemented',
        x=family_names,
        y=implemented_counts,
        marker_color='#66BB6A',
        text=implemented_counts,
        textposition='inside'
    ))

    fig.add_trace(go.Bar(
        name='⚠️ Partial',
        x=family_names,
        y=partial_counts,
        marker_color='#FFA726',
        text=partial_counts,
        textposition='inside'
    ))

    fig.add_trace(go.Bar(
        name='❌ Gaps',
        x=family_names,
        y=gap_counts,
        marker_color='#D32F2F',
        text=gap_counts,
        textposition='inside'
    ))

    fig.update_layout(
        title={
            'text': 'Control Coverage by Family',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Control Family',
        yaxis_title='Number of Controls',
        barmode='stack',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig


def render_compliance_dashboard(
    summary: Dict[str, int],
    classification: Dict[str, List[str]],
    recommendations: List[Dict[str, Any]]
):
    """Render complete compliance visualization dashboard

    Args:
        summary: Summary statistics
        classification: Control classifications
        recommendations: Remediation recommendations
    """
    st.markdown("### 📊 Compliance Visualization Dashboard")

    # Row 1: Gauge + Waterfall
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            render_coverage_gauge(summary),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            render_gap_waterfall(summary),
            use_container_width=True
        )

    st.markdown("---")

    # Row 2: Heatmap
    st.plotly_chart(
        render_compliance_heatmap(classification),
        use_container_width=True
    )

    st.markdown("---")

    # Row 3: Family bars
    st.plotly_chart(
        render_family_coverage_bars(classification),
        use_container_width=True
    )

    st.markdown("---")

    # Row 4: Priority matrix
    if recommendations:
        st.plotly_chart(
            render_priority_matrix(recommendations),
            use_container_width=True
        )
