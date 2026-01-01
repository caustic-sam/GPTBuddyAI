"""
Knowledge Graph UI Component

Interactive knowledge graph visualization and exploration:
- Entity browser
- Relationship explorer
- Graph visualization
- Entity detail views
"""

import streamlit as st
import sys
from pathlib import Path
import json
import networkx as nx
from typing import Dict, Any, List
import plotly.graph_objects as go

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from graph import KnowledgeGraphBuilder, GraphEnhancedRAG
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


def render_knowledge_graph():
    """Main knowledge graph component"""

    st.markdown("## 🕸️ Knowledge Graph")
    st.markdown("Explore entity relationships and graph-based reasoning")

    st.markdown("---")

    if not GRAPH_AVAILABLE:
        st.error("❌ Knowledge graph module not available")
        st.info("💡 Ensure graph dependencies are installed")
        return

    # Check if graph exists
    graph_path = Path("artifacts/graph/knowledge_graph.pkl")
    if not graph_path.exists():
        render_graph_build_ui()
        return

    # Load graph
    if 'graph_builder' not in st.session_state:
        try:
            with st.spinner("🔄 Loading knowledge graph..."):
                graph_builder = KnowledgeGraphBuilder()
                graph_builder.load_graph(graph_path)
                st.session_state['graph_builder'] = graph_builder
        except Exception as e:
            st.error(f"❌ Failed to load graph: {e}")
            st.info("💡 Try rebuilding the graph:")
            st.code("python src/graph/build_knowledge_graph.py", language="bash")
            return

    graph_builder = st.session_state['graph_builder']

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "🔍 Entity Explorer",
        "🗺️ Graph Visualization",
        "🔗 Relationship Browser"
    ])

    with tab1:
        render_graph_overview(graph_builder)

    with tab2:
        render_entity_explorer(graph_builder)

    with tab3:
        render_graph_visualization(graph_builder)

    with tab4:
        render_relationship_browser(graph_builder)


def render_graph_build_ui():
    """UI for building knowledge graph"""
    st.markdown("### 🛠️ Build Knowledge Graph")

    st.info("📝 Knowledge graph not found. Build it to enable graph-based features.")

    st.markdown("""
    **What the knowledge graph provides:**
    - Entity extraction (NIST controls, concepts, publications)
    - Relationship discovery (co-occurrence, hierarchies)
    - Graph-enhanced RAG queries
    - Multi-hop reasoning paths
    """)

    with st.expander("⚙️ Build Settings", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            sample_size = st.number_input(
                "Sample Size",
                min_value=100,
                max_value=100000,
                value=10000,
                step=1000,
                help="Number of documents to process (lower = faster)"
            )

        with col2:
            enable_cooccurrence = st.checkbox(
                "Co-occurrence Edges",
                value=True,
                help="Build edges between entities appearing together"
            )

    if st.button("🚀 Build Knowledge Graph", type="primary"):
        st.info("⚠️ This may take 2-5 minutes depending on sample size")
        st.code(f"""python src/graph/build_knowledge_graph.py \\
    --persist artifacts/index \\
    --collection studykit \\
    --output artifacts/graph/knowledge_graph.pkl \\
    --sample {sample_size}""", language="bash")

        st.markdown("After building, refresh this page to explore the graph.")


def render_graph_overview(graph_builder: KnowledgeGraphBuilder):
    """Render graph statistics and overview"""
    st.markdown("### 📊 Graph Statistics")

    try:
        stats = graph_builder.get_statistics()

        # Main metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Nodes", f"{stats['num_nodes']:,}")

        with col2:
            st.metric("Edges", f"{stats['num_edges']:,}")

        with col3:
            st.metric("Density", f"{stats['density']:.4f}")

        with col4:
            st.metric("Avg Degree", f"{stats['avg_degree']:.2f}")

        st.markdown("---")

        # Entity breakdown
        st.markdown("### 🏷️ Entity Types")

        entity_stats = stats.get('entity_statistics', {})
        if 'by_type' in entity_stats:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Entity Count by Type:**")
                for entity_type, count in entity_stats['by_type'].items():
                    st.markdown(f"- **{entity_type}**: {count:,}")

            with col2:
                st.markdown("**Total Unique Entities:**")
                st.markdown(f"**{entity_stats.get('total_entities', 0):,}**")

        st.markdown("---")

        # Top entities
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔝 Top NIST Controls")
            if 'top_controls' in entity_stats:
                for control in entity_stats['top_controls'][:10]:
                    st.markdown(f"- **{control['id']}**: {control['frequency']} mentions")

        with col2:
            st.markdown("### 💡 Top Concepts")
            if 'top_concepts' in entity_stats:
                for concept in entity_stats['top_concepts'][:10]:
                    st.markdown(f"- **{concept['id']}**: {concept['frequency']} mentions")

        st.markdown("---")

        # Central entities
        st.markdown("### ⭐ Most Central Entities (PageRank)")
        if 'top_central_entities' in stats:
            for entity_id, score in stats['top_central_entities'][:15]:
                st.markdown(f"- **{entity_id}**: {score:.4f}")

    except Exception as e:
        st.error(f"❌ Failed to load statistics: {e}")


def render_entity_explorer(graph_builder: KnowledgeGraphBuilder):
    """Interactive entity search and exploration"""
    st.markdown("### 🔍 Entity Explorer")

    # Search box
    search = st.text_input(
        "Search entities:",
        placeholder="e.g., AC-2, MFA, encryption"
    )

    if search:
        # Find matching entities
        matching = []
        search_lower = search.lower()

        for entity_id, entity in graph_builder.entity_extractor.entities.items():
            if (search_lower in entity_id.lower() or
                search_lower in entity.name.lower()):
                matching.append(entity)

        if matching:
            st.success(f"✓ Found {len(matching)} matching entities")

            # Display results
            for entity in matching[:20]:  # Limit to 20
                with st.expander(f"{entity.entity_type.upper()}: {entity.name}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**ID:** {entity.entity_id}")
                        st.markdown(f"**Type:** {entity.entity_type}")
                        st.markdown(f"**Frequency:** {entity.frequency}")

                    with col2:
                        if entity.properties:
                            st.markdown("**Properties:**")
                            for key, value in entity.properties.items():
                                st.markdown(f"- {key}: {value}")

                    # Neighbors
                    neighbors = graph_builder.get_neighbors(entity.entity_id, max_depth=1)
                    if neighbors:
                        st.markdown(f"**Connected Entities ({len(neighbors)}):**")
                        st.markdown(", ".join(neighbors[:10]))
                        if len(neighbors) > 10:
                            st.caption(f"... and {len(neighbors) - 10} more")

            if len(matching) > 20:
                st.info(f"Showing 20 of {len(matching)} results")
        else:
            st.warning("⚠️ No matching entities found")

    else:
        # Show entity type browser
        st.markdown("**Browse by type:**")

        entity_type = st.selectbox(
            "Select entity type",
            ["control", "concept", "publication", "control_family"]
        )

        entities = graph_builder.entity_extractor.get_top_entities(
            entity_type=entity_type,
            top_k=50
        )

        if entities:
            st.success(f"✓ {len(entities)} {entity_type} entities")

            for entity in entities:
                st.markdown(f"- **{entity.entity_id}** ({entity.frequency} mentions)")
        else:
            st.info(f"No {entity_type} entities found")


def render_graph_visualization(graph_builder: KnowledgeGraphBuilder):
    """Interactive graph visualization with Plotly"""
    st.markdown("### 🗺️ Graph Visualization")

    st.info("💡 Select entities to visualize their subgraph")

    # Entity selection
    all_entities = list(graph_builder.entity_extractor.entities.keys())

    selected = st.multiselect(
        "Select entities (up to 10)",
        all_entities[:100],  # Limit dropdown size
        default=all_entities[:5] if len(all_entities) >= 5 else all_entities
    )

    if not selected:
        st.warning("⚠️ Select at least one entity to visualize")
        return

    if len(selected) > 10:
        st.warning("⚠️ Too many entities selected. Limiting to first 10.")
        selected = selected[:10]

    # Extract subgraph
    include_neighbors = st.checkbox("Include neighbors", value=True)

    try:
        subgraph = graph_builder.get_entity_subgraph(selected, include_neighbors)

        st.success(f"✓ Subgraph: {len(subgraph.nodes)} nodes, {len(subgraph.edges)} edges")

        # Visualize with Plotly
        fig = create_plotly_graph(subgraph, selected)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Visualization failed: {e}")


def create_plotly_graph(graph: nx.MultiDiGraph, highlighted: List[str]) -> go.Figure:
    """Create Plotly graph visualization

    Args:
        graph: NetworkX graph
        highlighted: Entity IDs to highlight

    Returns:
        Plotly figure
    """
    # Layout
    pos = nx.spring_layout(graph, k=0.5, iterations=50)

    # Edges
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += (x0, x1, None)
        edge_trace['y'] += (y0, y1, None)

    # Nodes
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=10,
            color=[],
            colorbar=dict(
                thickness=15,
                title='Degree',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)
        ),
        textposition="top center"
    )

    for node in graph.nodes():
        x, y = pos[node]
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)

        # Color by degree
        degree = graph.degree(node)
        node_trace['marker']['color'] += (degree,)

        # Highlight selected nodes
        if node in highlighted:
            node_trace['marker']['line']['color'] = '#FF0000'
            node_trace['text'] += (f"<b>{node}</b>",)
        else:
            node_trace['marker']['line']['color'] = '#888'
            node_trace['text'] += (node,)

    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Knowledge Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
    )

    return fig


def render_relationship_browser(graph_builder: KnowledgeGraphBuilder):
    """Browse and analyze relationships"""
    st.markdown("### 🔗 Relationship Browser")

    st.markdown("**Find paths between entities:**")

    col1, col2 = st.columns(2)

    all_entities = list(graph_builder.entity_extractor.entities.keys())

    with col1:
        source = st.selectbox("Source entity", all_entities[:100], key='source')

    with col2:
        target = st.selectbox("Target entity", all_entities[:100], key='target')

    if st.button("🔍 Find Path"):
        if source == target:
            st.warning("⚠️ Source and target are the same")
            return

        path = graph_builder.get_shortest_path(source, target)

        if path:
            st.success(f"✓ Found path with {len(path)} hops")

            st.markdown("**Path:**")
            for i, entity_id in enumerate(path):
                if i < len(path) - 1:
                    st.markdown(f"{i+1}. **{entity_id}** →")
                else:
                    st.markdown(f"{i+1}. **{entity_id}**")
        else:
            st.warning("⚠️ No path found between these entities")

    st.markdown("---")

    # Relationship type analysis
    st.markdown("### 📈 Relationship Type Distribution")

    try:
        edge_types = {}
        for u, v, key in graph_builder.graph.edges(keys=True):
            edge_types[key] = edge_types.get(key, 0) + 1

        if edge_types:
            for rel_type, count in sorted(edge_types.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"- **{rel_type}**: {count:,} edges")
        else:
            st.info("No relationships found")

    except Exception as e:
        st.error(f"❌ Failed to analyze relationships: {e}")
