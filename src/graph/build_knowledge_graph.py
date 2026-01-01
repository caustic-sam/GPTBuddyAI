#!/usr/bin/env python3
"""
Build Knowledge Graph Script

Constructs knowledge graph from ChromaDB collection:
1. Extract entities (NIST controls, concepts, publications)
2. Build co-occurrence and hierarchical relationships
3. Save graph for graph-enhanced RAG

Usage:
    python src/graph/build_knowledge_graph.py \\
        --persist artifacts/index \\
        --collection studykit \\
        --output artifacts/graph/knowledge_graph.pkl \\
        --sample 10000
"""

import argparse
import logging
from pathlib import Path
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

from graph_rag import GraphEnhancedRAG

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()


def build_graph(
    persist_dir: str,
    collection: str,
    output_path: str,
    sample_size: int = None,
    enable_cooccurrence: bool = True,
    enable_hierarchy: bool = True
):
    """Build knowledge graph from ChromaDB collection

    Args:
        persist_dir: ChromaDB persistence directory
        collection: Collection name
        output_path: Output path for graph
        sample_size: Limit documents (None = all)
        enable_cooccurrence: Build co-occurrence edges
        enable_hierarchy: Build hierarchical edges
    """
    console.rule("[bold blue]Building Knowledge Graph")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:

        # Initialize graph-enhanced RAG
        task = progress.add_task("[cyan]Initializing...", total=None)
        graph_rag = GraphEnhancedRAG(
            chroma_persist_dir=persist_dir,
            collection_name=collection
        )
        progress.update(task, description="[green]✓ Initialized")

        # Build graph
        task = progress.add_task(
            f"[cyan]Building graph (sample_size={sample_size or 'all'})...",
            total=None
        )
        graph = graph_rag.build_graph_from_collection(
            sample_size=sample_size,
            enable_cooccurrence=enable_cooccurrence,
            enable_hierarchy=enable_hierarchy
        )
        progress.update(task, description="[green]✓ Graph built")

        # Get statistics
        task = progress.add_task("[cyan]Computing statistics...", total=None)
        stats = graph_rag.get_graph_statistics()
        progress.update(task, description="[green]✓ Statistics computed")

        # Save graph
        task = progress.add_task(f"[cyan]Saving to {output_path}...", total=None)
        graph_rag.graph_builder.save_graph(output_path)
        progress.update(task, description="[green]✓ Graph saved")

    # Display statistics
    console.rule("[bold blue]Graph Statistics")
    rprint(f"\n[bold]Nodes:[/bold] {stats['num_nodes']:,}")
    rprint(f"[bold]Edges:[/bold] {stats['num_edges']:,}")
    rprint(f"[bold]Density:[/bold] {stats['density']:.4f}")
    rprint(f"[bold]Avg Degree:[/bold] {stats['avg_degree']:.2f}")
    rprint(f"[bold]Connected Components:[/bold] {stats['num_connected_components']}")

    # Entity statistics
    entity_stats = stats.get('entity_statistics', {})
    rprint(f"\n[bold cyan]Total Entities:[/bold cyan] {entity_stats.get('total_entities', 0):,}")

    if 'by_type' in entity_stats:
        rprint("\n[bold]By Type:[/bold]")
        for entity_type, count in entity_stats['by_type'].items():
            rprint(f"  • {entity_type}: {count:,}")

    # Top controls
    if 'top_controls' in entity_stats:
        rprint("\n[bold]Top 10 NIST Controls:[/bold]")
        for control in entity_stats['top_controls']:
            rprint(f"  • {control['id']}: {control['frequency']} occurrences")

    # Top concepts
    if 'top_concepts' in entity_stats:
        rprint("\n[bold]Top 10 Security Concepts:[/bold]")
        for concept in entity_stats['top_concepts']:
            rprint(f"  • {concept['id']}: {concept['frequency']} occurrences")

    # Central entities (PageRank)
    if 'top_central_entities' in stats:
        rprint("\n[bold]Top 10 Central Entities (PageRank):[/bold]")
        for entity_id, score in stats['top_central_entities']:
            rprint(f"  • {entity_id}: {score:.4f}")

    # Save statistics
    stats_path = Path(output_path).parent / "graph_statistics.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    rprint(f"\n[green]✓[/green] Statistics saved to {stats_path}")

    console.rule("[bold green]✓ Knowledge Graph Built Successfully")
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Build knowledge graph from ChromaDB collection"
    )
    parser.add_argument(
        '--persist',
        type=str,
        default='artifacts/index',
        help='ChromaDB persistence directory'
    )
    parser.add_argument(
        '--collection',
        type=str,
        default='studykit',
        help='Collection name'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='artifacts/graph/knowledge_graph.pkl',
        help='Output path for graph'
    )
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Sample size (None = all documents)'
    )
    parser.add_argument(
        '--no-cooccurrence',
        action='store_true',
        help='Disable co-occurrence edges'
    )
    parser.add_argument(
        '--no-hierarchy',
        action='store_true',
        help='Disable hierarchical edges'
    )

    args = parser.parse_args()

    try:
        stats = build_graph(
            persist_dir=args.persist,
            collection=args.collection,
            output_path=args.output,
            sample_size=args.sample,
            enable_cooccurrence=not args.no_cooccurrence,
            enable_hierarchy=not args.no_hierarchy
        )

        return 0

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e}")
        logger.exception("Graph building failed")
        return 1


if __name__ == '__main__':
    exit(main())
