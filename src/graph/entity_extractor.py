"""
Entity Extraction Pipeline

Extracts structured entities from conversations and documents:
- NIST controls (AC-2, IA-5, etc.)
- Technical concepts (MFA, encryption, zero-trust)
- Projects and initiatives
- People and organizations
"""

import re
from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Structured entity representation"""
    entity_id: str
    entity_type: str  # control, concept, project, person, org
    name: str
    aliases: Set[str] = field(default_factory=set)
    properties: Dict[str, Any] = field(default_factory=dict)
    source_documents: List[str] = field(default_factory=list)
    frequency: int = 0


class EntityExtractor:
    """Extract structured entities from text"""

    # NIST Control patterns
    CONTROL_PATTERN = re.compile(r'\b([A-Z]{2})-(\d+)(?:\((\d+)\))?\b')

    # NIST publication patterns
    NIST_PUB_PATTERN = re.compile(r'\bNIST\s+SP\s+(\d+-\d+(?:[A-Z])?(?:r\d+)?)\b', re.IGNORECASE)

    # Common security concepts (expandable)
    SECURITY_CONCEPTS = {
        'mfa': ['multi-factor authentication', '2fa', 'two-factor'],
        'encryption': ['encrypt', 'encrypted', 'cipher', 'aes', 'rsa'],
        'zero-trust': ['zero trust', 'zt', 'never trust always verify'],
        'identity': ['digital identity', 'authentication', 'identity verification'],
        'privacy': ['data privacy', 'pii', 'personal information', 'gdpr'],
        'access-control': ['access control', 'authorization', 'rbac', 'abac'],
        'audit': ['audit log', 'logging', 'monitoring', 'siem'],
        'incident-response': ['incident response', 'ir', 'breach response'],
        'risk-management': ['risk assessment', 'risk analysis', 'threat modeling'],
        'supply-chain': ['supply chain security', 'sbom', 'vendor risk']
    }

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)  # type -> entity_ids

    def extract_from_text(
        self,
        text: str,
        source_id: str,
        entity_types: List[str] = None
    ) -> List[Entity]:
        """Extract entities from text

        Args:
            text: Text to extract from
            source_id: Document/conversation ID
            entity_types: Types to extract (None = all)

        Returns:
            List of extracted entities
        """
        if entity_types is None:
            entity_types = ['control', 'publication', 'concept']

        extracted = []

        if 'control' in entity_types:
            extracted.extend(self._extract_nist_controls(text, source_id))

        if 'publication' in entity_types:
            extracted.extend(self._extract_nist_publications(text, source_id))

        if 'concept' in entity_types:
            extracted.extend(self._extract_security_concepts(text, source_id))

        # Update internal entity registry
        for entity in extracted:
            self._register_entity(entity)

        return extracted

    def _extract_nist_controls(self, text: str, source_id: str) -> List[Entity]:
        """Extract NIST control identifiers"""
        entities = []

        for match in self.CONTROL_PATTERN.finditer(text):
            family = match.group(1)
            number = match.group(2)
            enhancement = match.group(3)

            if enhancement:
                control_id = f"{family}-{number}({enhancement})"
                name = f"NIST Control {family}-{number} Enhancement {enhancement}"
            else:
                control_id = f"{family}-{number}"
                name = f"NIST Control {family}-{number}"

            # Verify it's actually mentioned in context (not just pattern match)
            if control_id in text:
                entity = Entity(
                    entity_id=control_id,
                    entity_type='control',
                    name=name,
                    properties={
                        'family': family,
                        'number': number,
                        'enhancement': enhancement
                    },
                    source_documents=[source_id],
                    frequency=1
                )
                entities.append(entity)

        return entities

    def _extract_nist_publications(self, text: str, source_id: str) -> List[Entity]:
        """Extract NIST publication references"""
        entities = []

        for match in self.NIST_PUB_PATTERN.finditer(text):
            pub_number = match.group(1)
            entity_id = f"NIST-SP-{pub_number}"
            name = f"NIST SP {pub_number}"

            entity = Entity(
                entity_id=entity_id,
                entity_type='publication',
                name=name,
                properties={'publication_number': pub_number},
                source_documents=[source_id],
                frequency=1
            )
            entities.append(entity)

        return entities

    def _extract_security_concepts(self, text: str, source_id: str) -> List[Entity]:
        """Extract security concepts based on keyword matching"""
        entities = []
        text_lower = text.lower()

        for concept_id, keywords in self.SECURITY_CONCEPTS.items():
            # Check if any keyword appears in text
            matches = [kw for kw in keywords if kw in text_lower]

            if matches:
                entity = Entity(
                    entity_id=concept_id,
                    entity_type='concept',
                    name=concept_id.replace('-', ' ').title(),
                    aliases=set(keywords),
                    properties={'matched_keywords': matches},
                    source_documents=[source_id],
                    frequency=len(matches)
                )
                entities.append(entity)

        return entities

    def _register_entity(self, entity: Entity):
        """Register entity in internal index"""
        if entity.entity_id in self.entities:
            # Merge with existing entity
            existing = self.entities[entity.entity_id]
            existing.frequency += entity.frequency
            existing.source_documents.extend(entity.source_documents)
            existing.source_documents = list(set(existing.source_documents))  # Deduplicate
        else:
            # New entity
            self.entities[entity.entity_id] = entity
            self.entity_index[entity.entity_type].add(entity.entity_id)

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID"""
        return self.entities.get(entity_id)

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        entity_ids = self.entity_index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids]

    def get_top_entities(self, entity_type: str = None, top_k: int = 20) -> List[Entity]:
        """Get most frequent entities

        Args:
            entity_type: Filter by type (None = all types)
            top_k: Number to return

        Returns:
            Entities sorted by frequency
        """
        if entity_type:
            entities = self.get_entities_by_type(entity_type)
        else:
            entities = list(self.entities.values())

        return sorted(entities, key=lambda e: e.frequency, reverse=True)[:top_k]

    def extract_from_corpus(
        self,
        documents: List[Dict[str, str]],
        text_field: str = 'text',
        id_field: str = 'id'
    ) -> Dict[str, List[Entity]]:
        """Extract entities from entire corpus

        Args:
            documents: List of documents with text and ID fields
            text_field: Field containing text
            id_field: Field containing document ID

        Returns:
            Dictionary mapping document IDs to extracted entities
        """
        corpus_entities = {}

        for doc in documents:
            text = doc.get(text_field, '')
            doc_id = doc.get(id_field, str(hash(text)))

            entities = self.extract_from_text(text, doc_id)
            corpus_entities[doc_id] = entities

        logger.info(f"Extracted {len(self.entities)} unique entities from {len(documents)} documents")
        return corpus_entities

    def get_statistics(self) -> Dict[str, Any]:
        """Get entity extraction statistics"""
        stats = {
            'total_entities': len(self.entities),
            'by_type': {
                entity_type: len(entity_ids)
                for entity_type, entity_ids in self.entity_index.items()
            },
            'top_controls': [
                {'id': e.entity_id, 'frequency': e.frequency}
                for e in self.get_top_entities('control', 10)
            ],
            'top_concepts': [
                {'id': e.entity_id, 'frequency': e.frequency}
                for e in self.get_top_entities('concept', 10)
            ]
        }
        return stats
