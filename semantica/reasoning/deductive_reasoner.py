"""
Deductive Reasoner Module

This module provides deductive reasoning capabilities for logical inference
and proof generation, supporting formal logic and theorem proving.

Key Features:
    - Deductive reasoning for logical inference
    - Proof generation and validation
    - Premise and conclusion management
    - Logical argument construction
    - Theorem proving
    - Confidence calculation

Main Classes:
    - DeductiveReasoner: Deductive reasoning engine
    - Premise: Dataclass for logical premises
    - Conclusion: Dataclass for logical conclusions
    - Proof: Dataclass for logical proofs
    - Argument: Dataclass for logical arguments

Example Usage:
    >>> from semantica.reasoning import DeductiveReasoner, Premise
    >>> reasoner = DeductiveReasoner()
    >>> premises = [Premise("p1", "All humans are mortal"), Premise("p2", "Socrates is human")]
    >>> conclusion = reasoner.deduce(premises, rules)
    >>> proof = reasoner.generate_proof(premises, conclusion)

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .rule_manager import Rule, RuleManager


@dataclass
class Premise:
    """Logical premise."""

    premise_id: str
    statement: Any
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conclusion:
    """Logical conclusion."""

    conclusion_id: str
    statement: Any
    premises: List[Premise] = field(default_factory=list)
    rule_applied: Optional[Rule] = None
    confidence: float = 1.0
    proof_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Proof:
    """Logical proof."""

    proof_id: str
    theorem: Any
    premises: List[Premise] = field(default_factory=list)
    steps: List[Conclusion] = field(default_factory=list)
    valid: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Argument:
    """Logical argument."""

    argument_id: str
    premises: List[Premise] = field(default_factory=list)
    conclusion: Conclusion = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeductiveReasoner:
    """
    Deductive reasoning engine.

    • Deductive reasoning algorithms
    • Logical inference and proof generation
    • Rule application and validation
    • Performance optimization
    • Error handling and recovery
    • Advanced deductive techniques
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize deductive reasoner.

        Args:
            config: Configuration dictionary
            **kwargs: Additional configuration options
        """
        self.logger = get_logger("deductive_reasoner")
        self.config = config or {}
        self.config.update(kwargs)

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        self.rule_manager = RuleManager(**self.config)
        self.known_facts: Set[Any] = set()

    def apply_logic(self, premises: List[Premise], **options) -> List[Conclusion]:
        """
        Apply logical inference rules to premises.

        Args:
            premises: List of premises
            **options: Additional options

        Returns:
            List of conclusions
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="reasoning",
            submodule="DeductiveReasoner",
            message=f"Applying logic to {len(premises)} premises",
        )

        try:
            conclusions = []

            # Add premises to known facts
            self.progress_tracker.update_tracking(
                tracking_id, message="Adding premises to knowledge base..."
            )
            for premise in premises:
                self.known_facts.add(premise.statement)

            # Apply inference rules
            self.progress_tracker.update_tracking(
                tracking_id, message="Applying inference rules..."
            )
            rules = self.rule_manager.get_all_rules()

            for rule in rules:
                # Check if rule can be applied
                if self._can_apply_rule(rule, premises):
                    conclusion = self._apply_rule_to_premises(rule, premises)
                    if conclusion:
                        conclusions.append(conclusion)
                        self.known_facts.add(conclusion.statement)

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Applied logic: {len(conclusions)} conclusions from {len(premises)} premises",
            )
            return conclusions

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _can_apply_rule(self, rule: Rule, premises: List[Premise]) -> bool:
        """Check if rule can be applied to premises."""
        # Check if all rule conditions match premises
        premise_statements = {p.statement for p in premises}

        for condition in rule.conditions:
            if (
                condition not in premise_statements
                and condition not in self.known_facts
            ):
                return False

        return True

    def _apply_rule_to_premises(
        self, rule: Rule, premises: List[Premise]
    ) -> Optional[Conclusion]:
        """Apply rule to premises and generate conclusion."""
        # Find matching premises
        matching_premises = [
            p
            for p in premises
            if p.statement in rule.conditions or p.statement in self.known_facts
        ]

        conclusion = Conclusion(
            conclusion_id=f"conc_{len(matching_premises)}",
            statement=rule.conclusion,
            premises=matching_premises,
            rule_applied=rule,
            confidence=rule.confidence,
            proof_steps=[f"Applied rule: {rule.name}"],
            metadata={"rule_id": rule.rule_id},
        )

        return conclusion

    def prove_theorem(self, theorem: Any, **options) -> Optional[Proof]:
        """
        Prove logical theorem.

        Args:
            theorem: Theorem to prove
            **options: Additional options

        Returns:
            Proof or None
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="reasoning",
            submodule="DeductiveReasoner",
            message=f"Proving theorem: {theorem}",
        )

        try:
            # Start with empty proof
            self.progress_tracker.update_tracking(
                tracking_id, message="Initializing proof..."
            )
            proof = Proof(
                proof_id=f"proof_{theorem}",
                theorem=theorem,
                premises=[],
                steps=[],
                valid=False,
            )

            # Try to prove using backward chaining
            self.progress_tracker.update_tracking(
                tracking_id, message="Attempting backward chaining proof..."
            )
            conclusion = self._prove_backward(theorem, proof, **options)

            if conclusion:
                proof.steps.append(conclusion)
                proof.valid = True
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message=f"Successfully proved theorem: {theorem}",
                )
            else:
                self.progress_tracker.stop_tracking(
                    tracking_id,
                    status="completed",
                    message=f"Could not prove theorem: {theorem}",
                )

            return proof

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def _prove_backward(
        self, goal: Any, proof: Proof, depth: int = 0, max_depth: int = 10, **options
    ) -> Optional[Conclusion]:
        """Prove goal using backward chaining."""
        if depth > max_depth:
            return None

        # Check if goal is already known
        if goal in self.known_facts:
            return Conclusion(
                conclusion_id=f"known_{goal}",
                statement=goal,
                confidence=1.0,
                proof_steps=["Known fact"],
            )

        # Find rules that can prove goal
        rules = self.rule_manager.get_all_rules()
        applicable_rules = [r for r in rules if r.conclusion == goal]

        for rule in applicable_rules:
            # Try to prove all premises
            premise_conclusions = []
            all_proven = True

            for condition in rule.conditions:
                premise_conclusion = self._prove_backward(
                    condition, proof, depth + 1, max_depth, **options
                )
                if premise_conclusion:
                    premise_conclusions.append(premise_conclusion)
                else:
                    all_proven = False
                    break

            if all_proven:
                # All premises proven, rule can fire
                conclusion = Conclusion(
                    conclusion_id=f"conc_{goal}",
                    statement=goal,
                    premises=[Premise(p, p) for p in rule.conditions],
                    rule_applied=rule,
                    confidence=rule.confidence,
                    proof_steps=[f"Proved using rule: {rule.name}"],
                )
                return conclusion

        return None

    def validate_argument(self, argument: Argument, **options) -> Dict[str, Any]:
        """
        Validate logical argument.

        Args:
            argument: Argument to validate
            **options: Additional options

        Returns:
            Validation result
        """
        tracking_id = self.progress_tracker.start_tracking(
            module="reasoning",
            submodule="DeductiveReasoner",
            message=f"Validating argument: {argument.argument_id}",
        )

        try:
            errors = []
            warnings = []

            # Check if premises are valid
            self.progress_tracker.update_tracking(
                tracking_id, message="Validating premises..."
            )
            for premise in argument.premises:
                if premise.statement not in self.known_facts:
                    warnings.append(
                        f"Premise '{premise.statement}' not in knowledge base"
                    )

            # Try to prove conclusion from premises
            self.progress_tracker.update_tracking(
                tracking_id, message="Applying logic to premises..."
            )
            conclusions = self.apply_logic(argument.premises, **options)

            valid = False
            if argument.conclusion:
                # Check if conclusion follows from premises
                self.progress_tracker.update_tracking(
                    tracking_id,
                    message="Checking if conclusion follows from premises...",
                )
                for conclusion in conclusions:
                    if conclusion.statement == argument.conclusion.statement:
                        valid = True
                        break

            result = {
                "valid": valid,
                "errors": errors,
                "warnings": warnings,
                "conclusions": conclusions,
                "argument_id": argument.argument_id,
            }

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Argument validation complete: {'Valid' if valid else 'Invalid'} ({len(warnings)} warnings)",
            )
            return result

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def add_fact(self, fact: Any) -> None:
        """Add fact to knowledge base."""
        self.known_facts.add(fact)

    def add_facts(self, facts: List[Any]) -> None:
        """Add multiple facts."""
        for fact in facts:
            self.add_fact(fact)

    def clear_facts(self) -> None:
        """Clear knowledge base."""
        self.known_facts.clear()
