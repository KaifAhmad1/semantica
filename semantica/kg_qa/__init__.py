"""
Knowledge Graph Quality Assurance Module

This module provides comprehensive quality assurance capabilities for the
Semantica framework, enabling production-ready knowledge graph quality
assessment, validation, and automated fixes.

Key Features:
    - Quality metrics calculation (overall, completeness, consistency)
    - Consistency checking (logical, temporal, hierarchical)
    - Completeness validation (entity, relationship, property)
    - Automated fixes (duplicates, inconsistencies, missing properties)
    - Quality reporting with issue tracking
    - Validation engine with rules and constraints

Main Classes:
    - KGQualityAssessor: Overall quality assessment coordinator
    - ConsistencyChecker: Consistency validation engine
    - CompletenessValidator: Completeness validation engine
    - QualityMetrics: Quality metrics calculator
    - ValidationEngine: Rule and constraint validation
    - QualityReporter: Quality report generation
    - AutomatedFixer: Automated issue fixing

Example Usage:
    >>> from semantica.kg_qa import KGQualityAssessor
    >>> assessor = KGQualityAssessor()
    >>> score = assessor.assess_overall_quality(knowledge_graph)
    >>> report = assessor.generate_quality_report(knowledge_graph, schema)

Author: Semantica Contributors
License: MIT
"""

from .kg_quality_assessor import (
    KGQualityAssessor,
    ConsistencyChecker,
    CompletenessValidator,
)
from .quality_metrics import QualityMetrics, CompletenessMetrics, ConsistencyMetrics
from .validation_engine import ValidationEngine, RuleValidator, ConstraintValidator
from .reporting import QualityReporter, IssueTracker, ImprovementSuggestions, QualityReport
from .automated_fixes import AutomatedFixer, AutoMerger, AutoResolver

__all__ = [
    # Main classes
    "KGQualityAssessor",
    "ConsistencyChecker",
    "CompletenessValidator",
    # Quality metrics
    "QualityMetrics",
    "CompletenessMetrics",
    "ConsistencyMetrics",
    # Validation
    "ValidationEngine",
    "RuleValidator",
    "ConstraintValidator",
    # Reporting
    "QualityReporter",
    "IssueTracker",
    "ImprovementSuggestions",
    "QualityReport",
    # Automated fixes
    "AutomatedFixer",
    "AutoMerger",
    "AutoResolver",
]

