#!/usr/bin/env python3
"""
Performance Monitoring Script

Checks system performance and provides optimization recommendations.
"""

import time
import psutil
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint

console = Console()


def check_system_resources():
    """Check system resource usage"""
    console.rule("[bold blue]System Resources")

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()

    # Memory
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024**3)
    memory_used_gb = memory.used / (1024**3)
    memory_percent = memory.percent

    # Disk
    disk = psutil.disk_usage('/')
    disk_gb = disk.total / (1024**3)
    disk_used_gb = disk.used / (1024**3)
    disk_percent = disk.percent

    table = Table(title="Resource Usage")
    table.add_column("Resource", style="cyan")
    table.add_column("Usage", style="magenta")
    table.add_column("Status", style="green")

    # CPU
    cpu_status = "✅ Good" if cpu_percent < 70 else "⚠️ High" if cpu_percent < 90 else "❌ Critical"
    table.add_row("CPU", f"{cpu_percent:.1f}% ({cpu_count} cores)", cpu_status)

    # Memory
    mem_status = "✅ Good" if memory_percent < 70 else "⚠️ High" if memory_percent < 85 else "❌ Critical"
    table.add_row("Memory", f"{memory_used_gb:.1f}/{memory_gb:.1f} GB ({memory_percent:.1f}%)", mem_status)

    # Disk
    disk_status = "✅ Good" if disk_percent < 80 else "⚠️ High" if disk_percent < 90 else "❌ Critical"
    table.add_row("Disk", f"{disk_used_gb:.1f}/{disk_gb:.1f} GB ({disk_percent:.1f}%)", disk_status)

    console.print(table)
    console.print()

    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'disk_percent': disk_percent
    }


def check_file_sizes():
    """Check sizes of key artifacts"""
    console.rule("[bold blue]Artifact Sizes")

    artifacts = [
        ("ChromaDB Index", "artifacts/index"),
        ("OpenAI Parquet", "artifacts/openai.parquet"),
        ("Docs Parquet", "artifacts/docs.parquet"),
        ("Knowledge Graph", "artifacts/graph/knowledge_graph.pkl"),
        ("Cluster Labels", "artifacts/cluster_labels.json"),
        ("Topic Visualization", "artifacts/topic_clusters_2d.png")
    ]

    table = Table(title="File Sizes")
    table.add_column("Artifact", style="cyan")
    table.add_column("Size", style="magenta")
    table.add_column("Status", style="green")

    total_size = 0

    for name, path in artifacts:
        path_obj = Path(path)

        if path_obj.exists():
            if path_obj.is_file():
                size = path_obj.stat().st_size
            else:
                # Directory - sum all files
                size = sum(f.stat().st_size for f in path_obj.rglob('*') if f.is_file())

            size_mb = size / (1024**2)
            total_size += size

            status = "✅ Present"
            table.add_row(name, f"{size_mb:.1f} MB", status)
        else:
            table.add_row(name, "Not found", "⚠️ Missing")

    console.print(table)

    total_mb = total_size / (1024**2)
    total_gb = total_size / (1024**3)

    if total_gb < 1:
        console.print(f"\n[bold]Total Size:[/bold] {total_mb:.1f} MB")
    else:
        console.print(f"\n[bold]Total Size:[/bold] {total_gb:.2f} GB ({total_mb:.0f} MB)")

    console.print()


def check_import_times():
    """Check import performance for key modules"""
    console.rule("[bold blue]Module Import Performance")

    modules = [
        "agents",
        "graph",
        "chromadb",
        "sentence_transformers",
        "streamlit",
        "plotly"
    ]

    table = Table(title="Import Times")
    table.add_column("Module", style="cyan")
    table.add_column("Time", style="magenta")
    table.add_column("Status", style="green")

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    for module_name in modules:
        try:
            start = time.time()
            __import__(module_name)
            elapsed = time.time() - start

            status = "✅ Fast" if elapsed < 1.0 else "⚠️ Slow" if elapsed < 3.0 else "❌ Very Slow"
            table.add_row(module_name, f"{elapsed:.3f}s", status)

        except ImportError:
            table.add_row(module_name, "N/A", "⚠️ Not installed")

    console.print(table)
    console.print()


def check_agent_performance():
    """Check agent execution performance"""
    console.rule("[bold blue]Agent Performance")

    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from agents import ComplianceAgent, ResearchAgent, SynthesisAgent

    agents = [
        ("ComplianceAgent", ComplianceAgent),
        ("ResearchAgent", ResearchAgent),
        ("SynthesisAgent", SynthesisAgent)
    ]

    table = Table(title="Agent Initialization Times")
    table.add_column("Agent", style="cyan")
    table.add_column("Init Time", style="magenta")
    table.add_column("Status", style="green")

    for agent_name, agent_class in agents:
        try:
            start = time.time()
            agent = agent_class()
            elapsed = time.time() - start

            status = "✅ Fast" if elapsed < 2.0 else "⚠️ Slow" if elapsed < 5.0 else "❌ Very Slow"
            table.add_row(agent_name, f"{elapsed:.3f}s", status)

        except Exception as e:
            table.add_row(agent_name, f"Error: {str(e)[:30]}", "❌ Failed")

    console.print(table)
    console.print()


def generate_recommendations(resources):
    """Generate performance recommendations"""
    console.rule("[bold blue]Optimization Recommendations")

    recommendations = []

    # CPU recommendations
    if resources['cpu_percent'] > 70:
        recommendations.append({
            'priority': 'High',
            'issue': 'High CPU usage',
            'recommendation': 'Close unnecessary applications or reduce agent parallelism'
        })

    # Memory recommendations
    if resources['memory_percent'] > 80:
        recommendations.append({
            'priority': 'High',
            'issue': 'High memory usage',
            'recommendation': 'Restart Streamlit or reduce batch sizes in agents'
        })
    elif resources['memory_percent'] > 60:
        recommendations.append({
            'priority': 'Medium',
            'issue': 'Moderate memory usage',
            'recommendation': 'Consider clearing cached embeddings or model weights'
        })

    # Disk recommendations
    if resources['disk_percent'] > 85:
        recommendations.append({
            'priority': 'High',
            'issue': 'Low disk space',
            'recommendation': 'Clean up old artifacts or temporary files'
        })

    # General recommendations
    recommendations.append({
        'priority': 'Low',
        'issue': 'Optimization opportunity',
        'recommendation': 'Use smaller sample sizes during development (--sample flag)'
    })

    recommendations.append({
        'priority': 'Low',
        'issue': 'Performance tip',
        'recommendation': 'Cache model weights to speed up agent initialization'
    })

    if not recommendations:
        console.print("[green]✅ No performance issues detected![/green]\n")
        return

    table = Table(title="Recommendations")
    table.add_column("Priority", style="cyan")
    table.add_column("Issue", style="yellow")
    table.add_column("Recommendation", style="green")

    for rec in recommendations:
        priority = rec['priority']
        color = "red" if priority == "High" else "yellow" if priority == "Medium" else "blue"

        table.add_row(
            f"[{color}]{priority}[/{color}]",
            rec['issue'],
            rec['recommendation']
        )

    console.print(table)
    console.print()


def main():
    console.print("\n[bold cyan]GPTBuddyAI Performance Check[/bold cyan]\n")

    # Run checks
    resources = check_system_resources()
    check_file_sizes()
    check_import_times()
    check_agent_performance()
    generate_recommendations(resources)

    console.rule("[bold green]Performance Check Complete")
    console.print()


if __name__ == '__main__':
    main()
