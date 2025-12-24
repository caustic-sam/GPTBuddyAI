"""
Interactive Topic Browser Component for Streamlit

Displays conversation clusters with:
- Visual topic map
- Cluster selection
- Sample messages
- Temporal filtering
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

def load_cluster_labels():
    """Load cluster labels if available"""
    label_file = Path("artifacts/cluster_labels.json")
    if label_file.exists():
        with open(label_file) as f:
            return json.load(f)
    return {}

def load_conversation_data():
    """Load OpenAI conversation data"""
    parquet_file = Path("artifacts/openai.parquet")
    if parquet_file.exists():
        return pd.read_parquet(parquet_file)
    return None

def render_topic_overview():
    """Render high-level topic statistics"""
    st.markdown("### 📊 Your Intellectual Journey")

    df = load_conversation_data()
    if df is None:
        st.warning("No conversation data loaded")
        return

    # Filter to user messages
    if 'author' in df.columns:
        user_df = df[df['author'] == 'user']
    else:
        user_df = df

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Messages", f"{len(user_df):,}")

    with col2:
        if 'conversation_id' in df.columns:
            n_convos = df['conversation_id'].nunique()
        else:
            n_convos = "N/A"
        st.metric("Conversations", n_convos)

    with col3:
        if 'create_time' in df.columns:
            df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce')
            date_range = f"{df['create_time'].min().year} - {df['create_time'].max().year}"
        else:
            date_range = "Unknown"
        st.metric("Date Range", date_range)

def render_topic_clusters():
    """Render cluster visualization and selection"""
    st.markdown("### 🗺️ Topic Map")

    # Check if visualization exists
    viz_file = Path("artifacts/topic_clusters_2d.png")
    if viz_file.exists():
        st.image(str(viz_file), caption="25 Conversation Topics (K-Means Clustering)", use_container_width=True)
    else:
        st.info("🔄 Run topic discovery to generate the map: `python src/analytics/topic_discovery.py`")

def render_cluster_selector():
    """Interactive cluster selection and exploration"""
    st.markdown("### 🔍 Explore Topics")

    labels = load_cluster_labels()

    if not labels:
        st.warning("Run cluster labeling first: `python src/analytics/label_clusters.py`")

        # Temporary manual labels for demo
        labels = {
            "0": "AI/AGI Ethics & Regulation",
            "2": "Digital Identity & Privacy",
            "3": "Privacy Threats & Solutions",
            "7": "CBDC & Digital Policy",
            "1": "Python Development",
            "14": "DevOps & System Admin",
            "15": "Video Processing Projects",
            "4": "Writing & Content Style",
            "6": "Academic Research",
        }

    # Create dropdown
    cluster_options = {f"Cluster {k}: {v}": k for k, v in labels.items()}
    selected = st.selectbox("Select a topic to explore:", options=list(cluster_options.keys()))

    if selected:
        cluster_id = cluster_options[selected]
        st.markdown(f"**Selected**: {selected}")

        # TODO: Load and display sample messages from this cluster
        st.info("💡 This will show sample messages from your conversations in this topic cluster")

        # Placeholder for sample messages
        with st.expander("📝 Sample Messages (Coming Soon)", expanded=False):
            st.markdown("""
            This feature will display:
            - Top 10 representative messages from this cluster
            - Date range when you explored this topic
            - Related clusters
            - Export option
            """)

def render_volume_chart():
    """Render conversation volume over time"""
    st.markdown("### 📈 Activity Over Time")

    df = load_conversation_data()
    if df is None or 'create_time' not in df.columns:
        st.warning("No temporal data available")
        return

    # Convert to datetime
    df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce')
    df = df.dropna(subset=['create_time'])

    # Filter to user messages
    if 'author' in df.columns:
        df = df[df['author'] == 'user']

    # Group by month
    df['month'] = df['create_time'].dt.to_period('M').astype(str)
    monthly = df.groupby('month').size().reset_index(name='messages')

    # Plot with Plotly
    fig = px.line(monthly, x='month', y='messages',
                  title='Messages per Month',
                  labels={'month': 'Month', 'messages': 'Message Count'})

    fig.update_traces(line_color='#4A90E2', line_width=3)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2E3440'),
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0')
    )

    st.plotly_chart(fig, use_container_width=True)

def render_topic_browser():
    """Main topic browser component"""

    st.markdown("## 💬 My Conversations")
    st.markdown("Explore your intellectual journey through AI-discovered topics")

    st.markdown("---")

    # Overview stats
    render_topic_overview()

    st.markdown("---")

    # Topic clusters
    render_topic_clusters()

    st.markdown("---")

    # Cluster selector
    render_cluster_selector()

    st.markdown("---")

    # Volume chart
    render_volume_chart()
