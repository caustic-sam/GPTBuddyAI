"""
Compliance Gap Analysis Agent

Analyzes NIST control implementation coverage based on conversation history.
"""

import time
import re
from pathlib import Path
from typing import Dict, List, Any, Set
import pandas as pd
from chromadb import PersistentClient

from .base_agent import BaseAgent, AgentResult


class ComplianceAgent(BaseAgent):
    """
    Analyzes compliance gaps by comparing NIST controls against conversation evidence.

    Workflow:
    1. Load all NIST controls from document index
    2. Search conversations for implementation evidence
    3. Classify controls: implemented, partial, gap
    4. Generate prioritized remediation recommendations
    """

    def __init__(self, index_path: str = "artifacts/index", collection_name: str = "studykit"):
        super().__init__(
            name="ComplianceAgent",
            description="NIST compliance gap analysis and remediation planning"
        )
        self.index_path = index_path
        self.collection_name = collection_name

    def execute(self, task: Dict[str, Any]) -> AgentResult:
        """
        Execute compliance gap analysis.

        Args:
            task: Must contain:
                - framework: "NIST-800-53" (default) or other framework
                - min_evidence_threshold: Minimum passages to count as implemented (default: 2)

        Returns:
            AgentResult with gap analysis data
        """
        start_time = time.time()
        result = AgentResult(agent_name=self.name, status="success")

        # Validate task
        framework = task.get('framework', 'NIST-800-53')
        threshold = task.get('min_evidence_threshold', 2)

        try:
            # Step 1: Extract NIST controls from index
            self.log_step("Extracting NIST controls")
            controls = self._extract_nist_controls()
            result.add_step("extract_controls", f"Found {len(controls)} controls", 0)

            if not controls:
                result.status = "failure"
                result.errors.append("No NIST controls found in knowledge base")
                return result

            # Step 2: Search for evidence of each control
            self.log_step("Searching for implementation evidence")
            evidence_map = self._search_for_evidence(controls, threshold)
            result.add_step("search_evidence", f"Analyzed {len(controls)} controls", 0)

            # Step 3: Classify controls
            self.log_step("Classifying implementation status")
            classification = self._classify_controls(evidence_map, threshold)
            result.add_step("classify", classification['summary'], 0)

            # Step 4: Generate recommendations
            self.log_step("Generating remediation plan")
            recommendations = self._generate_recommendations(classification)
            result.add_step("recommendations", f"Generated {len(recommendations)} recommendations", 0)

            # Package results
            result.data = {
                'framework': framework,
                'total_controls': len(controls),
                'classification': classification,
                'evidence_map': evidence_map,
                'recommendations': recommendations,
                'summary': {
                    'implemented': len(classification['implemented']),
                    'partial': len(classification['partial']),
                    'gaps': len(classification['gaps']),
                    'coverage_percentage': (
                        len(classification['implemented']) / len(controls) * 100
                        if controls else 0
                    )
                }
            }

        except Exception as e:
            self.logger.error(f"Compliance analysis failed: {e}")
            result.status = "failure"
            result.errors.append(str(e))

        result.execution_time = time.time() - start_time
        return result

    def _extract_nist_controls(self) -> Set[str]:
        """
        Extract unique NIST control identifiers from the knowledge base.

        Returns:
            Set of control IDs (e.g., AC-2, IA-5, SC-7)
        """
        controls = set()
        control_pattern = re.compile(r'\b([A-Z]{2})-(\d+)\b')

        try:
            # Connect to ChromaDB
            client = PersistentClient(path=self.index_path)
            collection = client.get_collection(self.collection_name)

            # Get all NIST documents
            results = collection.get(where={"source": {"$regex": ".*NIST.*|.*SP.*"}})

            if results and 'documents' in results:
                for doc in results['documents']:
                    # Extract control IDs from text
                    matches = control_pattern.findall(doc)
                    for family, number in matches:
                        controls.add(f"{family}-{number}")

        except Exception as e:
            self.logger.warning(f"Error extracting controls: {e}")

        return controls

    def _search_for_evidence(
        self,
        controls: Set[str],
        threshold: int
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for evidence of each control in conversations.

        Args:
            controls: Set of control IDs to search for
            threshold: Minimum evidence count

        Returns:
            Dictionary mapping control IDs to evidence passages
        """
        evidence_map = {}

        try:
            from sentence_transformers import SentenceTransformer

            # Load embedding model
            embed_model = SentenceTransformer("all-MiniLM-L6-v2")

            # Connect to ChromaDB
            client = PersistentClient(path=self.index_path)
            collection = client.get_collection(self.collection_name)

            for control_id in controls:
                # Query for this control
                query = f"{control_id} implementation security control access"
                qv = embed_model.encode([query])[0].tolist()

                results = collection.query(
                    query_embeddings=[qv],
                    n_results=10
                )

                if results and 'documents' in results and results['documents']:
                    passages = []
                    for i, (doc, meta) in enumerate(zip(
                        results['documents'][0],
                        results['metadatas'][0]
                    )):
                        # Only count if control ID actually mentioned
                        if control_id.lower() in doc.lower():
                            passages.append({
                                'text': doc,
                                'source': meta.get('source', 'Unknown'),
                                'page': meta.get('page', 'N/A')
                            })

                    evidence_map[control_id] = passages

        except Exception as e:
            self.logger.error(f"Evidence search failed: {e}")

        return evidence_map

    def _classify_controls(
        self,
        evidence_map: Dict[str, List[Dict[str, Any]]],
        threshold: int
    ) -> Dict[str, List[str]]:
        """
        Classify controls based on evidence found.

        Args:
            evidence_map: Control ID → Evidence passages
            threshold: Minimum evidence for 'implemented' status

        Returns:
            Dictionary with 'implemented', 'partial', 'gaps' lists
        """
        classification = {
            'implemented': [],
            'partial': [],
            'gaps': [],
            'summary': ''
        }

        all_controls = set(evidence_map.keys())

        for control_id, evidence in evidence_map.items():
            evidence_count = len(evidence)

            if evidence_count >= threshold:
                classification['implemented'].append(control_id)
            elif evidence_count > 0:
                classification['partial'].append(control_id)
            else:
                classification['gaps'].append(control_id)

        # Add controls with no evidence at all
        searched = set(evidence_map.keys())
        classification['gaps'].extend(list(all_controls - searched))

        classification['summary'] = (
            f"Implemented: {len(classification['implemented'])}, "
            f"Partial: {len(classification['partial'])}, "
            f"Gaps: {len(classification['gaps'])}"
        )

        return classification

    def _generate_recommendations(
        self,
        classification: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized remediation recommendations.

        Args:
            classification: Control classification results

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # Priority 1: Address critical control families with gaps
        critical_families = {'AC', 'IA', 'SC', 'AU'}  # Access, Identity, System, Audit

        gaps = classification['gaps']
        partial = classification['partial']

        for control_id in gaps:
            family = control_id.split('-')[0]
            priority = 'High' if family in critical_families else 'Medium'

            recommendations.append({
                'control_id': control_id,
                'status': 'gap',
                'priority': priority,
                'action': f'Implement {control_id} security control',
                'reason': 'No implementation evidence found'
            })

        for control_id in partial:
            family = control_id.split('-')[0]
            priority = 'Medium' if family in critical_families else 'Low'

            recommendations.append({
                'control_id': control_id,
                'status': 'partial',
                'priority': priority,
                'action': f'Complete {control_id} implementation',
                'reason': 'Partial evidence found, needs strengthening'
            })

        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        recommendations.sort(key=lambda x: priority_order[x['priority']])

        return recommendations
