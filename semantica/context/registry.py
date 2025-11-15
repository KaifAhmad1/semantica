"""
Method Registry Module for Context Engineering

This module provides a method registry system for registering custom context engineering methods,
enabling extensibility and community contributions to the context toolkit.

Supported Registration Types:
    - Method Registry: Register custom context methods for:
        * "graph": Context graph construction methods
        * "memory": Agent memory management methods
        * "retrieval": Context retrieval methods
        * "linking": Entity linking methods

Algorithms Used:
    - Registry Pattern: Dictionary-based registration and lookup
    - Dynamic Registration: Runtime function registration
    - Type Checking: Type validation for registered components
    - Lookup Algorithms: Hash-based O(1) lookup for methods
    - Task-based Organization: Hierarchical organization by task type

Key Features:
    - Method registry for custom context methods
    - Task-based method organization (graph, memory, retrieval, linking)
    - Dynamic registration and unregistration
    - Easy discovery of available methods
    - Support for community-contributed extensions

Main Classes:
    - MethodRegistry: Registry for custom context methods

Global Instances:
    - method_registry: Global method registry instance

Example Usage:
    >>> from semantica.context.registry import method_registry
    >>> method_registry.register("graph", "custom_method", custom_graph_function)
    >>> available = method_registry.list_all("graph")

Author: Semantica Contributors
License: MIT
"""

from typing import Dict, Callable, Any, List, Optional


class MethodRegistry:
    """Registry for custom context methods."""
    
    _methods: Dict[str, Dict[str, Callable]] = {
        "graph": {},
        "memory": {},
        "retrieval": {},
        "linking": {},
    }
    
    @classmethod
    def register(cls, task: str, name: str, method_func: Callable):
        """
        Register a method for a specific task.
        
        Args:
            task: Task type ("graph", "memory", "retrieval", "linking")
            name: Method name
            method_func: Method function or callable
        """
        if task not in cls._methods:
            cls._methods[task] = {}
        cls._methods[task][name] = method_func
    
    @classmethod
    def get(cls, task: str, name: str) -> Optional[Callable]:
        """
        Get a registered method.
        
        Args:
            task: Task type
            name: Method name
            
        Returns:
            Registered method or None if not found
        """
        return cls._methods.get(task, {}).get(name)
    
    @classmethod
    def list_all(cls, task: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all registered methods.
        
        Args:
            task: Optional task type filter
            
        Returns:
            Dictionary mapping task types to method names
        """
        if task:
            return {task: list(cls._methods.get(task, {}).keys())}
        return {t: list(m.keys()) for t, m in cls._methods.items()}
    
    @classmethod
    def unregister(cls, task: str, name: str):
        """
        Unregister a method.
        
        Args:
            task: Task type
            name: Method name
        """
        if task in cls._methods and name in cls._methods[task]:
            del cls._methods[task][name]


method_registry = MethodRegistry()

