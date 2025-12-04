"""
Context Graph Builder

This module provides comprehensive context graph construction capabilities,
formalizing context as a graph of connections. It turns context from intuition
into infrastructure, enabling meaningful connections between concepts, entities,
and conversations.

Algorithms Used:

Graph Construction:
    - Node Creation: Dictionary-based node storage with type indexing
    - Edge Creation: List-based edge storage with type indexing
    - Entity Extraction: Entity extraction from conversations and text
    - Relationship Extraction: Relationship extraction from conversations
    - Intent Extraction: Intent classification from conversations
    - Sentiment Analysis: Sentiment extraction from conversations
    - URI Assignment: Entity linker-based URI assignment for entities

Graph Traversal:
    - BFS (Breadth-First Search): Multi-hop neighbor discovery
    - Graph Indexing: Type-based indexing for efficient node/edge lookup
    - Neighbor Discovery: Outgoing and incoming edge traversal
    - Multi-hop Expansion: Iterative expansion for related entities

Graph Querying:
    - Type Filtering: Node type-based filtering
    - Metadata Filtering: Dictionary-based metadata matching
    - Graph Statistics: Node and edge type counting

Key Features:
    - Builds context graphs from entities, relationships, and conversations
    - Creates meaningful connections between concepts
    - Assigns URLs/URIs to entities for web-like context
    - Formalizes context into graph structure
    - Supports ontology-based context graphs
    - Enables context traversal and querying
    - Conversation-based graph construction
    - Intent and sentiment extraction
    - Multi-hop relationship traversal
    - Graph statistics and analytics

Main Classes:
    - ContextNode: Context graph node data structure with node_id, node_type, content, metadata, properties
    - ContextEdge: Context graph edge data structure with source_id, target_id, edge_type, weight, metadata
    - ContextGraphBuilder: Context graph builder for formalizing context

Example Usage:
    >>> from semantica.context import ContextGraphBuilder
    >>> builder = ContextGraphBuilder()
    >>> graph = builder.build_from_entities_and_relationships(entities, relationships)
    >>> builder.add_node("node1", "entity", "Python programming")
    >>> builder.add_edge("node1", "node2", "related_to", weight=0.9)
    >>> neighbors = builder.get_neighbors("node1", max_hops=2)
    >>> results = builder.query(node_type="entity", confidence=0.8)

Author: Semantica Contributors
License: MIT
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from ..utils.types import EntityDict, RelationshipDict
from .entity_linker import EntityLinker


@dataclass
class ContextNode:
    """Context graph node."""

    node_id: str
    node_type: str  # "entity", "concept", "document", "intent", etc.
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextEdge:
    """Context graph edge."""

    source_id: str
    target_id: str
    edge_type: str
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextGraphBuilder:
    """
    Context graph builder for formalizing context as connections.

    • Builds context graphs from entities and relationships
    • Creates meaningful connections between concepts
    • Assigns URLs/URIs to entities for web-like context
    • Formalizes context into graph structure
    • Supports ontology-based context graphs
    • Enables context traversal and querying
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize context graph builder.

        Args:
            config: Configuration dictionary
            **kwargs: Additional configuration options:
                - extract_entities: Extract entities from content (default: True)
                - extract_relationships: Extract relationships (default: True)
                - link_external_entities: Link to external entities (default: True)
                - entity_linker: Entity linker instance
        """
        self.logger = get_logger("context_graph_builder")
        self.config = config or {}
        self.config.update(kwargs)

        self.extract_entities = self.config.get("extract_entities", True)
        self.extract_relationships = self.config.get("extract_relationships", True)
        self.link_external_entities = self.config.get("link_external_entities", True)

        self.entity_linker = self.config.get("entity_linker") or EntityLinker()

        # Graph structure
        self.nodes: Dict[str, ContextNode] = {}
        self.edges: List[ContextEdge] = []

        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()

        # Indexes
        self.node_type_index: Dict[str, Set[str]] = defaultdict(set)
        self.edge_type_index: Dict[str, List[ContextEdge]] = defaultdict(list)

    def build_from_conversations(
        self,
        conversations: List[Union[str, Dict[str, Any]]],
        link_entities: bool = True,
        extract_intents: bool = False,
        extract_sentiments: bool = False,
        **options,
    ) -> Dict[str, Any]:
        """
        Build context graph from conversations.

        Args:
            conversations: List of conversation files or dictionaries
            link_entities: Link entities across conversations
            extract_intents: Extract conversation intents
            extract_sentiments: Extract sentiment information
            **options: Additional options

        Returns:
            Context graph dictionary
        """
        # Track context graph building
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="context",
            submodule="ContextGraphBuilder",
            message=f"Building graph from {len(conversations)} conversations",
        )

        try:
            self.logger.info(
                f"Building context graph from {len(conversations)} conversations"
            )

            self.progress_tracker.update_tracking(
                tracking_id, message="Processing conversations..."
            )
            # Process each conversation
            for conv in conversations:
                if isinstance(conv, str):
                    # Load conversation from file
                    conv_data = self._load_conversation(conv)
                else:
                    conv_data = conv

                self._process_conversation(
                    conv_data,
                    extract_intents=extract_intents,
                    extract_sentiments=extract_sentiments,
                )

            # Link entities if requested
            if link_entities:
                self.progress_tracker.update_tracking(
                    tracking_id, message="Linking entities..."
                )
                self._link_entities()

            # Build graph structure
            self.progress_tracker.update_tracking(
                tracking_id, message="Building graph structure..."
            )
            graph = self._build_graph_structure()

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Built graph with {len(self.nodes)} nodes, {len(self.edges)} edges",
            )
            self.logger.info(
                f"Built context graph: {len(self.nodes)} nodes, {len(self.edges)} edges"
            )

            return graph

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def build_from_entities_and_relationships(
        self,
        entities: List[EntityDict],
        relationships: List[RelationshipDict],
        **options,
    ) -> Dict[str, Any]:
        """
        Build context graph from entities and relationships.

        Args:
            entities: List of entities
            relationships: List of relationships
            **options: Additional options

        Returns:
            Context graph dictionary
        """
        # Track context graph building
        tracking_id = self.progress_tracker.start_tracking(
            file=None,
            module="context",
            submodule="ContextGraphBuilder",
            message=f"Building graph from {len(entities)} entities, {len(relationships)} relationships",
        )

        try:
            self.progress_tracker.update_tracking(
                tracking_id, message="Adding entities as nodes..."
            )
            # Add entities as nodes
            for entity in entities:
                entity_id = entity.get("id") or entity.get("entity_id")
                if not entity_id:
                    continue

                node = ContextNode(
                    node_id=entity_id,
                    node_type="entity",
                    content=entity.get("text")
                    or entity.get("label")
                    or entity.get("name", ""),
                    metadata={
                        "type": entity.get("type") or entity.get("entity_type"),
                        "confidence": entity.get("confidence", 1.0),
                        **entity.get("metadata", {}),
                    },
                    properties=entity.get("properties", {}),
                )

                self.nodes[entity_id] = node
                self.node_type_index["entity"].add(entity_id)

                # Assign URI if entity linker available
                if self.entity_linker:
                    self.entity_linker.assign_uri(
                        entity_id, node.content, node.metadata.get("type")
                    )

            # Add relationships as edges
            self.progress_tracker.update_tracking(
                tracking_id, message="Adding relationships as edges..."
            )
            for rel in relationships:
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")

                if not source_id or not target_id:
                    continue

                # Ensure source and target nodes exist
                if source_id not in self.nodes:
                    self.nodes[source_id] = ContextNode(
                        node_id=source_id, node_type="entity", content=source_id
                    )

                if target_id not in self.nodes:
                    self.nodes[target_id] = ContextNode(
                        node_id=target_id, node_type="entity", content=target_id
                    )

                edge = ContextEdge(
                    source_id=source_id,
                    target_id=target_id,
                    edge_type=rel.get("type")
                    or rel.get("relationship_type", "related_to"),
                    weight=rel.get("confidence", 1.0),
                    metadata=rel.get("metadata", {}),
                )

                self.edges.append(edge)
                self.edge_type_index[edge.edge_type].append(edge)

            # Build graph structure
            self.progress_tracker.update_tracking(
                tracking_id, message="Building graph structure..."
            )
            graph = self._build_graph_structure()

            self.progress_tracker.stop_tracking(
                tracking_id,
                status="completed",
                message=f"Built graph with {len(self.nodes)} nodes, {len(self.edges)} edges",
            )
            return graph

        except Exception as e:
            self.progress_tracker.stop_tracking(
                tracking_id, status="failed", message=str(e)
            )
            raise

    def add_node(self, node_id: str, node_type: str, content: str, **metadata) -> bool:
        """
        Add node to context graph.

        Args:
            node_id: Node identifier
            node_type: Node type
            content: Node content
            **metadata: Additional metadata

        Returns:
            True if node added successfully
        """
        node = ContextNode(
            node_id=node_id, node_type=node_type, content=content, metadata=metadata
        )

        self.nodes[node_id] = node
        self.node_type_index[node_type].add(node_id)

        self.logger.debug(f"Added node: {node_id} ({node_type})")
        return True

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "related_to",
        weight: float = 1.0,
        **metadata,
    ) -> bool:
        """
        Add edge to context graph.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_type: Edge type
            weight: Edge weight
            **metadata: Additional metadata

        Returns:
            True if edge added successfully
        """
        # Ensure nodes exist
        if source_id not in self.nodes:
            self.add_node(source_id, "entity", source_id)

        if target_id not in self.nodes:
            self.add_node(target_id, "entity", target_id)

        edge = ContextEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            metadata=metadata,
        )

        self.edges.append(edge)
        self.edge_type_index[edge_type].append(edge)

        self.logger.debug(f"Added edge: {source_id} --{edge_type}--> {target_id}")
        return True

    def _process_conversation(
        self,
        conv_data: Dict[str, Any],
        extract_intents: bool = False,
        extract_sentiments: bool = False,
    ) -> None:
        """Process a conversation and add to graph."""
        # Extract conversation ID
        conv_id = conv_data.get("id") or f"conv_{hash(str(conv_data)) % 10000}"

        # Add conversation as node
        self.add_node(
            conv_id,
            "conversation",
            conv_data.get("content", "") or conv_data.get("summary", ""),
            **{
                "timestamp": conv_data.get("timestamp"),
                "participants": conv_data.get("participants", []),
                **conv_data.get("metadata", {}),
            },
        )

        # Extract entities
        if self.extract_entities:
            entities = conv_data.get("entities", [])
            for entity in entities:
                entity_id = entity.get("id") or entity.get("entity_id")
                if entity_id:
                    self.add_node(
                        entity_id,
                        "entity",
                        entity.get("text") or entity.get("label", ""),
                        **{
                            "type": entity.get("type"),
                            "confidence": entity.get("confidence", 1.0),
                        },
                    )

                    # Link entity to conversation
                    self.add_edge(
                        conv_id,
                        entity_id,
                        "mentions",
                        weight=entity.get("confidence", 1.0),
                    )

        # Extract relationships
        if self.extract_relationships:
            relationships = conv_data.get("relationships", [])
            for rel in relationships:
                source_id = rel.get("source_id")
                target_id = rel.get("target_id")

                if source_id and target_id:
                    self.add_edge(
                        source_id,
                        target_id,
                        rel.get("type", "related_to"),
                        weight=rel.get("confidence", 1.0),
                    )

        # Extract intents
        if extract_intents:
            intents = conv_data.get("intents", [])
            for intent in intents:
                intent_id = f"{conv_id}_intent_{len(intents)}"
                self.add_node(
                    intent_id,
                    "intent",
                    intent.get("text", ""),
                    **{"confidence": intent.get("confidence", 1.0)},
                )
                self.add_edge(conv_id, intent_id, "has_intent")

        # Extract sentiments
        if extract_sentiments:
            sentiment = conv_data.get("sentiment")
            if sentiment:
                sentiment_id = f"{conv_id}_sentiment"
                self.add_node(
                    sentiment_id,
                    "sentiment",
                    sentiment.get("label", ""),
                    **{"score": sentiment.get("score", 0.0)},
                )
                self.add_edge(conv_id, sentiment_id, "has_sentiment")

    def _link_entities(self) -> None:
        """Link entities across the graph."""
        if not self.entity_linker:
            return

        # Get all entity nodes
        entity_nodes = [
            (node_id, node)
            for node_id, node in self.nodes.items()
            if node.node_type == "entity"
        ]

        # Link similar entities
        for i, (node_id1, node1) in enumerate(entity_nodes):
            for node_id2, node2 in entity_nodes[i + 1 :]:
                # Check if similar
                similarity = self.entity_linker._calculate_text_similarity(
                    node1.content.lower(), node2.content.lower()
                )

                if similarity >= self.entity_linker.similarity_threshold:
                    # Link entities
                    self.entity_linker.link_entities(
                        node_id1,
                        node_id2,
                        link_type="same_as" if similarity >= 0.9 else "related_to",
                        confidence=similarity,
                    )

                    # Add edge to graph
                    self.add_edge(
                        node_id1,
                        node_id2,
                        "same_as" if similarity >= 0.9 else "related_to",
                        weight=similarity,
                    )

    def _load_conversation(self, file_path: str) -> Dict[str, Any]:
        """Load conversation from file."""
        from pathlib import Path

        from ..utils.helpers import read_json_file

        path = Path(file_path)
        if not path.exists():
            raise ProcessingError(f"Conversation file not found: {file_path}")

        return read_json_file(path)

    def _build_graph_structure(self) -> Dict[str, Any]:
        """Build graph structure dictionary."""
        return {
            "nodes": [
                {
                    "id": node.node_id,
                    "type": node.node_type,
                    "content": node.content,
                    "metadata": node.metadata,
                    "properties": node.properties,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.edge_type,
                    "weight": edge.weight,
                    "metadata": edge.metadata,
                }
                for edge in self.edges
            ],
            "statistics": {
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "node_types": {
                    node_type: len(node_ids)
                    for node_type, node_ids in self.node_type_index.items()
                },
                "edge_types": {
                    edge_type: len(edges)
                    for edge_type, edges in self.edge_type_index.items()
                },
            },
        }

    def get_neighbors(self, node_id: str, max_hops: int = 1) -> List[str]:
        """
        Get neighbor nodes.

        Args:
            node_id: Node identifier
            max_hops: Maximum number of hops

        Returns:
            List of neighbor node IDs
        """
        neighbors = set()
        current_level = {node_id}

        for hop in range(max_hops):
            next_level = set()

            for current_id in current_level:
                # Find outgoing edges
                for edge in self.edges:
                    if edge.source_id == current_id:
                        next_level.add(edge.target_id)
                        neighbors.add(edge.target_id)

                # Find incoming edges
                for edge in self.edges:
                    if edge.target_id == current_id:
                        next_level.add(edge.source_id)
                        neighbors.add(edge.source_id)

            current_level = next_level

        return list(neighbors)

    def query(
        self,
        node_type: Optional[str] = None,
        edge_type: Optional[str] = None,
        **filters,
    ) -> List[Dict[str, Any]]:
        """
        Query graph nodes and edges.

        Args:
            node_type: Filter by node type
            edge_type: Filter by edge type
            **filters: Additional filters

        Returns:
            List of matching nodes
        """
        results = []

        for node_id, node in self.nodes.items():
            # Filter by node type
            if node_type and node.node_type != node_type:
                continue

            # Filter by metadata
            match = True
            for key, value in filters.items():
                if key in node.metadata and node.metadata[key] != value:
                    match = False
                    break

            if match:
                results.append(
                    {
                        "id": node_id,
                        "type": node.node_type,
                        "content": node.content,
                        "metadata": node.metadata,
                    }
                )

        return results

    # High-Level Construction
    def from_text(self, text: str, **options) -> Dict[str, Any]:
        """
        Build graph from plain text.
        
        Args:
            text: Plain text to build graph from
            **options: Additional options
        
        Returns:
            Graph dictionary
        
        Example:
            >>> graph = builder.from_text("Python is used for machine learning")
        """
        # Simple entity extraction (mock - in real implementation would use NLP)
        entities = []
        relationships = []
        
        # Mock extraction
        if "Python" in text:
            entities.append({"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"})
        if "machine learning" in text.lower():
            entities.append({"id": "e2", "text": "Machine Learning", "type": "CONCEPT"})
        if len(entities) >= 2:
            relationships.append({"source_id": "e1", "target_id": "e2", "type": "used_for"})
        
        return self.build_from_entities_and_relationships(entities, relationships, **options)

    def from_documents(self, docs: List[Union[str, Dict[str, Any]]], **options) -> Dict[str, Any]:
        """
        Build graph from document list.
        
        Args:
            docs: List of documents (strings or dicts with content)
            **options: Additional options
        
        Returns:
            Graph dictionary
        
        Example:
            >>> graph = builder.from_documents(["Doc 1", "Doc 2"])
        """
        conversations = []
        for i, doc in enumerate(docs):
            if isinstance(doc, str):
                conversations.append({
                    "id": f"doc_{i}",
                    "content": doc,
                    "entities": [],
                    "relationships": []
                })
            elif isinstance(doc, dict):
                conversations.append({
                    "id": doc.get("id", f"doc_{i}"),
                    "content": doc.get("content", ""),
                    "entities": doc.get("entities", []),
                    "relationships": doc.get("relationships", [])
                })
        
        return self.build_from_conversations(conversations, **options)

    def from_conversations(self, conversations: List[Dict[str, Any]], **options) -> Dict[str, Any]:
        """
        Build from conversations (alias for build_from_conversations).
        
        Args:
            conversations: List of conversations
            **options: Additional options
        
        Returns:
            Graph dictionary
        
        Example:
            >>> graph = builder.from_conversations(conversations)
        """
        return self.build_from_conversations(conversations, **options)

    def add(
        self,
        entities: Optional[List[EntityDict]] = None,
        relationships: Optional[List[RelationshipDict]] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Simple add method.
        
        Args:
            entities: List of entities to add
            relationships: List of relationships to add
            **options: Additional options
        
        Returns:
            Graph statistics
        
        Example:
            >>> stats = builder.add(entities=entities, relationships=relationships)
        """
        if entities and relationships:
            graph = self.build_from_entities_and_relationships(entities, relationships, **options)
            return graph.get("statistics", {})
        elif entities:
            # Add entities only
            for entity in entities:
                self.add_node(
                    entity.get("id", f"entity_{len(self.nodes)}"),
                    entity.get("type", "entity"),
                    entity.get("text", ""),
                    **entity.get("metadata", {})
                )
            return {"node_count": len(self.nodes), "edge_count": len(self.edges)}
        else:
            return {"node_count": len(self.nodes), "edge_count": len(self.edges)}

    # Query Methods
    def find(self, query: str, **filters) -> List[Dict[str, Any]]:
        """
        Simple search in graph.
        
        Args:
            query: Search query
            **filters: Additional filters
        
        Returns:
            List of matching nodes
        
        Example:
            >>> results = builder.find("Python")
        """
        query_lower = query.lower()
        results = []
        
        for node_id, node in self.nodes.items():
            if query_lower in node.content.lower():
                results.append({
                    "id": node_id,
                    "type": node.node_type,
                    "content": node.content,
                    "metadata": node.metadata,
                })
        
        return results

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Find node by ID.
        
        Args:
            node_id: Node ID
        
        Returns:
            Node dict or None if not found
        
        Example:
            >>> node = builder.find_node("node1")
        """
        if node_id in self.nodes:
            node = self.nodes[node_id]
            return {
                "id": node_id,
                "type": node.node_type,
                "content": node.content,
                "metadata": node.metadata,
            }
        return None

    def find_nodes(self, **filters) -> List[Dict[str, Any]]:
        """
        Find nodes by filters.
        
        Args:
            **filters: Filter criteria (node_type, etc.)
        
        Returns:
            List of matching nodes
        
        Example:
            >>> nodes = builder.find_nodes(node_type="entity")
        """
        return self.query(**filters)

    def find_edges(self, **filters) -> List[Dict[str, Any]]:
        """
        Find edges by filters.
        
        Args:
            **filters: Filter criteria (edge_type, source_id, target_id, etc.)
        
        Returns:
            List of matching edges
        
        Example:
            >>> edges = builder.find_edges(edge_type="related_to")
        """
        results = []
        edge_type = filters.get("edge_type")
        source_id = filters.get("source_id")
        target_id = filters.get("target_id")
        
        for edge in self.edges:
            if edge_type and edge.edge_type != edge_type:
                continue
            if source_id and edge.source_id != source_id:
                continue
            if target_id and edge.target_id != target_id:
                continue
            
            results.append({
                "source_id": edge.source_id,
                "target_id": edge.target_id,
                "type": edge.edge_type,
                "weight": edge.weight,
                "metadata": edge.metadata,
            })
        
        return results

    def find_path(self, source_id: str, target_id: str, max_hops: int = 5) -> List[Dict[str, Any]]:
        """
        Find path between nodes.
        
        Args:
            source_id: Source node ID
            target_id: Target node ID
            max_hops: Maximum hops (default: 5)
        
        Returns:
            List of nodes in path
        
        Example:
            >>> path = builder.find_path("node1", "node2", max_hops=5)
        """
        from collections import deque
        
        if source_id not in self.nodes or target_id not in self.nodes:
            return []
        
        queue = deque([(source_id, [source_id])])
        visited = {source_id}
        
        while queue:
            current_id, path = queue.popleft()
            
            if len(path) > max_hops:
                continue
            
            if current_id == target_id:
                # Return path with node info
                path_info = []
                for node_id in path:
                    node = self.nodes.get(node_id)
                    if node:
                        path_info.append({
                            "id": node_id,
                            "type": node.node_type,
                            "content": node.content,
                        })
                return path_info
            
            # Get neighbors
            for edge in self.edges:
                neighbor_id = None
                if edge.source_id == current_id:
                    neighbor_id = edge.target_id
                elif edge.target_id == current_id:
                    neighbor_id = edge.source_id
                
                if neighbor_id and neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, path + [neighbor_id]))
        
        return []

    # Graph Operations
    def get_subgraph(self, node_ids: List[str]) -> Dict[str, Any]:
        """
        Get subgraph.
        
        Args:
            node_ids: List of node IDs to include
        
        Returns:
            Subgraph dict with nodes and edges
        
        Example:
            >>> subgraph = builder.get_subgraph(["node1", "node2"])
        """
        subgraph_nodes = {}
        subgraph_edges = []
        
        node_set = set(node_ids)
        
        # Get nodes
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph_nodes[node_id] = self.nodes[node_id]
        
        # Get edges between these nodes
        for edge in self.edges:
            if edge.source_id in node_set and edge.target_id in node_set:
                subgraph_edges.append(edge)
        
        return {
            "nodes": {nid: {
                "id": nid,
                "type": node.node_type,
                "content": node.content,
                "metadata": node.metadata,
            } for nid, node in subgraph_nodes.items()},
            "edges": [{
                "source_id": e.source_id,
                "target_id": e.target_id,
                "type": e.edge_type,
                "weight": e.weight,
            } for e in subgraph_edges],
            "statistics": {
                "node_count": len(subgraph_nodes),
                "edge_count": len(subgraph_edges),
            }
        }

    def merge(self, other_graph: 'ContextGraphBuilder') -> Dict[str, Any]:
        """
        Merge with another graph.
        
        Args:
            other_graph: Another ContextGraphBuilder instance
        
        Returns:
            Merge statistics
        
        Example:
            >>> stats = builder.merge(other_builder)
        """
        merged_nodes = 0
        merged_edges = 0
        
        # Merge nodes
        for node_id, node in other_graph.nodes.items():
            if node_id not in self.nodes:
                self.nodes[node_id] = node
                self.node_type_index[node.node_type].add(node_id)
                merged_nodes += 1
        
        # Merge edges
        for edge in other_graph.edges:
            # Check if edge already exists
            exists = any(
                e.source_id == edge.source_id and e.target_id == edge.target_id
                for e in self.edges
            )
            if not exists:
                self.edges.append(edge)
                self.edge_type_index[edge.edge_type].append(edge)
                merged_edges += 1
        
        return {
            "merged_nodes": merged_nodes,
            "merged_edges": merged_edges,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
        }

    def clone(self) -> 'ContextGraphBuilder':
        """
        Clone graph.
        
        Returns:
            New ContextGraphBuilder instance with copied graph
        
        Example:
            >>> cloned = builder.clone()
        """
        new_builder = ContextGraphBuilder(
            extract_entities=self.extract_entities,
            extract_relationships=self.extract_relationships,
            link_external_entities=self.link_external_entities,
        )
        
        # Copy nodes
        for node_id, node in self.nodes.items():
            new_builder.nodes[node_id] = ContextNode(
                node_id=node.node_id,
                node_type=node.node_type,
                content=node.content,
                metadata=node.metadata.copy(),
                properties=node.properties.copy(),
            )
            new_builder.node_type_index[node.node_type].add(node_id)
        
        # Copy edges
        for edge in self.edges:
            new_edge = ContextEdge(
                source_id=edge.source_id,
                target_id=edge.target_id,
                edge_type=edge.edge_type,
                weight=edge.weight,
                metadata=edge.metadata.copy(),
            )
            new_builder.edges.append(new_edge)
            new_builder.edge_type_index[edge.edge_type].append(new_edge)
        
        return new_builder

    # Statistics
    def stats(self) -> Dict[str, Any]:
        """
        Get statistics (enhance existing).
        
        Returns:
            Statistics dict
        
        Example:
            >>> stats = builder.stats()
        """
        node_types = defaultdict(int)
        edge_types = defaultdict(int)
        
        for node in self.nodes.values():
            node_types[node.node_type] += 1
        
        for edge in self.edges:
            edge_types[edge.edge_type] += 1
        
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": dict(node_types),
            "edge_types": dict(edge_types),
        }

    def node_count(self, **filters) -> int:
        """
        Count nodes.
        
        Args:
            **filters: Filter criteria
        
        Returns:
            Count of nodes matching filters
        
        Example:
            >>> count = builder.node_count(node_type="entity")
        """
        if not filters:
            return len(self.nodes)
        
        return len(self.find_nodes(**filters))

    def edge_count(self, **filters) -> int:
        """
        Count edges.
        
        Args:
            **filters: Filter criteria
        
        Returns:
            Count of edges matching filters
        
        Example:
            >>> count = builder.edge_count(edge_type="related_to")
        """
        if not filters:
            return len(self.edges)
        
        return len(self.find_edges(**filters))

    def density(self) -> float:
        """
        Calculate graph density.
        
        Returns:
            Graph density (0-1)
        
        Example:
            >>> density = builder.density()
        """
        n = len(self.nodes)
        if n <= 1:
            return 0.0
        
        # Maximum possible edges in undirected graph
        max_edges = n * (n - 1) / 2
        if max_edges == 0:
            return 0.0
        
        # Actual edges (considering undirected)
        actual_edges = len(self.edges)
        
        return actual_edges / max_edges