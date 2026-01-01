"""
Graph-Enhanced RAG

Hybrid retrieval combining:
1. Vector semantic search (existing ChromaDB)
2. Graph traversal for related entities
3. Multi-hop reasoning paths

Provides richer context by including graph-connected knowledge.
"""

import logging
from typing import List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import networkx as nx

from .graph_builder import KnowledgeGraphBuilder
from .entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


@dataclass
class GraphRAGResult:
    """Result from graph-enhanced RAG query"""
    query: str
    vector_results: List[Dict[str, Any]] = field(default_factory=list)
    graph_entities: List[str] = field(default_factory=list)
    graph_paths: List[List[str]] = field(default_factory=list)
    combined_context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class GraphEnhancedRAG:
    """RAG system enhanced with knowledge graph reasoning"""

    def __init__(
        self,
        chroma_persist_dir: str,
        collection_name: str,
        graph_path: str = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize graph-enhanced RAG

        Args:
            chroma_persist_dir: Path to ChromaDB persistence
            collection_name: Collection name
            graph_path: Path to knowledge graph (optional)
            embedding_model: Sentence transformer model
        """
        # Vector search components
        self.client = PersistentClient(path=chroma_persist_dir)
        self.collection = self.client.get_collection(collection_name)
        self.embed_model = SentenceTransformer(embedding_model)

        # Graph components
        self.graph_builder = KnowledgeGraphBuilder()
        if graph_path:
            try:
                self.graph_builder.load_graph(graph_path)
                logger.info(f"Loaded knowledge graph from {graph_path}")
            except Exception as e:
                logger.warning(f"Could not load graph: {e}. Graph features disabled.")

        self.entity_extractor = EntityExtractor()

    def query(
        self,
        query_text: str,
        topk_vector: int = 6,
        max_graph_depth: int = 2,
        enable_graph: bool = True,
        relationship_types: List[str] = None
    ) -> GraphRAGResult:
        """Execute graph-enhanced RAG query

        Args:
            query_text: User query
            topk_vector: Number of vector results
            max_graph_depth: Maximum graph traversal depth
            enable_graph: Use graph enhancement
            relationship_types: Filter graph by edge types

        Returns:
            GraphRAGResult with combined context
        """
        result = GraphRAGResult(query=query_text)

        # Step 1: Vector search (existing RAG)
        try:
            vector_results = self._vector_search(query_text, topk_vector)
            result.vector_results = vector_results
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            result.metadata['vector_error'] = str(e)
            vector_results = []

        # Step 2: Extract entities from query
        query_entities = []
        if enable_graph and len(self.graph_builder.graph.nodes) > 0:
            try:
                extracted = self.entity_extractor.extract_from_text(
                    query_text,
                    source_id='query'
                )
                query_entities = [e.entity_id for e in extracted]
                result.graph_entities = query_entities
            except Exception as e:
                logger.error(f"Entity extraction failed: {e}")
                result.metadata['entity_error'] = str(e)

        # Step 3: Graph traversal for related entities
        if enable_graph and query_entities and len(self.graph_builder.graph.nodes) > 0:
            try:
                related_entities = self._graph_expansion(
                    query_entities,
                    max_depth=max_graph_depth,
                    relationship_types=relationship_types
                )

                # Find paths between query entities
                paths = self._find_connecting_paths(query_entities)
                result.graph_paths = paths

                # Retrieve documents for related entities
                graph_docs = self._retrieve_entity_documents(related_entities)

                # Merge with vector results
                result.vector_results.extend(graph_docs)
            except Exception as e:
                logger.error(f"Graph expansion failed: {e}")
                result.metadata['graph_error'] = str(e)

        # Step 4: Build combined context
        result.combined_context = self._build_context(result.vector_results)

        # Step 5: Metadata
        result.metadata.update({
            'vector_count': len([r for r in result.vector_results if r.get('source') == 'vector']),
            'graph_count': len([r for r in result.vector_results if r.get('source') == 'graph']),
            'query_entities': query_entities,
            'graph_enabled': enable_graph
        })

        return result

    def _vector_search(
        self,
        query_text: str,
        topk: int
    ) -> List[Dict[str, Any]]:
        """Perform vector semantic search"""
        # Encode query
        query_vector = self.embed_model.encode([query_text])[0].tolist()

        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=topk
        )

        # Format results
        formatted = []
        if results and 'documents' in results and results['documents']:
            chunks = results['documents'][0]
            metadatas = results['metadatas'][0]

            for chunk, meta in zip(chunks, metadatas):
                formatted.append({
                    'text': chunk,
                    'metadata': meta,
                    'source': 'vector'
                })

        return formatted

    def _graph_expansion(
        self,
        seed_entities: List[str],
        max_depth: int = 2,
        relationship_types: List[str] = None
    ) -> Set[str]:
        """Expand query entities via graph traversal

        Args:
            seed_entities: Starting entities
            max_depth: Maximum traversal depth
            relationship_types: Filter by edge types

        Returns:
            Set of related entity IDs
        """
        related = set(seed_entities)

        for entity_id in seed_entities:
            neighbors = self.graph_builder.get_neighbors(
                entity_id,
                relationship_type=relationship_types[0] if relationship_types else None,
                max_depth=max_depth
            )
            related.update(neighbors)

        logger.info(f"Graph expansion: {len(seed_entities)} seeds -> {len(related)} related entities")
        return related

    def _find_connecting_paths(
        self,
        entities: List[str],
        max_paths: int = 5
    ) -> List[List[str]]:
        """Find paths connecting query entities

        Args:
            entities: Entity IDs to connect
            max_paths: Maximum paths to return

        Returns:
            List of paths (each path is a list of entity IDs)
        """
        paths = []

        # Find paths between each pair
        for i, source in enumerate(entities):
            for target in entities[i+1:]:
                path = self.graph_builder.get_shortest_path(source, target)
                if path:
                    paths.append(path)

                if len(paths) >= max_paths:
                    return paths

        return paths

    def _retrieve_entity_documents(
        self,
        entity_ids: Set[str]
    ) -> List[Dict[str, Any]]:
        """Retrieve documents mentioning specific entities

        Args:
            entity_ids: Entity IDs to retrieve

        Returns:
            List of document chunks
        """
        docs = []

        # Get entity details from extractor
        for entity_id in entity_ids:
            entity = self.entity_extractor.get_entity(entity_id)
            if not entity:
                continue

            # Simple retrieval: search for entity name
            try:
                # Use vector search for entity name
                entity_vector = self.embed_model.encode([entity.name])[0].tolist()
                results = self.collection.query(
                    query_embeddings=[entity_vector],
                    n_results=2  # Limit per entity
                )

                if results and 'documents' in results and results['documents']:
                    chunks = results['documents'][0]
                    metadatas = results['metadatas'][0]

                    for chunk, meta in zip(chunks, metadatas):
                        # Verify entity actually appears in chunk
                        if entity_id.lower() in chunk.lower() or entity.name.lower() in chunk.lower():
                            docs.append({
                                'text': chunk,
                                'metadata': meta,
                                'source': 'graph',
                                'entity_id': entity_id
                            })
            except Exception as e:
                logger.warning(f"Could not retrieve docs for {entity_id}: {e}")

        return docs

    def _build_context(self, results: List[Dict[str, Any]]) -> str:
        """Build context string from results

        Args:
            results: Combined vector + graph results

        Returns:
            Formatted context string
        """
        context = ""

        for i, result in enumerate(results, start=1):
            text = result.get('text', '')
            meta = result.get('metadata', {})
            source_type = result.get('source', 'unknown')

            source_name = meta.get('source', 'Unknown')
            page = meta.get('page', 'N/A')

            cite = f"[{i}] ({source_type}) source={source_name} page={page}"
            context += f"{cite}\n{text}\n\n"

        return context

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        if len(self.graph_builder.graph.nodes) == 0:
            return {'status': 'no graph loaded'}

        return self.graph_builder.get_statistics()

    def build_graph_from_collection(
        self,
        sample_size: int = None,
        enable_cooccurrence: bool = True,
        enable_hierarchy: bool = True
    ) -> nx.MultiDiGraph:
        """Build knowledge graph from ChromaDB collection

        Args:
            sample_size: Limit documents (None = all)
            enable_cooccurrence: Build co-occurrence edges
            enable_hierarchy: Build hierarchical edges

        Returns:
            Built knowledge graph
        """
        logger.info("Building knowledge graph from ChromaDB collection...")

        # Fetch documents from ChromaDB
        results = self.collection.get(
            limit=sample_size if sample_size else None
        )

        if not results or 'documents' not in results:
            logger.warning("No documents found in collection")
            return self.graph_builder.graph

        # Format for graph builder
        documents = []
        for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas'])):
            documents.append({
                'id': meta.get('chunk_id', str(i)),
                'text': doc,
                'metadata': meta
            })

        # Build graph
        graph = self.graph_builder.build_from_corpus(
            documents,
            text_field='text',
            id_field='id',
            enable_cooccurrence=enable_cooccurrence,
            enable_hierarchy=enable_hierarchy
        )

        logger.info(f"Built graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")

        return graph
