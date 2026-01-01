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
import sys

# Import temporal visualization
sys.path.append(str(Path(__file__).parent))
from temporal_viz import render_temporal_dashboard

def load_cluster_labels():
    """Load cluster labels with error handling"""
    label_file = Path("artifacts/cluster_labels.json")

    if not label_file.exists():
        return {}

    try:
        with open(label_file) as f:
            labels = json.load(f)

        # Validate structure
        if not isinstance(labels, dict):
            st.warning("⚠️ Invalid cluster labels format")
            return {}

        return labels

    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse cluster labels: {str(e)[:200]}")
        st.info("💡 The JSON file may be corrupted. Try regenerating:")
        st.code("python src/analytics/label_clusters.py", language="bash")
        return {}
    except Exception as e:
        st.error(f"❌ Failed to load cluster labels: {str(e)[:200]}")
        st.info(f"💡 Check file permissions for: {label_file}")
        return {}

def load_conversation_data():
    """Load OpenAI conversation data with error handling"""
    parquet_file = Path("artifacts/openai.parquet")
    if not parquet_file.exists():
        return None

    try:
        return pd.read_parquet(parquet_file)
    except Exception as e:
        st.error(f"❌ Failed to load conversations: {e}")
        st.info("💡 Try running: `python src/ingest/ingest_openai.py`")
        return None

def render_topic_overview():
    """Render high-level topic statistics with error handling"""
    st.markdown("### 📊 Your Intellectual Journey")

    df = load_conversation_data()
    if df is None:
        st.warning("⚠️ No conversation data loaded")
        st.info("💡 Ingest your conversations:")
        st.code("python src/ingest/ingest_openai.py", language="bash")
        return

    try:
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
                try:
                    df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce')
                    valid_dates = df['create_time'].dropna()
                    if len(valid_dates) > 0:
                        date_range = f"{valid_dates.min().year} - {valid_dates.max().year}"
                    else:
                        date_range = "Unknown"
                except Exception:
                    date_range = "Unknown"
            else:
                date_range = "Unknown"
            st.metric("Date Range", date_range)

    except Exception as e:
        st.error(f"❌ Failed to render topic overview: {str(e)[:200]}")
        st.info("💡 Your conversation data may have an unexpected format")

def render_topic_clusters():
    """Render cluster visualization and selection"""
    st.markdown("### 🗺️ Topic Map")

    # Check if visualization exists
    viz_file = Path("artifacts/topic_clusters_2d.png")
    if viz_file.exists():
        st.image(str(viz_file), caption="25 Conversation Topics (K-Means Clustering)", use_column_width=True)
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
    """Render conversation volume over time with interactive filters"""
    st.markdown("### 📈 Activity Over Time")

    df = load_conversation_data()
    if df is None or 'create_time' not in df.columns:
        st.warning("No temporal data available")
        return

    try:
        # Convert to datetime
        df['create_time'] = pd.to_datetime(df['create_time'], unit='s', errors='coerce')
        df = df.dropna(subset=['create_time'])

        # Filter to user messages
        if 'author' in df.columns:
            df = df[df['author'] == 'user']

        if len(df) == 0:
            st.warning("No messages with valid timestamps")
            return

        # Date range filter
        min_date = df['create_time'].min().date()
        max_date = df['create_time'].max().date()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date)

        # Filter dataframe by date range
        mask = (df['create_time'].dt.date >= start_date) & (df['create_time'].dt.date <= end_date)
        filtered_df = df[mask]

        if len(filtered_df) == 0:
            st.warning("⚠️ No data in selected date range")
            st.info("💡 Try adjusting the date filter or check your data")
            return

        # Group by month
        filtered_df['month'] = filtered_df['create_time'].dt.to_period('M').astype(str)
        monthly = filtered_df.groupby('month').size().reset_index(name='messages')

        # Plot with Plotly
        fig = px.line(monthly, x='month', y='messages',
                      title=f'Messages per Month ({len(filtered_df):,} total)',
                      labels={'month': 'Month', 'messages': 'Message Count'})

        fig.update_traces(line_color='#4A90E2', line_width=3, mode='lines+markers')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2E3440'),
            xaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
            yaxis=dict(showgrid=True, gridcolor='#E0E0E0'),
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to render chart: {e}")
        return

def render_topic_browser():
    """Main topic browser component"""

    st.markdown("## 💬 My Conversations")
    st.markdown("Explore your intellectual journey through AI-discovered topics")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Topics & Clusters", "📅 Temporal Analysis"])

    with tab1:
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

    with tab2:
        st.markdown("---")
        # Temporal dashboard
        render_temporal_dashboard()
