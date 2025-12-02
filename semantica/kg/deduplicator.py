"""
Deduplication Module

This module provides comprehensive duplicate detection and merging capabilities
for the Semantica framework, enabling identification and resolution of duplicate
entities and relationships in knowledge graphs.

Key Features:
    - Duplicate entity detection using similarity metrics
    - Duplicate group identification
    - Entity merging with configurable strategies
    - Relationship deduplication
    - Provenance tracking for merged entities

Main Classes:
    - Deduplicator: Main deduplication engine

Example Usage:
    >>> from semantica.kg import Deduplicator
    >>> deduplicator = Deduplicator()
    >>> duplicate_groups = deduplicator.find_duplicates(entities)
    >>> merged_entities = deduplicator.merge_duplicates(duplicate_groups)

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional

from ..deduplication.duplicate_detector import DuplicateDetector, DuplicateGroup
from ..deduplication.entity_merger import EntityMerger
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


class Deduplicator:
    """
    Deduplication engine.

    This class provides duplicate detection and merging capabilities for
    knowledge graphs, using the deduplication module's duplicate detector
    and entity merger components.

    Features:
        - Duplicate entity detection with similarity metrics
        - Duplicate group identification
        - Entity merging with configurable strategies
        - Provenance tracking for merged entities

    Example Usage:
        >>> deduplicator = Deduplicator()
        >>> duplicate_groups = deduplicator.find_duplicates(entities)
        >>> merged_entities = deduplicator.merge_duplicates(duplicate_groups)
    """

    def __init__(self, **config):
        """
        Initialize deduplicator.

        Sets up the deduplicator with duplicate detector and entity merger
        components from the deduplication module.

        Args:
            **config: Configuration options:
                - detection: Configuration for duplicate detection (optional)
                - merger: Configuration for entity merging (optional)
        """
        self.logger = get_logger("deduplicator")
        self.config = config

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        # Initialize deduplication components
        self.duplicate_detector = DuplicateDetector(**config.get("detection", {}))
        self.entity_merger = EntityMerger(**config.get("merger", {}))

        self.logger.debug("Deduplicator initialized")

    def find_duplicates(
        self, entities: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        Find duplicate entities.

        This method detects duplicate entities using similarity metrics and
        groups them into duplicate groups. Uses the duplicate detector from
        the deduplication module.

        Args:
            entities: List of entity dictionaries to check for duplicates

        Returns:
            list: List of duplicate groups, where each group is a list of
                  duplicate entity dictionaries (groups with 2+ entities)
        """
        self.logger.info(f"Finding duplicates in {len(entities)} entities")

        # Track deduplication
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="kg",
            submodule="Deduplicator",
            message="Finding duplicates",
        )

        try:
            # Detect duplicate groups
            duplicate_groups = self.duplicate_detector.detect_duplicate_groups(
                entities, **self.config
            )

            # Convert to list of lists
            result = []
            for group in duplicate_groups:
                if len(group.entities) >= 2:
                    result.append(group.entities)

            self.logger.info(f"Found {len(result)} duplicate groups")
            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Found {len(result)} duplicate groups",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def merge_duplicates(
        self, duplicate_groups: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merge duplicate entities.

        This method merges groups of duplicate entities using the entity merger
        from the deduplication module. Each group is merged into a single entity
        with merged properties and provenance tracking.

        Args:
            duplicate_groups: List of duplicate groups (each group is a list
                            of duplicate entity dictionaries)

        Returns:
            list: List of merged entity dictionaries (one per duplicate group)
        """
        self.logger.info(f"Merging {len(duplicate_groups)} duplicate groups")

        merged_entities = []
        processed_ids = set()

        for group in duplicate_groups:
            if len(group) < 2:
                continue

            # Merge the group
            merge_operations = self.entity_merger.merge_duplicates(group, **self.config)

            for operation in merge_operations:
                merged_entity = operation.merged_entity
                merged_entities.append(merged_entity)

                # Mark source entities as processed
                for source_entity in operation.source_entities:
                    entity_id = source_entity.get("id") or source_entity.get(
                        "entity_id"
                    )
                    if entity_id:
                        processed_ids.add(entity_id)

        self.logger.info(f"Merged to {len(merged_entities)} entities")
        return merged_entities
