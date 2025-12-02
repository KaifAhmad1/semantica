"""
Graph Validation Module

This module provides comprehensive consistency validation and quality checking
capabilities for the Semantica framework, enabling validation of knowledge
graph structure and consistency.

Key Features:
    - Entity validation (required fields, unique IDs)
    - Relationship validation (valid references, required fields)
    - Consistency checking (type consistency, circular relationships)
    - Orphaned entity detection
    - Validation result reporting with errors and warnings

Main Classes:
    - GraphValidator: Main graph validation engine
    - ValidationResult: Validation result dataclass

Example Usage:
    >>> from semantica.kg import GraphValidator
    >>> validator = GraphValidator()
    >>> result = validator.validate(knowledge_graph)
    >>> is_consistent = validator.check_consistency(knowledge_graph)

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker


@dataclass
class ValidationResult:
    """
    Validation result dataclass.

    This dataclass represents the result of graph validation, containing
    validation status, errors, and warnings.

    Attributes:
        valid: Whether the graph is valid (True if no errors)
        errors: List of error messages (critical issues)
        warnings: List of warning messages (non-critical issues)
    """

    valid: bool
    errors: List[str]
    warnings: List[str]


class GraphValidator:
    """
    Graph validation engine.

    This class provides comprehensive validation capabilities for knowledge
    graphs, checking for structural consistency, required fields, valid
    references, and logical consistency.

    Features:
        - Entity validation (IDs, types, required fields)
        - Relationship validation (valid entity references)
        - Consistency checking (type consistency, circular relationships)
        - Orphaned entity detection
        - Detailed error and warning reporting

    Example Usage:
        >>> validator = GraphValidator()
        >>> result = validator.validate(knowledge_graph)
        >>> if not result.valid:
        ...     print(f"Errors: {result.errors}")
        >>> is_consistent = validator.check_consistency(knowledge_graph)
    """

    def __init__(self, **config):
        """
        Initialize graph validator.

        Sets up the validator with configuration options.

        Args:
            **config: Configuration options (currently unused)
        """
        self.logger = get_logger("graph_validator")
        self.config = config

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self.logger.debug("Graph validator initialized")

    def validate(self, knowledge_graph: Any) -> ValidationResult:
        """
        Validate knowledge graph.

        This method performs comprehensive validation of the knowledge graph,
        checking for:
        - Entity validity (required ID field, unique IDs)
        - Relationship validity (required source/target/type fields)
        - Valid entity references in relationships
        - Orphaned entities (entities with no relationships)

        Args:
            knowledge_graph: Knowledge graph instance (object with entities/relationships
                           attributes, or dict with "entities" and "relationships" keys)

        Returns:
            ValidationResult: Validation result object containing:
                - valid: True if no errors found, False otherwise
                - errors: List of error messages (critical issues)
                - warnings: List of warning messages (non-critical issues)
        """
        self.logger.info("Validating knowledge graph")

        errors = []
        warnings = []

        # Extract entities and relationships
        entities = []
        relationships = []

        if hasattr(knowledge_graph, "entities"):
            entities = knowledge_graph.entities
        elif hasattr(knowledge_graph, "get_entities"):
            entities = knowledge_graph.get_entities()
        elif isinstance(knowledge_graph, dict):
            entities = knowledge_graph.get("entities", [])
            relationships = knowledge_graph.get("relationships", [])

        if hasattr(knowledge_graph, "relationships"):
            relationships = knowledge_graph.relationships
        elif hasattr(knowledge_graph, "get_relationships"):
            relationships = knowledge_graph.get_relationships()

        # Track validation
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="kg",
            submodule="GraphValidator",
            message="Validating graph",
        )

        try:
            self.progress_tracker.update_tracking(
                tracking_id, message="Validating entities..."
            )
            # Validate entities
            entity_ids = set()
            for entity in entities:
                entity_id = entity.get("id") or entity.get("entity_id")
                if not entity_id:
                    errors.append("Entity missing required 'id' field")
                    continue

                if entity_id in entity_ids:
                    errors.append(f"Duplicate entity ID: {entity_id}")
                else:
                    entity_ids.add(entity_id)

                if not entity.get("type"):
                    warnings.append(f"Entity {entity_id} missing 'type' field")

            # Validate relationships
            for rel in relationships:
                source = rel.get("source") or rel.get("subject")
                target = rel.get("target") or rel.get("object")
                rel_type = rel.get("type") or rel.get("predicate")

                if not source:
                    errors.append("Relationship missing 'source' field")
                elif source not in entity_ids:
                    warnings.append(
                        f"Relationship references unknown source entity: {source}"
                    )

                if not target:
                    errors.append("Relationship missing 'target' field")
                elif target not in entity_ids:
                    warnings.append(
                        f"Relationship references unknown target entity: {target}"
                    )

                if not rel_type:
                    errors.append("Relationship missing 'type' field")

            self.progress_tracker.update_tracking(
                tracking_id, message="Checking for orphaned entities..."
            )
            # Check for orphaned entities (entities with no relationships)
            entity_has_relationships = set()
            for rel in relationships:
                source = rel.get("source") or rel.get("subject")
                target = rel.get("target") or rel.get("object")
                if source:
                    entity_has_relationships.add(source)
                if target:
                    entity_has_relationships.add(target)

            orphaned = entity_ids - entity_has_relationships
            if orphaned:
                warnings.append(
                    f"Found {len(orphaned)} orphaned entities (no relationships)"
                )

            valid = len(errors) == 0

            self.logger.info(
                f"Validation complete: {len(errors)} errors, {len(warnings)} warnings"
            )

            result = ValidationResult(valid=valid, errors=errors, warnings=warnings)
            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Validation complete: {len(errors)} errors, {len(warnings)} warnings",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def check_consistency(self, knowledge_graph: Any) -> bool:
        """
        Check graph consistency.

        This method performs logical consistency checking, including:
        - Type consistency (same entity should not have conflicting types)
        - Circular relationship detection
        - Basic validation checks

        Args:
            knowledge_graph: Knowledge graph instance

        Returns:
            bool: True if graph is consistent, False if inconsistencies found
        """
        self.logger.info("Checking graph consistency")

        # Use validation to check consistency
        validation_result = self.validate(knowledge_graph)

        # Check for logical inconsistencies
        # Extract entities and relationships
        entities = []
        relationships = []

        if hasattr(knowledge_graph, "entities"):
            entities = knowledge_graph.entities
        elif hasattr(knowledge_graph, "get_entities"):
            entities = knowledge_graph.get_entities()
        elif isinstance(knowledge_graph, dict):
            entities = knowledge_graph.get("entities", [])
            relationships = knowledge_graph.get("relationships", [])

        if hasattr(knowledge_graph, "relationships"):
            relationships = knowledge_graph.relationships
        elif hasattr(knowledge_graph, "get_relationships"):
            relationships = knowledge_graph.get_relationships()

        # Check for type consistency
        entity_types = {}
        for entity in entities:
            entity_id = entity.get("id") or entity.get("entity_id")
            entity_type = entity.get("type")
            if entity_id and entity_type:
                if entity_id in entity_types and entity_types[entity_id] != entity_type:
                    self.logger.warning(f"Inconsistent type for entity {entity_id}")
                    return False
                entity_types[entity_id] = entity_type

        # Check for circular relationships
        # Build adjacency list
        adjacency = {}
        for rel in relationships:
            source = rel.get("source") or rel.get("subject")
            target = rel.get("target") or rel.get("object")
            if source and target:
                if source not in adjacency:
                    adjacency[source] = []
                adjacency[source].append(target)

        # Simple cycle detection (DFS)
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)

            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        for node in adjacency:
            if node not in visited:
                if has_cycle(node, visited, set()):
                    self.logger.warning("Found circular relationship")
                    return False

        return validation_result.valid
