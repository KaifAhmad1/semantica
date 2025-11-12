"""
Named Entity Recognition Extractor Module

This module provides core NER capabilities using spaCy and transformers for
entity identification and classification, with fallback pattern-based extraction.

Key Features:
    - spaCy-based entity extraction
    - Pattern-based fallback extraction
    - Multiple entity type support
    - Confidence scoring
    - Batch processing
    - Entity filtering by confidence

Main Classes:
    - NERExtractor: Core NER extractor
    - Entity: Entity representation dataclass

Example Usage:
    >>> from semantica.semantic_extract import NERExtractor
    >>> extractor = NERExtractor(model="en_core_web_sm")
    >>> entities = extractor.extract_entities("Apple Inc. was founded in 1976.")
    >>> filtered = extractor.filter_by_confidence(entities, min_confidence=0.8)

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..utils.exceptions import ProcessingError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


@dataclass
class Entity:
    """Entity representation."""
    
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class NERExtractor:
    """Named Entity Recognition extractor."""
    
    def __init__(self, **config):
        """
        Initialize NER extractor.
        
        Args:
            **config: Configuration options:
                - model: Model name (default: "en_core_web_sm")
                - language: Language code (default: "en")
                - min_confidence: Minimum confidence threshold
        """
        self.logger = get_logger("ner_extractor")
        self.config = config
        
        self.model_name = config.get("model", "en_core_web_sm")
        self.language = config.get("language", "en")
        self.min_confidence = config.get("min_confidence", 0.5)
        self.progress_tracker = get_progress_tracker()
        
        # Initialize spaCy model if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(self.model_name)
            except OSError:
                self.logger.warning(f"spaCy model {self.model_name} not found. NER capabilities limited.")
    
    def extract_entities(self, text: str, **options) -> List[Entity]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            **options: Extraction options:
                - entity_types: Filter by entity types (list)
                - min_confidence: Minimum confidence threshold
                
        Returns:
            list: List of extracted entities
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="semantic_extract",
            submodule="NERExtractor",
            message="Extracting named entities from text"
        )
        
        try:
            if not text:
                self.progress_tracker.stop_tracking(tracking_id, status="completed", message="No text provided")
                return []
            
            min_confidence = options.get("min_confidence", self.min_confidence)
            entity_types = options.get("entity_types")
            
            if self.nlp:
                self.progress_tracker.update_tracking(tracking_id, message="Extracting entities using spaCy...")
                entities = self._extract_with_spacy(text, min_confidence, entity_types)
            else:
                self.progress_tracker.update_tracking(tracking_id, message="Extracting entities using fallback method...")
                entities = self._extract_fallback(text)
            
            self.progress_tracker.stop_tracking(tracking_id, status="completed",
                                              message=f"Extracted {len(entities)} entities")
            return entities
            
        except Exception as e:
            self.progress_tracker.stop_tracking(tracking_id, status="failed", message=str(e))
            raise
    
    def _extract_with_spacy(self, text: str, min_confidence: float, entity_types: Optional[List[str]]) -> List[Entity]:
        """Extract entities using spaCy."""
        entities = []
        
        doc = self.nlp(text)
        
        for ent in doc.ents:
            # Filter by entity types if specified
            if entity_types and ent.label_ not in entity_types:
                continue
            
            # Get confidence if available
            confidence = 1.0
            if hasattr(ent, 'confidence'):
                confidence = ent.confidence
            elif hasattr(ent, 'score'):
                confidence = ent.score
            
            if confidence >= min_confidence:
                entities.append(Entity(
                    text=ent.text,
                    label=ent.label_,
                    start_char=ent.start_char,
                    end_char=ent.end_char,
                    confidence=confidence,
                    metadata={
                        "lemma": ent.lemma_ if hasattr(ent, 'lemma_') else ent.text
                    }
                ))
        
        return entities
    
    def _extract_fallback(self, text: str) -> List[Entity]:
        """Fallback entity extraction using simple patterns."""
        entities = []
        
        # Simple patterns for common entity types
        patterns = {
            "PERSON": r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b',
            "ORG": r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\s+(?:Inc|Corp|LLC|Ltd|Company))\b',
            "GPE": r'\b([A-Z][a-z]+\s*(?:City|State|Country|Nation))\b',
            "DATE": r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4})\b'
        }
        
        import re
        for label, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    text=match.group(1),
                    label=label,
                    start_char=match.start(),
                    end_char=match.end(),
                    confidence=0.7,  # Lower confidence for pattern-based
                    metadata={"extraction_method": "pattern"}
                ))
        
        return entities
    
    def extract_entities_batch(self, texts: List[str], **options) -> List[List[Entity]]:
        """
        Extract entities from multiple texts.
        
        Args:
            texts: List of input texts
            **options: Extraction options
            
        Returns:
            list: List of entity lists for each text
        """
        return [self.extract_entities(text, **options) for text in texts]
    
    def classify_entities(self, entities: List[Entity]) -> Dict[str, List[Entity]]:
        """
        Classify entities by type.
        
        Args:
            entities: List of entities
            
        Returns:
            dict: Entities grouped by type
        """
        classified = {}
        for entity in entities:
            if entity.label not in classified:
                classified[entity.label] = []
            classified[entity.label].append(entity)
        
        return classified
    
    def filter_by_confidence(self, entities: List[Entity], min_confidence: float) -> List[Entity]:
        """
        Filter entities by confidence score.
        
        Args:
            entities: List of entities
            min_confidence: Minimum confidence threshold
            
        Returns:
            list: Filtered entities
        """
        return [e for e in entities if e.confidence >= min_confidence]
