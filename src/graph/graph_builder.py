"""
Knowledge Graph Builder

Constructs graph from extracted entities and discovers relationships:
- Co-occurrence relationships (entities appearing together)
- Hierarchical relationships (controls -> families, concepts -> categories)
- Temporal relationships (evolution over time)
- Semantic relationships (vector similarity)
"""

import networkx as nx
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import logging
from pathlib import Path
import json
import pickle

from .entity_extractor import Entity, EntityExtractor

logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Graph relationship/edge"""
    source: str  # entity_id
    target: str  # entity_id
    relationship_type: str  # co-occurrence, hierarchy, semantic, temporal
    weight: float = 1.0
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class KnowledgeGraphBuilder:
    """Build and manage knowledge graph from entities"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()  # Allow multiple edge types between nodes
        self.entity_extractor = EntityExtractor()

    def add_entity(self, entity: Entity):
        """Add entity as graph node"""
        self.graph.add_node(
            entity.entity_id,
            entity_type=entity.entity_type,
            name=entity.name,
            frequency=entity.frequency,
            properties=entity.properties
        )

    def add_relationship(self, relationship: Relationship):
        """Add relationship as graph edge"""
        self.graph.add_edge(
            relationship.source,
            relationship.target,
            key=relationship.relationship_type,
            weight=relationship.weight,
            **relationship.properties
        )

    def build_from_corpus(
        self,
        documents: List[Dict[str, str]],
        text_field: str = 'text',
        id_field: str = 'id',
        enable_cooccurrence: bool = True,
        enable_hierarchy: bool = True,
        cooccurrence_window: int = None  # None = document-level
    ) -> nx.MultiDiGraph:
        """Build complete knowledge graph from corpus

        Args:
            documents: List of documents
            text_field: Field containing text
            id_field: Field containing document ID
            enable_cooccurrence: Build co-occurrence edges
            enable_hierarchy: Build hierarchical edges
            cooccurrence_window: Window size for co-occurrence (None = document-level)

        Returns:
            NetworkX graph
        """
        logger.info(f"Building knowledge graph from {len(documents)} documents...")

        # Step 1: Extract entities
        corpus_entities = self.entity_extractor.extract_from_corpus(
            documents, text_field, id_field
        )

        # Step 2: Add all entities as nodes
        for entity in self.entity_extractor.entities.values():
            self.add_entity(entity)

        logger.info(f"Added {len(self.graph.nodes)} entity nodes")

        # Step 3: Build co-occurrence relationships
        if enable_cooccurrence:
            self._build_cooccurrence_edges(corpus_entities)

        # Step 4: Build hierarchical relationships
        if enable_hierarchy:
            self._build_hierarchy_edges()

        logger.info(f"Built graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")

        return self.graph

    def _build_cooccurrence_edges(self, corpus_entities: Dict[str, List[Entity]]):
        """Build edges based on entity co-occurrence in documents"""
        logger.info("Building co-occurrence relationships...")

        cooccurrence_counts = defaultdict(lambda: defaultdict(int))

        for doc_id, entities in corpus_entities.items():
            # All entities in this document co-occur
            entity_ids = [e.entity_id for e in entities]

            # Create edges for each pair
            for i, source_id in enumerate(entity_ids):
                for target_id in entity_ids[i+1:]:
                    # Count co-occurrences
                    cooccurrence_counts[source_id][target_id] += 1
                    cooccurrence_counts[target_id][source_id] += 1

        # Add edges with weights
        edge_count = 0
        for source_id, targets in cooccurrence_counts.items():
            for target_id, count in targets.items():
                relationship = Relationship(
                    source=source_id,
                    target=target_id,
                    relationship_type='co-occurrence',
                    weight=float(count),
                    properties={'co_occurrence_count': count}
                )
                self.add_relationship(relationship)
                edge_count += 1

        logger.info(f"Added {edge_count} co-occurrence edges")

    def _build_hierarchy_edges(self):
        """Build hierarchical relationships (e.g., controls -> families)"""
        logger.info("Building hierarchical relationships...")

        edge_count = 0

        # NIST Control hierarchies
        controls = self.entity_extractor.get_entities_by_type('control')

        # Group controls by family
        families = defaultdict(list)
        for control in controls:
            family = control.properties.get('family')
            if family:
                families[family].append(control)

        # Create family nodes and edges
        for family, family_controls in families.items():
            # Add family node if not exists
            family_id = f"FAMILY-{family}"
            if family_id not in self.graph:
                self.graph.add_node(
                    family_id,
                    entity_type='control_family',
                    name=f"{family} - Control Family",
                    frequency=len(family_controls)
                )

            # Create parent-child relationships
            for control in family_controls:
                relationship = Relationship(
                    source=family_id,
                    target=control.entity_id,
                    relationship_type='contains',
                    weight=1.0,
                    properties={'hierarchy_level': 'family->control'}
                )
                self.add_relationship(relationship)
                edge_count += 1

        logger.info(f"Added {edge_count} hierarchical edges")

    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: str = None,
        max_depth: int = 1
    ) -> List[str]:
        """Get neighboring entities

        Args:
            entity_id: Source entity
            relationship_type: Filter by edge type
            max_depth: Maximum traversal depth

        Returns:
            List of connected entity IDs
        """
        if entity_id not in self.graph:
            return []

        if max_depth == 1:
            # Direct neighbors
            if relationship_type:
                neighbors = [
                    target for _, target, key in self.graph.out_edges(entity_id, keys=True)
                    if key == relationship_type
                ]
            else:
                neighbors = list(self.graph.successors(entity_id))
            return neighbors
        else:
            # Multi-hop traversal (BFS)
            visited = set()
            queue = [(entity_id, 0)]
            neighbors = []

            while queue:
                current, depth = queue.pop(0)

                if current in visited or depth >= max_depth:
                    continue

                visited.add(current)

                if depth > 0:  # Don't include source
                    neighbors.append(current)

                # Add successors
                for _, target, key in self.graph.out_edges(current, keys=True):
                    if relationship_type is None or key == relationship_type:
                        queue.append((target, depth + 1))

            return neighbors

    def get_entity_subgraph(
        self,
        entity_ids: List[str],
        include_neighbors: bool = True
    ) -> nx.MultiDiGraph:
        """Extract subgraph containing specific entities

        Args:
            entity_ids: Entities to include
            include_neighbors: Also include direct neighbors

        Returns:
            Subgraph
        """
        nodes = set(entity_ids)

        if include_neighbors:
            for entity_id in entity_ids:
                if entity_id in self.graph:
                    nodes.update(self.graph.successors(entity_id))
                    nodes.update(self.graph.predecessors(entity_id))

        return self.graph.subgraph(nodes).copy()

    def get_shortest_path(
        self,
        source: str,
        target: str,
        relationship_type: str = None
    ) -> List[str] | None:
        """Find shortest path between entities

        Args:
            source: Source entity ID
            target: Target entity ID
            relationship_type: Filter by edge type

        Returns:
            List of entity IDs forming path, or None if no path exists
        """
        if source not in self.graph or target not in self.graph:
            return None

        try:
            if relationship_type:
                # Filter graph by edge type
                filtered_edges = [
                    (u, v) for u, v, key in self.graph.edges(keys=True)
                    if key == relationship_type
                ]
                filtered_graph = self.graph.edge_subgraph(filtered_edges)
                return nx.shortest_path(filtered_graph, source, target)
            else:
                return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return None

    def get_central_entities(
        self,
        centrality_type: str = 'degree',
        top_k: int = 20
    ) -> List[Tuple[str, float]]:
        """Get most central entities in graph

        Args:
            centrality_type: 'degree', 'betweenness', 'closeness', 'pagerank'
            top_k: Number to return

        Returns:
            List of (entity_id, centrality_score) tuples
        """
        if centrality_type == 'degree':
            centrality = nx.degree_centrality(self.graph)
        elif centrality_type == 'betweenness':
            centrality = nx.betweenness_centrality(self.graph)
        elif centrality_type == 'closeness':
            centrality = nx.closeness_centrality(self.graph)
        elif centrality_type == 'pagerank':
            centrality = nx.pagerank(self.graph)
        else:
            raise ValueError(f"Unknown centrality type: {centrality_type}")

        sorted_entities = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_entities[:top_k]

    def save_graph(self, output_path: str | Path):
        """Save graph to disk

        Args:
            output_path: Path to save (will create .graphml and .pkl files)
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as GraphML (human-readable)
        graphml_path = output_path.with_suffix('.graphml')
        nx.write_graphml(self.graph, graphml_path)
        logger.info(f"Saved GraphML to {graphml_path}")

        # Save as pickle (preserves all data types)
        pkl_path = output_path.with_suffix('.pkl')
        with open(pkl_path, 'wb') as f:
            pickle.dump(self.graph, f)
        logger.info(f"Saved pickle to {pkl_path}")

        # Save entity extractor state
        extractor_path = output_path.parent / "entity_extractor.pkl"
        with open(extractor_path, 'wb') as f:
            pickle.dump(self.entity_extractor, f)
        logger.info(f"Saved entity extractor to {extractor_path}")

    def load_graph(self, input_path: str | Path):
        """Load graph from disk

        Args:
            input_path: Path to graph file (.pkl preferred)
        """
        input_path = Path(input_path)

        # Load pickle if available
        pkl_path = input_path.with_suffix('.pkl')
        if pkl_path.exists():
            with open(pkl_path, 'rb') as f:
                self.graph = pickle.load(f)
            logger.info(f"Loaded graph from {pkl_path}")
        else:
            # Fall back to GraphML
            graphml_path = input_path.with_suffix('.graphml')
            self.graph = nx.read_graphml(graphml_path)
            logger.info(f"Loaded graph from {graphml_path}")

        # Load entity extractor
        extractor_path = input_path.parent / "entity_extractor.pkl"
        if extractor_path.exists():
            with open(extractor_path, 'rb') as f:
                self.entity_extractor = pickle.load(f)
            logger.info(f"Loaded entity extractor from {extractor_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        stats = {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'num_connected_components': nx.number_weakly_connected_components(self.graph),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / len(self.graph.nodes) if len(self.graph.nodes) > 0 else 0,
            'entity_statistics': self.entity_extractor.get_statistics(),
            'top_central_entities': self.get_central_entities('pagerank', 10)
        }
        return stats
