"""
Context Engineering Module

This module provides comprehensive context engineering infrastructure for agents,
formalizing context as a graph of connections to enable meaningful agent
understanding and memory. It integrates RAG with knowledge graphs to provide
persistent context for intelligent agents.

Algorithms Used:

Context Graph Construction:
    - Graph Building: Node and edge construction from entities and relationships
    - Entity Extraction: Entity extraction from conversations and text
    - Relationship Extraction: Relationship extraction from conversations
    - Intent Extraction: Intent classification from conversations
    - Sentiment Analysis: Sentiment extraction from conversations
    - Graph Traversal: BFS/DFS for neighbor discovery and multi-hop traversal
    - Graph Indexing: Type-based indexing for efficient node/edge lookup

Agent Memory Management:
    - Vector Embedding: Embedding generation for memory items
    - Vector Search: Similarity search in vector space
    - Keyword Search: Fallback keyword-based search
    - Retention Policy: Time-based memory retention and cleanup
    - Memory Indexing: Deque-based memory index for efficient access
    - Knowledge Graph Integration: Entity and relationship updates to knowledge graph

Context Retrieval:
    - Vector Similarity Search: Cosine similarity in vector space
    - Graph Traversal: Multi-hop graph expansion for related entities
    - Memory Search: Vector and keyword search in memory store
    - Result Ranking: Score-based ranking and merging
    - Deduplication: Content-based result deduplication
    - Hybrid Scoring: Weighted combination of multiple retrieval sources

Entity Linking:
    - URI Generation: Hash-based and text-based URI assignment
    - Text Similarity: Word overlap-based similarity calculation
    - Knowledge Graph Lookup: Entity matching in knowledge graph
    - Cross-Document Linking: Entity linking across multiple documents
    - Bidirectional Linking: Symmetric relationship creation
    - Entity Web Construction: Graph-based entity connection web

Key Features:
    - Context graph construction from entities, relationships, and conversations
    - Agent memory management with RAG integration
    - Entity linking across sources with URI assignment
    - Hybrid context retrieval (vector + graph + memory)
    - Conversation history management
    - Context accumulation and synthesis
    - Graph-based context traversal and querying
    - Method registry for custom context methods
    - Configuration management with environment variables and config files

Main Classes:
    - ContextGraphBuilder: Builds context graphs from various sources
    - ContextNode: Context graph node data structure
    - ContextEdge: Context graph edge data structure
    - AgentMemory: Manages persistent agent memory with RAG
    - MemoryItem: Memory item data structure
    - EntityLinker: Links entities across sources with URIs
    - EntityLink: Entity link data structure
    - LinkedEntity: Linked entity with context
    - ContextRetriever: Retrieves relevant context from multiple sources
    - RetrievedContext: Retrieved context item data structure
    - MethodRegistry: Registry for custom context methods
    - ContextConfig: Configuration manager for context module

Convenience Functions:
    - build_context: Build context graph and manage memory in one call

Example Usage:
    >>> from semantica.context import build_context, ContextGraphBuilder, AgentMemory
    >>> # Using convenience function
    >>> result = build_context(
    ...     entities=entities,
    ...     relationships=relationships,
    ...     vector_store=vs,
    ...     knowledge_graph=kg
    ... )
    >>> # Using classes directly
    >>> builder = ContextGraphBuilder()
    >>> graph = builder.build_from_entities_and_relationships(entities, relationships)
    >>> memory = AgentMemory(vector_store=vs, knowledge_graph=kg)
    >>> memory_id = memory.store("User asked about Python", metadata={"type": "conversation"})
    >>> results = memory.retrieve("Python", max_results=5)

Author: Semantica Contributors
License: MIT
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .context_graph import ContextGraphBuilder, ContextNode, ContextEdge
from .entity_linker import EntityLinker, EntityLink, LinkedEntity
from .agent_memory import AgentMemory, MemoryItem
from .context_retriever import ContextRetriever, RetrievedContext
from .registry import MethodRegistry, method_registry
from .methods import (
    build_context_graph,
    store_memory,
    retrieve_context,
    link_entities,
    get_context_method,
    list_available_methods,
)
from .config import ContextConfig, context_config

__all__ = [
    # Main classes
    "ContextGraphBuilder",
    "ContextNode",
    "ContextEdge",
    "EntityLinker",
    "EntityLink",
    "LinkedEntity",
    "AgentMemory",
    "MemoryItem",
    "ContextRetriever",
    "RetrievedContext",
    # Registry
    "MethodRegistry",
    "method_registry",
    # Methods
    "build_context_graph",
    "store_memory",
    "retrieve_context",
    "link_entities",
    "get_context_method",
    "list_available_methods",
    # Config
    "ContextConfig",
    "context_config",
    # Convenience
    "build_context",
]


def build_context(
    entities: Optional[List[Dict[str, Any]]] = None,
    relationships: Optional[List[Dict[str, Any]]] = None,
    conversations: Optional[List[Union[str, Dict[str, Any]]]] = None,
    vector_store: Optional[Any] = None,
    knowledge_graph: Optional[Any] = None,
    graph_method: str = "entities_relationships",
    store_initial_memories: bool = False,
    **options
) -> Dict[str, Any]:
    """
    Build context graph and optionally manage memory (convenience function).
    
    This is a user-friendly wrapper that builds context graphs and optionally
    stores initial memories in one call.
    
    Args:
        entities: List of entity dictionaries
        relationships: List of relationship dictionaries
        conversations: List of conversation files or dictionaries
        vector_store: Vector store instance for memory
        knowledge_graph: Knowledge graph instance
        graph_method: Graph construction method (default: "entities_relationships")
        store_initial_memories: Whether to store initial memories from entities
        **options: Additional options passed to builders
        
    Returns:
        Dictionary containing:
            - graph: Context graph dictionary
            - memory_ids: List of stored memory IDs (if store_initial_memories=True)
            - statistics: Graph and memory statistics
            
    Examples:
        >>> from semantica.context import build_context
        >>> entities = [{"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"}]
        >>> relationships = [{"source_id": "e1", "target_id": "e2", "type": "related_to"}]
        >>> result = build_context(
        ...     entities=entities,
        ...     relationships=relationships,
        ...     vector_store=vs,
        ...     knowledge_graph=kg
        ... )
        >>> print(f"Graph has {result['graph']['statistics']['node_count']} nodes")
    """
    from ..utils.logging import get_logger
    
    logger = get_logger("context")
    
    # Build context graph
    graph = build_context_graph(
        entities=entities,
        relationships=relationships,
        conversations=conversations,
        method=graph_method,
        **options
    )
    
    memory_ids = []
    
    # Optionally store initial memories
    if store_initial_memories and vector_store:
        memory = AgentMemory(
            vector_store=vector_store,
            knowledge_graph=knowledge_graph,
            **options
        )
        
        # Store entity-based memories
        if entities:
            for entity in entities[:10]:  # Limit to first 10
                entity_text = entity.get("text") or entity.get("label") or entity.get("name", "")
                if entity_text:
                    memory_id = memory.store(
                        f"Entity: {entity_text}",
                        metadata={
                            "type": "entity",
                            "entity_id": entity.get("id"),
                            "entity_type": entity.get("type")
                        },
                        entities=[entity] if entity.get("id") else None
                    )
                    memory_ids.append(memory_id)
    
    return {
        "graph": graph,
        "memory_ids": memory_ids,
        "statistics": {
            "graph": graph.get("statistics", {}),
            "memories_stored": len(memory_ids)
        }
    }
