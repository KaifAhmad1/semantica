# Context Module Usage Guide

This guide demonstrates how to use the context module for building context graphs, managing agent memory, retrieving context, and linking entities for intelligent agents.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Context Graph Construction](#context-graph-construction)
3. [Agent Memory Management](#agent-memory-management)
4. [Context Retrieval](#context-retrieval)
5. [Entity Linking](#entity-linking)
6. [Using Methods](#using-methods)
7. [Using Registry](#using-registry)
8. [Configuration](#configuration)
9. [Advanced Examples](#advanced-examples)

## Basic Usage

### Using the Convenience Function

```python
from semantica.context import build_context

# Sample entities and relationships
entities = [
    {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"},
    {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"},
]
relationships = [
    {"source_id": "e1", "target_id": "e2", "type": "used_for"},
]

# Build context graph and optionally store memories
result = build_context(
    entities=entities,
    relationships=relationships,
    vector_store=vs,  # Optional vector store
    knowledge_graph=kg,  # Optional knowledge graph
    graph_method="entities_relationships",
    store_initial_memories=False
)

print(f"Graph has {result['graph']['statistics']['node_count']} nodes")
print(f"Graph has {result['graph']['statistics']['edge_count']} edges")
```

### Using Main Classes

```python
from semantica.context import ContextGraphBuilder, AgentMemory, ContextRetriever

# Step 1: Build context graph
builder = ContextGraphBuilder()
graph = builder.build_from_entities_and_relationships(entities, relationships)

# Step 2: Initialize agent memory
memory = AgentMemory(vector_store=vs, knowledge_graph=kg)
memory_id = memory.store("User asked about Python", metadata={"type": "conversation"})

# Step 3: Retrieve context
retriever = ContextRetriever(memory_store=memory, knowledge_graph=kg, vector_store=vs)
results = retriever.retrieve("Python programming", max_results=5)
```

## Context Graph Construction

### Building from Entities and Relationships

```python
from semantica.context import ContextGraphBuilder

builder = ContextGraphBuilder()

entities = [
    {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"},
    {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"},
    {"id": "e3", "text": "TensorFlow", "type": "FRAMEWORK"},
]

relationships = [
    {"source_id": "e1", "target_id": "e2", "type": "used_for", "confidence": 0.9},
    {"source_id": "e3", "target_id": "e2", "type": "implements", "confidence": 0.95},
]

graph = builder.build_from_entities_and_relationships(entities, relationships)

print(f"Nodes: {graph['statistics']['node_count']}")
print(f"Edges: {graph['statistics']['edge_count']}")
```

### Building from Conversations

```python
from semantica.context import ContextGraphBuilder

builder = ContextGraphBuilder()

conversations = [
    {
        "id": "conv1",
        "content": "User asked about Python programming",
        "entities": [
            {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"}
        ],
        "relationships": []
    },
    {
        "id": "conv2",
        "content": "User asked about machine learning",
        "entities": [
            {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"}
        ],
        "relationships": []
    }
]

graph = builder.build_from_conversations(
    conversations,
    link_entities=True,
    extract_intents=True,
    extract_sentiments=True
)
```

### Adding Nodes and Edges Manually

```python
from semantica.context import ContextGraphBuilder

builder = ContextGraphBuilder()

# Add nodes
builder.add_node("node1", "entity", "Python programming", confidence=0.9)
builder.add_node("node2", "concept", "Machine Learning", confidence=0.95)

# Add edges
builder.add_edge("node1", "node2", "related_to", weight=0.9)

# Get neighbors
neighbors = builder.get_neighbors("node1", max_hops=2)
print(f"Neighbors: {neighbors}")

# Query graph
results = builder.query(node_type="entity", confidence=0.8)
```

### Using Graph Construction Methods

```python
from semantica.context.methods import build_context_graph

# Build from entities and relationships
graph = build_context_graph(
    entities=entities,
    relationships=relationships,
    method="entities_relationships"
)

# Build from conversations
graph = build_context_graph(
    conversations=conversations,
    method="conversations"
)

# Hybrid construction
graph = build_context_graph(
    entities=entities,
    relationships=relationships,
    conversations=conversations,
    method="hybrid"
)
```

## Agent Memory Management

### Storing Memories

```python
from semantica.context import AgentMemory

memory = AgentMemory(
    vector_store=vs,
    knowledge_graph=kg,
    retention_policy="30_days",
    max_memory_size=10000
)

# Store a memory
memory_id = memory.store(
    "User asked about Python programming",
    metadata={
        "type": "conversation",
        "conversation_id": "conv_123",
        "user_id": "user_456"
    },
    entities=[
        {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"}
    ]
)

print(f"Stored memory: {memory_id}")
```

### Retrieving Memories

```python
from semantica.context import AgentMemory

memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Retrieve memories
results = memory.retrieve(
    "Python programming",
    max_results=5,
    min_score=0.5,
    type="conversation"
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Timestamp: {result['timestamp']}")
```

### Getting Specific Memory

```python
from semantica.context import AgentMemory

memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Get specific memory
memory_item = memory.get_memory("mem_abc123")
if memory_item:
    print(f"Content: {memory_item['content']}")
    print(f"Metadata: {memory_item['metadata']}")
```

### Conversation History

```python
from semantica.context import AgentMemory

memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Get conversation history
history = memory.get_conversation_history(
    conversation_id="conv_123",
    max_items=100
)

for item in history:
    print(f"{item['timestamp']}: {item['content']}")
```

### Memory Management

```python
from semantica.context import AgentMemory

memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Delete specific memory
memory.delete_memory("mem_abc123")

# Clear memories by filters
deleted_count = memory.clear_memory(
    type="conversation",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(f"Deleted {deleted_count} memories")

# Get statistics
stats = memory.get_statistics()
print(f"Total items: {stats['total_items']}")
print(f"Items by type: {stats['items_by_type']}")
```

### Using Memory Methods

```python
from semantica.context.methods import store_memory

# Store memory using method
memory_id = store_memory(
    "User asked about Python",
    vector_store=vs,
    knowledge_graph=kg,
    method="store",
    metadata={"type": "conversation"}
)

# Store conversation memory
memory_id = store_memory(
    "User asked about machine learning",
    vector_store=vs,
    knowledge_graph=kg,
    method="conversation",
    metadata={"conversation_id": "conv_123"}
)
```

## Context Retrieval

### Basic Retrieval

```python
from semantica.context import ContextRetriever

retriever = ContextRetriever(
    memory_store=memory,
    knowledge_graph=kg,
    vector_store=vs,
    use_graph_expansion=True,
    max_expansion_hops=2
)

# Retrieve context
results = retriever.retrieve(
    "Python programming",
    max_results=5,
    min_relevance_score=0.5
)

for result in results:
    print(f"Content: {result.content}")
    print(f"Score: {result.score:.2f}")
    print(f"Source: {result.source}")
    print(f"Related entities: {len(result.related_entities)}")
```

### Retrieval Methods

```python
from semantica.context.methods import retrieve_context

# Vector-based retrieval only
results = retrieve_context(
    "Python programming",
    vector_store=vs,
    method="vector",
    max_results=5
)

# Graph-based retrieval only
results = retrieve_context(
    "Python programming",
    knowledge_graph=kg,
    method="graph",
    max_results=5
)

# Memory-based retrieval only
results = retrieve_context(
    "Python programming",
    memory_store=memory,
    method="memory",
    max_results=5
)

# Hybrid retrieval (all sources)
results = retrieve_context(
    "Python programming",
    memory_store=memory,
    knowledge_graph=kg,
    vector_store=vs,
    method="hybrid",
    max_results=5
)
```

### Graph Expansion

```python
from semantica.context import ContextRetriever

retriever = ContextRetriever(
    knowledge_graph=kg,
    use_graph_expansion=True,
    max_expansion_hops=3
)

# Retrieve with graph expansion
results = retriever.retrieve(
    "Python",
    max_results=10,
    max_hops=3
)

for result in results:
    print(f"Content: {result.content}")
    print(f"Related entities: {len(result.related_entities)}")
    for entity in result.related_entities[:3]:
        print(f"  - {entity['content']} (hop: {entity['hop']})")
```

## Entity Linking

### Basic Entity Linking

```python
from semantica.context import EntityLinker

linker = EntityLinker(
    knowledge_graph=kg,
    similarity_threshold=0.8,
    base_uri="https://semantica.dev/entity/"
)

# Assign URI to entity
uri = linker.assign_uri(
    "entity_1",
    "Python",
    "PROGRAMMING_LANGUAGE"
)
print(f"URI: {uri}")

# Link entities in text
entities = [
    {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"},
    {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"},
]

linked_entities = linker.link(
    "Python is used for machine learning",
    entities=entities
)

for entity in linked_entities:
    print(f"{entity.text}: {entity.uri}")
    print(f"Linked to {len(entity.linked_entities)} entities")
```

### Explicit Entity Linking

```python
from semantica.context import EntityLinker

linker = EntityLinker(knowledge_graph=kg)

# Create explicit link
linker.link_entities(
    "entity_1",
    "entity_2",
    link_type="related_to",
    confidence=0.9,
    source="manual"
)

# Get entity links
links = linker.get_entity_links("entity_1")
for link in links:
    print(f"{link.source_entity_id} --{link.link_type}--> {link.target_entity_id}")
```

### Finding Similar Entities

```python
from semantica.context import EntityLinker

linker = EntityLinker(knowledge_graph=kg)

# Find similar entities
similar = linker.find_similar_entities(
    "Python",
    entity_type="PROGRAMMING_LANGUAGE",
    threshold=0.8
)

for entity_id, similarity in similar:
    print(f"{entity_id}: {similarity:.2f}")
```

### Building Entity Web

```python
from semantica.context import EntityLinker

linker = EntityLinker(knowledge_graph=kg)

# Link multiple entities
linker.link_entities("e1", "e2", "related_to", confidence=0.9)
linker.link_entities("e2", "e3", "related_to", confidence=0.85)

# Build entity web
web = linker.build_entity_web()

print(f"Total entities: {web['statistics']['total_entities']}")
print(f"Total links: {web['statistics']['total_links']}")

for entity_id, info in web['entities'].items():
    print(f"{entity_id}: {info['uri']} ({info['links']} links)")
```

### Using Linking Methods

```python
from semantica.context.methods import link_entities

# URI assignment only
linked = link_entities(
    entities,
    method="uri"
)

# Similarity-based linking
linked = link_entities(
    entities,
    knowledge_graph=kg,
    method="similarity"
)

# Knowledge graph-based linking
linked = link_entities(
    entities,
    knowledge_graph=kg,
    method="knowledge_graph"
)

# Cross-document linking
linked = link_entities(
    entities,
    knowledge_graph=kg,
    method="cross_document",
    context=[{"source": "doc1"}, {"source": "doc2"}]
)
```

## Using Methods

### Available Methods

```python
from semantica.context.methods import (
    build_context_graph,
    store_memory,
    retrieve_context,
    link_entities,
    get_context_method,
    list_available_methods
)

# List all available methods
all_methods = list_available_methods()
print(all_methods)

# List methods for specific task
graph_methods = list_available_methods("graph")
print(f"Graph methods: {graph_methods}")

# Get custom method
custom_method = get_context_method("graph", "custom_method")
if custom_method:
    result = custom_method(entities, relationships)
```

## Using Registry

### Registering Custom Methods

```python
from semantica.context.registry import method_registry

def custom_graph_builder(entities, relationships, **kwargs):
    """Custom graph building method."""
    # Custom implementation
    return {"nodes": [], "edges": [], "statistics": {}}

# Register custom method
method_registry.register("graph", "custom_builder", custom_graph_builder)

# Use custom method
from semantica.context.methods import build_context_graph
graph = build_context_graph(entities, relationships, method="custom_builder")

# List registered methods
methods = method_registry.list_all("graph")
print(f"Registered graph methods: {methods}")

# Unregister method
method_registry.unregister("graph", "custom_builder")
```

## Configuration

### Using Configuration

```python
from semantica.context.config import context_config

# Get configuration
retention = context_config.get("retention_policy", default="unlimited")
max_size = context_config.get("max_memory_size", default=10000)

# Set configuration
context_config.set("retention_policy", "30_days")
context_config.set("max_memory_size", 5000)

# Method-specific configuration
context_config.set_method_config("graph", {
    "extract_entities": True,
    "extract_relationships": True
})

method_config = context_config.get_method_config("graph")

# Get all configurations
all_configs = context_config.get_all()
```

### Environment Variables

```bash
# Set environment variables
export CONTEXT_RETENTION_POLICY=30_days
export CONTEXT_MAX_MEMORY_SIZE=5000
export CONTEXT_SIMILARITY_THRESHOLD=0.8
```

### Config Files

```yaml
# context_config.yaml
context:
  retention_policy: 30_days
  max_memory_size: 5000
  similarity_threshold: 0.8

context_methods:
  graph:
    extract_entities: true
    extract_relationships: true
  memory:
    retention_policy: unlimited
```

```python
from semantica.context.config import ContextConfig

# Load from config file
config = ContextConfig(config_file="context_config.yaml")
```

## Advanced Examples

### Complete Agent Context Workflow

```python
from semantica.context import (
    build_context,
    AgentMemory,
    ContextRetriever,
    EntityLinker
)

# Step 1: Build context graph
result = build_context(
    entities=entities,
    relationships=relationships,
    vector_store=vs,
    knowledge_graph=kg,
    store_initial_memories=True
)

graph = result['graph']
memory_ids = result['memory_ids']

# Step 2: Initialize memory
memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Step 3: Store conversation
conversation_id = "conv_123"
memory.store(
    "User asked about Python programming",
    metadata={
        "type": "conversation",
        "conversation_id": conversation_id
    }
)

# Step 4: Link entities
linker = EntityLinker(knowledge_graph=kg)
linked = linker.link("Python is used for machine learning", entities=entities)

# Step 5: Retrieve context
retriever = ContextRetriever(
    memory_store=memory,
    knowledge_graph=kg,
    vector_store=vs
)

results = retriever.retrieve("Python programming", max_results=5)

# Step 6: Use retrieved context
for result in results:
    print(f"Context: {result.content}")
    print(f"Relevance: {result.score:.2f}")
    if result.related_entities:
        print(f"Related: {[e['content'] for e in result.related_entities]}")
```

### Multi-Source Context Integration

```python
from semantica.context import ContextRetriever

# Initialize retriever with multiple sources
retriever = ContextRetriever(
    memory_store=memory,
    knowledge_graph=kg,
    vector_store=vs,
    hybrid_alpha=0.5  # Balance between vector and graph
)

# Retrieve with hybrid approach
results = retriever.retrieve(
    "Python machine learning frameworks",
    max_results=10,
    use_graph_expansion=True,
    max_hops=2
)

# Process results
for result in results:
    print(f"Source: {result.source}")
    print(f"Content: {result.content[:100]}...")
    print(f"Score: {result.score:.2f}")
    print(f"Related entities: {len(result.related_entities)}")
    print("---")
```

### Conversation-Based Context Building

```python
from semantica.context import ContextGraphBuilder, AgentMemory

builder = ContextGraphBuilder()
memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Process conversations
conversations = [
    {
        "id": "conv1",
        "content": "User asked about Python",
        "timestamp": "2024-01-01T10:00:00",
        "entities": [{"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"}]
    },
    {
        "id": "conv2",
        "content": "User asked about machine learning",
        "timestamp": "2024-01-01T11:00:00",
        "entities": [{"id": "e2", "text": "Machine Learning", "type": "CONCEPT"}]
    }
]

# Build graph from conversations
graph = builder.build_from_conversations(
    conversations,
    link_entities=True,
    extract_intents=True
)

# Store conversations in memory
for conv in conversations:
    memory.store(
        conv["content"],
        metadata={
            "type": "conversation",
            "conversation_id": conv["id"],
            "timestamp": conv["timestamp"]
        },
        entities=conv.get("entities", [])
    )

# Retrieve conversation history
history = memory.get_conversation_history(conversation_id="conv1")
```

### Entity Web Construction

```python
from semantica.context import EntityLinker

linker = EntityLinker(
    knowledge_graph=kg,
    similarity_threshold=0.8
)

# Link multiple entities
entities = [
    {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"},
    {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"},
    {"id": "e3", "text": "TensorFlow", "type": "FRAMEWORK"},
    {"id": "e4", "text": "PyTorch", "type": "FRAMEWORK"},
]

# Link entities
linked = linker.link("", entities=entities)

# Create explicit links
linker.link_entities("e1", "e2", "used_for", confidence=0.9)
linker.link_entities("e3", "e2", "implements", confidence=0.95)
linker.link_entities("e4", "e2", "implements", confidence=0.95)
linker.link_entities("e3", "e4", "related_to", confidence=0.8)

# Build entity web
web = linker.build_entity_web()

print(f"Entity Web Statistics:")
print(f"  Total entities: {web['statistics']['total_entities']}")
print(f"  Total links: {web['statistics']['total_links']}")

for entity_id, info in web['entities'].items():
    print(f"  {entity_id}: {info['uri']} ({info['links']} links)")
```

