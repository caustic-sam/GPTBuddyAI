"""
Research Agent

Performs deep multi-document research and synthesis with:
- Multi-hop iterative querying
- Theme clustering
- Cross-reference validation
- Citation tracking
"""

import time
import logging
from typing import Dict, List, Any, Set
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import numpy as np
from sklearn.cluster import KMeans

from .base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Conducts comprehensive research across the knowledge base.

    Workflow:
    1. Initial query for seed documents
    2. Extract key concepts and expand queries
    3. Multi-hop iterative deepening
    4. Theme clustering of findings
    5. Structured synthesis with citations
    """

    def __init__(
        self,
        chroma_persist_dir: str = "artifacts/index",
        collection_name: str = "studykit",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        super().__init__(
            name="ResearchAgent",
            description="Deep research and multi-document synthesis"
        )

        # Initialize retrieval components
        try:
            self.client = PersistentClient(path=chroma_persist_dir)
            self.collection = self.client.get_collection(collection_name)
            self.embed_model = SentenceTransformer(embedding_model)
        except Exception as e:
            logger.error(f"Failed to initialize ResearchAgent: {e}")
            self.client = None
            self.collection = None
            self.embed_model = None

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute research task.

        Args:
            task: Must contain:
                - topic: Research topic or question
                - depth: Search depth (1-5, default 3)
                - max_sources: Maximum sources per hop (default 10)
                - cluster_themes: Enable theme clustering (default True)

        Returns:
            AgentResult with research findings
        """
        start_time = time.time()
        result = AgentResult(agent_name=self.name, status="success")

        # Validate components
        if not self.collection or not self.embed_model:
            result.status = "failure"
            result.errors.append("Research agent not properly initialized")
            return result

        # Extract parameters
        topic = task.get('topic', '')
        depth = task.get('depth', 3)
        max_sources = task.get('max_sources', 10)
        cluster_themes = task.get('cluster_themes', True)

        if not topic:
            result.status = "failure"
            result.errors.append("No research topic provided")
            return result

        try:
            # Step 1: Multi-hop research
            self.log_step("Research initiation", f"Topic: {topic}, Depth: {depth}")

            all_documents = []
            seen_chunks = set()  # Deduplicate
            query_history = [topic]

            for hop in range(depth):
                self.log_step(f"Hop {hop+1}/{depth}", f"Query: {query_history[-1]}")

                # Query ChromaDB
                hop_docs = self._query_documents(
                    query_history[-1],
                    max_results=max_sources
                )

                # Deduplicate
                new_docs = []
                for doc in hop_docs:
                    chunk_id = doc.get('chunk_id', '')
                    if chunk_id and chunk_id not in seen_chunks:
                        seen_chunks.add(chunk_id)
                        new_docs.append(doc)

                all_documents.extend(new_docs)

                self.log_step(
                    f"Hop {hop+1} results",
                    f"Found {len(new_docs)} new documents ({len(all_documents)} total)"
                )

                # Extract concepts for next hop (if not last hop)
                if hop < depth - 1:
                    concepts = self._extract_key_concepts(new_docs)
                    if concepts:
                        # Create expanded query for next hop
                        expanded_query = f"{topic} {' '.join(concepts[:3])}"
                        query_history.append(expanded_query)
                    else:
                        # No new concepts, break early
                        break

            self.log_step("Research complete", f"Retrieved {len(all_documents)} unique documents")

            # Step 2: Theme clustering (optional)
            themes = []
            if cluster_themes and len(all_documents) >= 5:
                self.log_step("Theme clustering", "Identifying themes...")
                themes = self._cluster_themes(all_documents, n_clusters=min(5, len(all_documents) // 3))
                self.log_step("Themes identified", f"Found {len(themes)} themes")

            # Step 3: Build structured result
            result.data = {
                'topic': topic,
                'depth': depth,
                'total_sources': len(all_documents),
                'query_history': query_history,
                'documents': all_documents,
                'themes': themes,
                'summary': self._create_summary(topic, all_documents, themes)
            }

            result.steps = self.steps

        except Exception as e:
            logger.exception(f"Research failed: {e}")
            result.status = "failure"
            result.errors.append(str(e))

        result.execution_time = time.time() - start_time
        return result

    def _query_documents(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Query ChromaDB for documents

        Args:
            query: Search query
            max_results: Maximum results to return

        Returns:
            List of document dictionaries
        """
        # Encode query
        query_vector = self.embed_model.encode([query])[0].tolist()

        # Search
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=max_results
        )

        # Format results
        documents = []
        if results and 'documents' in results and results['documents']:
            chunks = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results.get('distances', [[]])[0]

            for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
                doc = {
                    'text': chunk,
                    'chunk_id': meta.get('chunk_id', f'chunk_{i}'),
                    'source': meta.get('source', 'Unknown'),
                    'page': meta.get('page', 'N/A'),
                    'distance': distances[i] if i < len(distances) else None
                }
                documents.append(doc)

        return documents

    def _extract_key_concepts(
        self,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[str]:
        """Extract key concepts from documents for query expansion

        Args:
            documents: Documents to analyze
            top_k: Number of concepts to extract

        Returns:
            List of key concept strings
        """
        # Simple concept extraction: most frequent capitalized phrases
        concept_freq = defaultdict(int)

        for doc in documents:
            text = doc.get('text', '')

            # Extract capitalized phrases (simple heuristic)
            words = text.split()
            for i, word in enumerate(words):
                if word and word[0].isupper() and len(word) > 3:
                    # Single word concept
                    concept_freq[word] += 1

                    # Two-word phrases
                    if i < len(words) - 1 and words[i+1] and words[i+1][0].isupper():
                        phrase = f"{word} {words[i+1]}"
                        concept_freq[phrase] += 1

        # Get top concepts
        top_concepts = sorted(
            concept_freq.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]

        return [concept for concept, freq in top_concepts]

    def _cluster_themes(
        self,
        documents: List[Dict[str, Any]],
        n_clusters: int = 5
    ) -> List[Dict[str, Any]]:
        """Cluster documents into themes

        Args:
            documents: Documents to cluster
            n_clusters: Number of clusters

        Returns:
            List of theme dictionaries with representative documents
        """
        if len(documents) < n_clusters:
            n_clusters = len(documents)

        # Encode all documents
        texts = [doc['text'] for doc in documents]
        embeddings = self.embed_model.encode(texts)

        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)

        # Group documents by cluster
        clusters = defaultdict(list)
        for doc, label in zip(documents, labels):
            clusters[label].append(doc)

        # Create theme summaries
        themes = []
        for cluster_id, cluster_docs in clusters.items():
            # Find document closest to centroid
            cluster_indices = [i for i, l in enumerate(labels) if l == cluster_id]
            cluster_embeddings = embeddings[cluster_indices]
            centroid = kmeans.cluster_centers_[cluster_id]

            # Calculate distances to centroid
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            representative_idx = cluster_indices[np.argmin(distances)]
            representative = documents[representative_idx]

            # Extract theme name from representative text (first 50 chars)
            theme_name = representative['text'][:50].strip() + "..."

            themes.append({
                'theme_id': int(cluster_id),
                'theme_name': theme_name,
                'document_count': len(cluster_docs),
                'representative_doc': representative,
                'documents': cluster_docs[:5]  # Top 5 docs per theme
            })

        return themes

    def _create_summary(
        self,
        topic: str,
        documents: List[Dict[str, Any]],
        themes: List[Dict[str, Any]]
    ) -> str:
        """Create research summary

        Args:
            topic: Research topic
            documents: All documents
            themes: Identified themes

        Returns:
            Summary string
        """
        summary = f"Research Summary: {topic}\n\n"

        summary += f"Total Sources: {len(documents)}\n"

        if themes:
            summary += f"\nKey Themes ({len(themes)}):\n"
            for theme in themes:
                summary += f"- {theme['theme_name']} ({theme['document_count']} documents)\n"

        # Source breakdown
        sources = defaultdict(int)
        for doc in documents:
            sources[doc['source']] += 1

        summary += f"\nSource Breakdown:\n"
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            summary += f"- {source}: {count} passages\n"

        return summary
