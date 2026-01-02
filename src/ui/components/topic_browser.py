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

def load_cluster_analysis():
    """Load detailed cluster analysis with keywords and samples"""
    analysis_file = Path("artifacts/cluster_analysis.json")

    if not analysis_file.exists():
        return None

    try:
        with open(analysis_file) as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Could not load cluster analysis: {e}")
        return None

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

def render_semantic_topics():
    """Render semantic topic breakdown with keywords and sample messages"""
    st.markdown("### 🏷️ Semantic Topic Breakdown")

    # Load cluster analysis
    cluster_analysis = load_cluster_analysis()
    labels = load_cluster_labels()

    if not cluster_analysis:
        st.info("🔄 Generating topic analysis...")
        st.code("# This was just generated! Refresh the page to see results", language="bash")
        return

    # Sort clusters by size (largest first)
    sorted_clusters = sorted(
        cluster_analysis.items(),
        key=lambda x: x[1]['size'],
        reverse=True
    )

    # Display overview statistics
    total_messages = sum(info['size'] for _, info in sorted_clusters)
    st.metric("Total Clustered Messages", f"{total_messages:,}", help="Messages analyzed and grouped by topic")

    st.markdown("---")

    # Display each cluster
    for cluster_id, info in sorted_clusters[:15]:  # Show top 15 clusters
        size = info['size']
        keywords = info.get('keywords', [])
        samples = info.get('representative_messages', [])
        label = info.get('label', f"Topic {cluster_id}")

        # Calculate percentage
        pct = (size / total_messages * 100) if total_messages > 0 else 0

        # Create expander for each topic
        with st.expander(f"**{label}** — {size} messages ({pct:.1f}%)", expanded=False):

            # Keywords section
            if keywords:
                st.markdown("**🔑 Keywords:**")
                keyword_badges = " • ".join([f"`{kw}`" for kw in keywords])
                st.markdown(keyword_badges)
                st.markdown("")

            # Sample messages
            if samples:
                st.markdown("**💬 Representative Messages:**")
                for i, msg in enumerate(samples[:3], 1):  # Show top 3
                    # Truncate long messages
                    display_msg = msg[:200] + "..." if len(msg) > 200 else msg
                    st.markdown(f"{i}. *\"{display_msg}\"*")

                if len(samples) > 3:
                    st.caption(f"*...and {len(samples) - 3} more similar messages*")

    # Show remaining clusters summary
    if len(sorted_clusters) > 15:
        remaining = len(sorted_clusters) - 15
        remaining_size = sum(info['size'] for _, info in sorted_clusters[15:])
        st.markdown("---")
        st.caption(f"*+ {remaining} more topics with {remaining_size} messages*")

def render_cluster_selector():
    """Interactive cluster selection for detailed exploration"""
    st.markdown("### 🔍 Deep Dive into a Topic")

    labels = load_cluster_labels()

    if not labels:
        st.info("🔄 Topic labels being generated...")
        return

    # Create dropdown sorted by cluster ID
    cluster_options = {f"Topic {k}: {v}": k for k, v in sorted(labels.items(), key=lambda x: int(x[0]))}
    selected = st.selectbox("Select a topic to explore in detail:", options=list(cluster_options.keys()))

    if selected:
        cluster_id = cluster_options[selected]
        cluster_analysis = load_cluster_analysis()

        if cluster_analysis and cluster_id in cluster_analysis:
            info = cluster_analysis[cluster_id]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Messages in Topic", info['size'])
            with col2:
                st.metric("Keywords Extracted", len(info.get('keywords', [])))

            # Keywords
            if info.get('keywords'):
                st.markdown("**🔑 Keywords:**")
                st.write(" • ".join([f"`{kw}`" for kw in info['keywords']]))

            # Sample messages
            if info.get('representative_messages'):
                st.markdown("**💬 Sample Messages:**")
                for i, msg in enumerate(info['representative_messages'][:5], 1):
                    with st.container():
                        st.markdown(f"**Message {i}:**")
                        st.text_area("", msg, height=100, key=f"msg_{cluster_id}_{i}", disabled=True)
        else:
            st.info("💡 Detailed analysis for this topic is being processed...")

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

        # Topic clusters visualization
        render_topic_clusters()

        st.markdown("---")

        # NEW: Semantic topic breakdown
        render_semantic_topics()

        st.markdown("---")

        # Deep dive selector
        render_cluster_selector()

        st.markdown("---")

        # Volume chart
        render_volume_chart()

    with tab2:
        st.markdown("---")
        # Temporal dashboard
        render_temporal_dashboard()
