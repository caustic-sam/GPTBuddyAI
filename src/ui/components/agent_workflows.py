"""
Agent Workflows UI Component

Interactive interface for autonomous agent workflows.
"""

import streamlit as st
import sys
from pathlib import Path
import json
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from agents import (
    AgentCoordinator,
    ComplianceAgent,
    ResearchAgent,
    SynthesisAgent
)
from agents.coordinator import WorkflowStep

# Import visualization components
sys.path.append(str(Path(__file__).parent))
from compliance_viz import render_compliance_dashboard


def render_agent_workflows():
    """Main agent workflows component"""

    st.markdown("## 🤖 Agent Workflows")
    st.markdown("Autonomous multi-agent workflows for complex knowledge tasks")

    st.markdown("---")

    # Workflow selection
    workflow_type = st.selectbox(
        "Select Workflow",
        [
            "Compliance Gap Analysis",
            "Research Synthesis",
            "Custom Workflow (Coming Soon)"
        ]
    )

    st.markdown("---")

    if "Compliance" in workflow_type:
        render_compliance_workflow()
    elif "Research" in workflow_type:
        render_research_workflow()
    else:
        render_custom_workflow()


def render_compliance_workflow():
    """Compliance gap analysis workflow UI"""

    st.markdown("### 📊 NIST Compliance Gap Analysis")

    st.markdown("""
    This workflow automatically:
    1. 🔍 Extracts all NIST controls from your knowledge base
    2. 🔎 Searches for implementation evidence in conversations
    3. 📈 Classifies controls (implemented/partial/gaps)
    4. 📋 Generates prioritized remediation recommendations
    """)

    # Settings
    with st.expander("⚙️ Workflow Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            framework = st.selectbox(
                "Framework",
                ["NIST-800-53", "NIST-800-171", "ISO-27001"]
            )

        with col2:
            threshold = st.slider(
                "Evidence Threshold",
                min_value=1,
                max_value=5,
                value=2,
                help="Minimum passages to count as implemented"
            )

    # Run workflow button
    run_workflow = st.button("🚀 Run Compliance Analysis", type="primary")

    if run_workflow:
        run_compliance_analysis(framework, threshold)


def run_compliance_analysis(framework: str, threshold: int):
    """Execute compliance gap analysis workflow"""

    # Initialize coordinator
    coordinator = AgentCoordinator()

    # Register agents
    compliance_agent = ComplianceAgent()
    coordinator.register_agent(compliance_agent)

    # Create workflow
    steps = [
        WorkflowStep(
            agent_name="ComplianceAgent",
            task={
                'framework': framework,
                'min_evidence_threshold': threshold
            }
        )
    ]

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Initializing agents...")
    progress_bar.progress(10)
    time.sleep(0.5)

    try:
        # Execute workflow
        status_text.text("🤖 Running compliance analysis...")
        progress_bar.progress(30)

        results = coordinator.execute_workflow(
            workflow_name="Compliance Gap Analysis",
            steps=steps
        )

        progress_bar.progress(70)
        status_text.text("📊 Processing results...")
        time.sleep(0.5)

        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")

        # Display results
        if results:
            display_compliance_results(results)
        else:
            st.error("❌ Workflow failed - no results returned")

    except Exception as e:
        st.error(f"❌ Workflow execution failed: {e}")
        st.info("💡 Check that the knowledge base is indexed and accessible")


def display_compliance_results(results: dict):
    """Display compliance analysis results"""

    st.markdown("---")
    st.markdown("### 📈 Analysis Results")

    # Get the compliance agent result
    agent_result = None
    for key, result in results.items():
        if result.agent_name == "ComplianceAgent":
            agent_result = result
            break

    if not agent_result or agent_result.status != "success":
        st.error("❌ Analysis failed")
        if agent_result and agent_result.errors:
            for error in agent_result.errors:
                st.error(f"Error: {error}")
        return

    data = agent_result.data
    summary = data.get('summary', {})
    classification = data.get('classification', {})
    recommendations = data.get('recommendations', [])

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Controls",
            summary.get('implemented', 0) + summary.get('partial', 0) + summary.get('gaps', 0)
        )

    with col2:
        st.metric(
            "✅ Implemented",
            summary.get('implemented', 0),
            delta=None,
            delta_color="normal"
        )

    with col3:
        st.metric(
            "⚠️ Partial",
            summary.get('partial', 0),
            delta=None
        )

    with col4:
        st.metric(
            "❌ Gaps",
            summary.get('gaps', 0),
            delta=f"-{summary.get('coverage_percentage', 0):.1f}% coverage"
        )

    st.markdown("---")

    # Render compliance visualization dashboard
    render_compliance_dashboard(summary, classification, recommendations)

    st.markdown("---")

    # Coverage breakdown
    st.markdown("### 📊 Coverage Breakdown")

    # Show control lists
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander(f"✅ Implemented ({len(classification.get('implemented', []))})"):
            for control in sorted(classification.get('implemented', [])[:20]):  # Show first 20
                st.markdown(f"- {control}")
            if len(classification.get('implemented', [])) > 20:
                st.info(f"... and {len(classification.get('implemented', [])) - 20} more")

    with col2:
        with st.expander(f"⚠️ Partial ({len(classification.get('partial', []))})"):
            for control in sorted(classification.get('partial', [])[:20]):
                st.markdown(f"- {control}")
            if len(classification.get('partial', [])) > 20:
                st.info(f"... and {len(classification.get('partial', [])) - 20} more")

    with col3:
        with st.expander(f"❌ Gaps ({len(classification.get('gaps', []))})"):
            for control in sorted(classification.get('gaps', [])[:20]):
                st.markdown(f"- {control}")
            if len(classification.get('gaps', [])) > 20:
                st.info(f"... and {len(classification.get('gaps', [])) - 20} more")

    st.markdown("---")

    # Recommendations
    st.markdown("### 🎯 Remediation Recommendations")

    if recommendations:
        # Filter by priority
        priority_filter = st.multiselect(
            "Filter by priority",
            ["High", "Medium", "Low"],
            default=["High", "Medium"]
        )

        filtered_recs = [
            r for r in recommendations
            if r.get('priority') in priority_filter
        ]

        # Display top 10
        for i, rec in enumerate(filtered_recs[:10], 1):
            priority_color = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(rec.get('priority', 'Low'), '⚪')

            st.markdown(
                f"{priority_color} **{i}. {rec.get('control_id')}** - "
                f"{rec.get('action')}"
            )
            st.caption(f"Reason: {rec.get('reason')}")

        if len(filtered_recs) > 10:
            st.info(f"Showing 10 of {len(filtered_recs)} recommendations")
    else:
        st.success("✨ No recommendations - excellent coverage!")

    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Results")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📄 Export to JSON"):
            json_data = json.dumps(data, indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="compliance_analysis.json",
                mime="application/json"
            )

    with col2:
        if st.button("📑 Generate PDF Report (Coming Soon)"):
            st.info("PDF export will be available in Day 4 deliverables")


def render_research_workflow():
    """Research synthesis workflow UI"""
    st.markdown("### 🔬 Autonomous Research Synthesis")

    st.markdown("""
    This workflow automatically:
    1. 🔍 Performs multi-hop iterative querying
    2. 📊 Extracts key concepts and expands queries
    3. 🎯 Clusters findings into themes
    4. 📝 Generates structured markdown reports with citations
    """)

    # Settings
    with st.expander("⚙️ Research Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            research_topic = st.text_input(
                "Research Topic",
                placeholder="e.g., Multi-factor authentication in federal systems",
                help="Topic or question to research"
            )

            depth = st.slider(
                "Search Depth (hops)",
                min_value=1,
                max_value=5,
                value=3,
                help="Number of iterative query expansions"
            )

        with col2:
            max_sources = st.slider(
                "Sources per Hop",
                min_value=5,
                max_value=20,
                value=10,
                help="Maximum documents to retrieve per query"
            )

            cluster_themes = st.checkbox(
                "Cluster Themes",
                value=True,
                help="Group findings into themes using K-means clustering"
            )

    # Run workflow button
    run_research = st.button("🚀 Run Research Synthesis", type="primary")

    if run_research:
        if not research_topic:
            st.error("❌ Please enter a research topic")
        else:
            run_research_synthesis(research_topic, depth, max_sources, cluster_themes)


def run_research_synthesis(topic: str, depth: int, max_sources: int, cluster_themes: bool):
    """Execute research synthesis workflow"""

    # Initialize coordinator and agents
    coordinator = AgentCoordinator()
    research_agent = ResearchAgent()
    synthesis_agent = SynthesisAgent()

    coordinator.register_agent(research_agent)
    coordinator.register_agent(synthesis_agent)

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Initializing research agents...")
    progress_bar.progress(10)
    time.sleep(0.5)

    try:
        # Step 1: Research
        status_text.text(f"🔬 Researching: {topic}...")
        progress_bar.progress(20)

        research_steps = [
            WorkflowStep(
                agent_name="ResearchAgent",
                task={
                    'topic': topic,
                    'depth': depth,
                    'max_sources': max_sources,
                    'cluster_themes': cluster_themes
                }
            )
        ]

        research_results = coordinator.execute_workflow(
            workflow_name="Research Phase",
            steps=research_steps
        )

        progress_bar.progress(60)

        # Get research data
        research_result = None
        for key, result in research_results.items():
            if result.agent_name == "ResearchAgent":
                research_result = result
                break

        if not research_result or research_result.status != "success":
            st.error("❌ Research failed")
            if research_result and research_result.errors:
                for error in research_result.errors:
                    st.error(f"Error: {error}")
            return

        # Step 2: Synthesis
        status_text.text("📝 Generating report...")
        progress_bar.progress(70)

        synthesis_steps = [
            WorkflowStep(
                agent_name="SynthesisAgent",
                task={
                    'research_data': research_result.data,
                    'report_title': f"Research Report: {topic}",
                    'format': 'markdown',
                    'include_executive_summary': True,
                    'output_path': f"artifacts/reports/research_{int(time.time())}.md"
                }
            )
        ]

        synthesis_results = coordinator.execute_workflow(
            workflow_name="Synthesis Phase",
            steps=synthesis_steps
        )

        progress_bar.progress(90)

        # Get synthesis data
        synthesis_result = None
        for key, result in synthesis_results.items():
            if result.agent_name == "SynthesisAgent":
                synthesis_result = result
                break

        progress_bar.progress(100)
        status_text.text("✅ Research synthesis complete!")

        # Display results
        if synthesis_result and synthesis_result.status == "success":
            display_research_results(research_result, synthesis_result)
        else:
            st.error("❌ Synthesis failed")
            if synthesis_result and synthesis_result.errors:
                for error in synthesis_result.errors:
                    st.error(f"Error: {error}")

    except Exception as e:
        st.error(f"❌ Workflow execution failed: {e}")
        st.info("💡 Check that the knowledge base is indexed and accessible")


def display_research_results(research_result, synthesis_result):
    """Display research synthesis results"""

    st.markdown("---")
    st.markdown("### 📊 Research Results")

    research_data = research_result.data
    synthesis_data = synthesis_result.data

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Sources",
            research_data.get('total_sources', 0)
        )

    with col2:
        st.metric(
            "Search Depth",
            f"{research_data.get('depth', 0)} hops"
        )

    with col3:
        st.metric(
            "Themes Identified",
            len(research_data.get('themes', []))
        )

    with col4:
        execution_time = research_result.execution_time + synthesis_result.execution_time
        st.metric(
            "Execution Time",
            f"{execution_time:.1f}s"
        )

    st.markdown("---")

    # Query evolution
    st.markdown("### 🔍 Query Evolution")
    query_history = research_data.get('query_history', [])

    for i, query in enumerate(query_history, 1):
        st.markdown(f"**Hop {i}:** {query}")

    st.markdown("---")

    # Themes
    themes = research_data.get('themes', [])
    if themes:
        st.markdown("### 🎯 Discovered Themes")

        for theme in themes:
            with st.expander(f"Theme {theme['theme_id'] + 1}: {theme['theme_name'][:60]}..."):
                st.markdown(f"**Documents:** {theme['document_count']}")

                rep_doc = theme.get('representative_doc', {})
                if rep_doc:
                    st.markdown("**Representative Passage:**")
                    st.markdown(f"> {rep_doc.get('text', 'N/A')[:300]}...")
                    st.caption(f"Source: {rep_doc.get('source', 'Unknown')}, Page {rep_doc.get('page', 'N/A')}")

    st.markdown("---")

    # Generated report
    st.markdown("### 📝 Generated Report")

    report_content = synthesis_data.get('content', '')
    st.markdown(report_content[:2000])  # Preview first 2000 chars

    if len(report_content) > 2000:
        st.info(f"Report truncated for display. Full report: {len(report_content):,} characters")

    # Download options
    st.markdown("---")
    st.markdown("### 📥 Export Report")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="📄 Download Markdown",
            data=report_content,
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown"
        )

    with col2:
        json_data = json.dumps(research_data, indent=2, default=str)
        st.download_button(
            label="📊 Download Research Data (JSON)",
            data=json_data,
            file_name=f"research_data_{int(time.time())}.json",
            mime="application/json"
        )

    # Show saved path
    saved_path = synthesis_data.get('saved_path')
    if saved_path:
        st.success(f"✅ Report saved to: `{saved_path}`")


def render_custom_workflow():
    """Custom workflow builder UI (stub)"""
    st.markdown("### 🛠️ Custom Workflow Builder")
    st.info("🚧 Custom workflow builder coming in Day 3!")

    st.markdown("""
    **Planned features:**
    - Drag-and-drop agent composer
    - Dependency graph visualization
    - Custom task parameters
    - Workflow templates
    """)
