"""
Conflict Detection Module

This module provides comprehensive conflict detection and resolution capabilities
for the Semantica framework, identifying conflicts from multiple sources and
providing investigation guides for discrepancies. It enables source tracking,
conflict analysis, and automated resolution strategies.

Key Features:
    - Multi-source conflict detection (value, type, relationship, temporal)
    - Source tracking and provenance management
    - Conflict analysis and pattern identification
    - Multiple resolution strategies (voting, credibility-weighted, recency)
    - Investigation guide generation
    - Source credibility scoring
    - Conflict reporting and statistics

Main Classes:
    - ConflictDetector: Detects conflicts from multiple sources
    - ConflictResolver: Resolves conflicts using various strategies
    - ConflictAnalyzer: Analyzes conflict patterns and trends
    - SourceTracker: Tracks source information and provenance
    - InvestigationGuideGenerator: Generates investigation guides

Example Usage:
    >>> from semantica.conflicts import ConflictDetector, ConflictResolver
    >>> detector = ConflictDetector()
    >>> conflicts = detector.detect_value_conflicts(entities, "name")
    >>> resolver = ConflictResolver()
    >>> results = resolver.resolve_conflicts(conflicts)

Author: Semantica Contributors
License: MIT
"""

from .conflict_detector import ConflictDetector, Conflict, ConflictType
from .source_tracker import SourceTracker, SourceReference, PropertySource
from .conflict_resolver import ConflictResolver, ResolutionResult, ResolutionStrategy
from .investigation_guide import (
    InvestigationGuideGenerator,
    InvestigationGuide,
    InvestigationStep,
)
from .conflict_analyzer import ConflictAnalyzer, ConflictPattern

__all__ = [
    "ConflictDetector",
    "Conflict",
    "ConflictType",
    "SourceTracker",
    "SourceReference",
    "PropertySource",
    "ConflictResolver",
    "ResolutionResult",
    "ResolutionStrategy",
    "InvestigationGuideGenerator",
    "InvestigationGuide",
    "InvestigationStep",
    "ConflictAnalyzer",
    "ConflictPattern",
]
