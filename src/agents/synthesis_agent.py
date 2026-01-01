"""
Synthesis Agent

Generates structured reports from research findings with:
- Markdown report generation
- Citation management
- PDF export (optional)
- Executive summaries
"""

import time
import logging
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class SynthesisAgent(BaseAgent):
    """
    Synthesizes research findings into structured reports.

    Capabilities:
    1. Structured markdown report generation
    2. Citation tracking and formatting
    3. Executive summary creation
    4. Export to multiple formats (MD, JSON, PDF)
    """

    def __init__(self):
        super().__init__(
            name="SynthesisAgent",
            description="Report generation and synthesis"
        )

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute synthesis task.

        Args:
            task: Must contain:
                - research_data: Research findings from ResearchAgent
                - report_title: Title for the report
                - format: Output format ('markdown', 'json', 'pdf')
                - include_executive_summary: Boolean (default True)
                - output_path: Optional path to save report

        Returns:
            AgentResult with synthesized report
        """
        start_time = time.time()
        result = AgentResult(agent_name=self.name, status="success")

        # Extract parameters
        research_data = task.get('research_data', {})
        report_title = task.get('report_title', 'Research Report')
        output_format = task.get('format', 'markdown')
        include_exec_summary = task.get('include_executive_summary', True)
        output_path = task.get('output_path', None)

        if not research_data:
            result.status = "failure"
            result.errors.append("No research data provided")
            return result

        try:
            # Step 1: Create executive summary
            exec_summary = ""
            if include_exec_summary:
                self.log_step("Creating executive summary", "Analyzing research data")
                exec_summary = self._create_executive_summary(research_data)

            # Step 2: Generate report based on format
            if output_format == 'markdown':
                self.log_step("Generating markdown report", f"Title: {report_title}")
                report_content = self._generate_markdown_report(
                    report_title,
                    research_data,
                    exec_summary
                )

            elif output_format == 'json':
                self.log_step("Generating JSON report", f"Title: {report_title}")
                report_content = self._generate_json_report(
                    report_title,
                    research_data,
                    exec_summary
                )

            elif output_format == 'pdf':
                result.warnings.append("PDF export requires additional dependencies - generating markdown instead")
                report_content = self._generate_markdown_report(
                    report_title,
                    research_data,
                    exec_summary
                )
            else:
                result.status = "failure"
                result.errors.append(f"Unsupported format: {output_format}")
                return result

            # Step 3: Save report (optional)
            saved_path = None
            if output_path:
                self.log_step("Saving report", f"Path: {output_path}")
                saved_path = self._save_report(report_content, output_path, output_format)

            # Build result
            result.data = {
                'report_title': report_title,
                'format': output_format,
                'content': report_content,
                'executive_summary': exec_summary,
                'saved_path': str(saved_path) if saved_path else None,
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'source_count': research_data.get('total_sources', 0),
                    'theme_count': len(research_data.get('themes', []))
                }
            }

            result.steps = self.steps

        except Exception as e:
            logger.exception(f"Synthesis failed: {e}")
            result.status = "failure"
            result.errors.append(str(e))

        result.execution_time = time.time() - start_time
        return result

    def _create_executive_summary(self, research_data: Dict[str, Any]) -> str:
        """Create executive summary from research data

        Args:
            research_data: Research findings

        Returns:
            Executive summary string
        """
        topic = research_data.get('topic', 'Unknown Topic')
        total_sources = research_data.get('total_sources', 0)
        themes = research_data.get('themes', [])

        summary = f"## Executive Summary\n\n"
        summary += f"This report presents findings from an automated research synthesis on **{topic}**. "
        summary += f"The analysis examined **{total_sources} sources** across the knowledge base.\n\n"

        if themes:
            summary += f"### Key Findings\n\n"
            summary += f"{len(themes)} major themes were identified:\n\n"

            for i, theme in enumerate(themes[:5], 1):  # Top 5 themes
                theme_name = theme.get('theme_name', f'Theme {i}')
                doc_count = theme.get('document_count', 0)
                summary += f"{i}. **{theme_name}** ({doc_count} documents)\n"

            summary += "\n"

        return summary

    def _generate_markdown_report(
        self,
        title: str,
        research_data: Dict[str, Any],
        exec_summary: str
    ) -> str:
        """Generate markdown formatted report

        Args:
            title: Report title
            research_data: Research findings
            exec_summary: Executive summary

        Returns:
            Markdown report string
        """
        md = f"# {title}\n\n"
        md += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        md += "---\n\n"

        # Executive summary
        if exec_summary:
            md += exec_summary
            md += "---\n\n"

        # Research topic
        topic = research_data.get('topic', 'Unknown')
        md += f"## Research Topic\n\n{topic}\n\n"

        # Methodology
        depth = research_data.get('depth', 'N/A')
        total_sources = research_data.get('total_sources', 0)
        query_history = research_data.get('query_history', [])

        md += "## Methodology\n\n"
        md += f"- **Search Depth**: {depth} hops\n"
        md += f"- **Total Sources**: {total_sources}\n"
        md += f"- **Query Evolution**: {len(query_history)} iterations\n\n"

        if query_history:
            md += "**Query Progression:**\n\n"
            for i, query in enumerate(query_history, 1):
                md += f"{i}. {query}\n"
            md += "\n"

        # Themes
        themes = research_data.get('themes', [])
        if themes:
            md += "## Key Themes\n\n"

            for theme in themes:
                theme_id = theme.get('theme_id', 0)
                theme_name = theme.get('theme_name', 'Unnamed Theme')
                doc_count = theme.get('document_count', 0)

                md += f"### Theme {theme_id + 1}: {theme_name}\n\n"
                md += f"*{doc_count} documents*\n\n"

                # Representative document
                rep_doc = theme.get('representative_doc', {})
                if rep_doc:
                    md += f"**Representative Passage:**\n\n"
                    md += f"> {rep_doc.get('text', 'N/A')[:300]}...\n\n"
                    md += f"*Source: {rep_doc.get('source', 'Unknown')}, Page {rep_doc.get('page', 'N/A')}*\n\n"

                # Top documents in theme
                theme_docs = theme.get('documents', [])
                if theme_docs:
                    md += f"**Related Documents ({len(theme_docs)}):**\n\n"
                    for i, doc in enumerate(theme_docs, 1):
                        source = doc.get('source', 'Unknown')
                        page = doc.get('page', 'N/A')
                        md += f"{i}. {source} (page {page})\n"
                    md += "\n"

            md += "---\n\n"

        # Source breakdown
        md += "## Sources\n\n"

        documents = research_data.get('documents', [])
        if documents:
            # Group by source
            sources = {}
            for doc in documents:
                source = doc.get('source', 'Unknown')
                if source not in sources:
                    sources[source] = []
                sources[source].append(doc)

            md += f"**Total Unique Sources**: {len(sources)}\n\n"

            for source, docs in sorted(sources.items(), key=lambda x: len(x[1]), reverse=True):
                md += f"- **{source}**: {len(docs)} passages\n"

            md += "\n---\n\n"

        # Full citation list
        md += "## Citations\n\n"

        if documents:
            for i, doc in enumerate(documents, 1):
                source = doc.get('source', 'Unknown')
                page = doc.get('page', 'N/A')
                md += f"[{i}] {source}, page {page}\n"
        else:
            md += "*No citations available*\n"

        md += "\n"

        return md

    def _generate_json_report(
        self,
        title: str,
        research_data: Dict[str, Any],
        exec_summary: str
    ) -> str:
        """Generate JSON formatted report

        Args:
            title: Report title
            research_data: Research findings
            exec_summary: Executive summary

        Returns:
            JSON report string
        """
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'executive_summary': exec_summary,
            'research_data': research_data
        }

        return json.dumps(report, indent=2, default=str)

    def _save_report(
        self,
        content: str,
        output_path: str | Path,
        format: str
    ) -> Path:
        """Save report to disk

        Args:
            content: Report content
            output_path: Output path
            format: Report format

        Returns:
            Saved file path
        """
        output_path = Path(output_path)

        # Ensure correct extension
        if format == 'markdown' and not output_path.suffix == '.md':
            output_path = output_path.with_suffix('.md')
        elif format == 'json' and not output_path.suffix == '.json':
            output_path = output_path.with_suffix('.json')

        # Create directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Report saved to {output_path}")
        return output_path
