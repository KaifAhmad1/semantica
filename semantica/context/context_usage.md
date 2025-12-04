# Context Module Usage Guide

This guide demonstrates how to use the context module for building context graphs, managing agent memory, retrieving context, and linking entities for intelligent agents.

## Table of Contents

1. [High-Level Interface (Quick Start)](#high-level-interface-quick-start)
2. [Basic Usage](#basic-usage)
3. [Context Graph Construction](#context-graph-construction)
4. [Agent Memory Management](#agent-memory-management)
5. [Context Retrieval](#context-retrieval)
6. [Entity Linking](#entity-linking)
7. [Using Methods](#using-methods)
8. [Using Registry](#using-registry)
9. [Configuration](#configuration)
10. [Advanced Examples](#advanced-examples)

## High-Level Interface (Quick Start)

The `AgentContext` class provides a simplified, generic interface for common use cases. It uses generic method names (`store`, `retrieve`, `forget`, `conversation`) that auto-detect content types and retrieval strategies.

### Simple RAG

```python
from semantica.context import AgentContext

# Initialize with vector store
context = AgentContext(vector_store=vs)

# Store a memory
memory_id = context.store("User likes Python programming", conversation_id="conv1")

# Retrieve context
results = context.retrieve("Python programming", max_results=5)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']:.2f}")
```

### GraphRAG

```python
# Initialize with vector store and knowledge graph
context = AgentContext(vector_store=vs, knowledge_graph=kg)

# Store documents (auto-builds graph)
documents = [
    "Python is a programming language used for machine learning",
    "TensorFlow and PyTorch are popular ML frameworks",
    "Machine learning involves training models on data"
]

stats = context.store(
    documents,
    extract_entities=True,      # Extract entities from documents
    extract_relationships=True,  # Extract relationships
    link_entities=True          # Link entities across documents
)

print(f"Stored {stats['stored_count']} documents")
print(f"Built graph with {stats['graph_nodes']} nodes and {stats['graph_edges']} edges")

# Retrieve with graph context (auto-detects GraphRAG)
results = context.retrieve(
    "Python machine learning",
    use_graph=None,              # Auto-detect (uses graph since knowledge_graph available)
    include_entities=True,       # Include related entities
    expand_graph=True            # Use graph expansion
)

for result in results:
    print(f"Content: {result['content']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Related entities: {len(result.get('related_entities', []))}")
```

### Agent Memory Management

```python
context = AgentContext(vector_store=vs, retention_days=30)

# Store multiple memories in a conversation
context.store("Hello, I'm interested in Python", conversation_id="conv1", user_id="user123")
context.store("What can you tell me about machine learning?", conversation_id="conv1", user_id="user123")
context.store("I prefer TensorFlow over PyTorch", conversation_id="conv1", user_id="user123")

# Get conversation history
history = context.conversation(
    "conv1",
    reverse=True,           # Most recent first
    include_metadata=True   # Include full metadata
)

for item in history:
    print(f"{item['timestamp']}: {item['content']}")

# Retrieve context from conversation
results = context.retrieve(
    "Python",
    conversation_id="conv1",  # Filter by conversation
    max_results=3
)

# Delete old memories
deleted_count = context.forget(days_old=90)
print(f"Deleted {deleted_count} old memories")
```

### Boolean Flags for Common Options

The `AgentContext` class uses boolean flags to simplify common operations:

**Store Method:**
- `extract_entities: bool = True` - Extract entities from documents
- `extract_relationships: bool = True` - Extract relationships
- `link_entities: bool = True` - Link entities across documents
- `auto_extract: bool = False` - Auto-extract entities/relationships if not provided

**Retrieve Method:**
- `use_graph: Optional[bool] = None` - Auto-detect if None, True/False to force
- `include_entities: bool = True` - Include related entities in results
- `include_relationships: bool = False` - Include relationships in results
- `expand_graph: bool = True` - Use graph expansion
- `deduplicate: bool = True` - Deduplicate results

**Conversation Method:**
- `reverse: bool = False` - Reverse chronological order
- `include_metadata: bool = True` - Include full metadata

**Helper Methods:**
- `get_memory(memory_id)` - Get specific memory by ID
- `stats()` - Get memory statistics
- `link(text, entities, ...)` - Link entities in text
- `build_graph(...)` - Build context graph manually

**Example with Flags:**

```python
# Store documents without entity extraction
stats = context.store(
    documents,
    extract_entities=False,      # Skip entity extraction
    extract_relationships=False   # Skip relationship extraction
)

# Retrieve with vector-only (no graph)
results = context.retrieve(
    "Python",
    use_graph=False,              # Force vector-only retrieval
    include_entities=False        # Don't include entities
)

# Retrieve with graph but no expansion
results = context.retrieve(
    "Python",
    use_graph=True,               # Force graph retrieval
    expand_graph=False            # Disable graph expansion
)
```

### Additional Helper Methods

```python
# Get a specific memory by ID
memory = context.get_memory("mem123")
if memory:
    print(f"Content: {memory['content']}")
    print(f"Metadata: {memory['metadata']}")

# Get statistics about stored memories
stats = context.stats()
print(f"Total memories: {stats['total_items']}")
print(f"By type: {stats.get('items_by_type', {})}")

# Link entities in text (requires knowledge_graph)
linked = context.link(
    "Python is used for machine learning",
    entities=[
        {"id": "e1", "text": "Python", "type": "PROGRAMMING_LANGUAGE"},
        {"id": "e2", "text": "Machine Learning", "type": "CONCEPT"}
    ],
    similarity_threshold=0.8
)
for entity in linked:
    print(f"{entity['text']}: {entity['uri']} ({entity['linked_count']} links)")

# Build graph manually from entities and relationships
graph_stats = context.build_graph(
    entities=entities,
    relationships=relationships,
    link_entities=True
)
print(f"Graph: {graph_stats.get('node_count', 0)} nodes, {graph_stats.get('edge_count', 0)} edges")
```

### Auto-Detection

The `AgentContext` class automatically detects:

1. **Content Type in `store()`:**
   - Single string → Memory item
   - List of strings/dicts → Documents

2. **Retrieval Strategy in `retrieve()`:**
   - If `knowledge_graph` available → GraphRAG (hybrid retrieval)
   - Otherwise → Simple RAG (vector only)

3. **Graph Usage:**
   - If `use_graph=None` → Auto-detect based on `knowledge_graph` availability
   - If `use_graph=True` → Force graph retrieval (requires `knowledge_graph`)
   - If `use_graph=False` → Force vector-only retrieval

### Additional Memory Management Methods

```python
context = AgentContext(vector_store=vs, knowledge_graph=kg)

# Check if memory exists
if context.exists("mem123"):
    print("Memory exists")

# Get memory count
total = context.count()
conv_count = context.count(conversation_id="conv1")

# Get memory by ID (alias for get_memory)
memory = context.get("mem123")

# Update memory
context.update("mem123", content="Updated content", metadata={"key": "value"})

# Delete memory (alias for forget with memory_id)
context.delete("mem123")

# Clear memories with filters (alias for forget)
deleted = context.clear(conversation_id="conv1")
deleted = context.clear(days_old=90)

# List memories with pagination
memories = context.list(conversation_id="conv1", limit=50, offset=10)

# Batch operations
ids = context.batch_store(["Item 1", "Item 2", "Item 3"])
deleted = context.batch_delete(["mem1", "mem2"])
updated = context.batch_update([
    {"memory_id": "mem1", "content": "New content"},
    {"memory_id": "mem2", "metadata": {"key": "value"}}
])
```

### Additional Search Methods

```python
# Simple search (alias for retrieve)
results = context.search("Python", max_results=10)

# Find similar content
similar = context.find_similar("Python programming", limit=5)

# Get context for query
context_data = context.get_context("Python", max_results=10)

# Expand query with graph context
expanded = context.expand_query("Python", max_hops=3)
```

### Additional Conversation Methods

```python
# Get conversation (alias for conversation)
conv = context.get_conversation("conv1", limit=50)

# List all conversations
conversations = context.list_conversations(user_id="user123", limit=50)

# Delete entire conversation
deleted = context.delete_conversation("conv1")

# Get conversation summary
summary = context.conversation_summary("conv1")
print(f"Messages: {summary['message_count']}")
print(f"First: {summary['first_message']}")
print(f"Last: {summary['last_message']}")
```

### Export/Import Methods

```python
# Export memories
data = context.export(conversation_id="conv1", format='json')
data = context.export(format='dict')

# Import memories
imported = context.import_data(data, format='json')

# Backup and restore
backup_data = context.backup()
restored = context.restore(backup_data)
```

### Statistics and Analytics

```python
# Get statistics (enhanced)
stats = context.stats()
stats = context.stats(conversation_id="conv1")

# Check system health
health = context.health()
print(f"Status: {health['status']}")
print(f"Total memories: {health['total_memories']}")

# Get usage statistics
usage = context.usage_stats(period='week')
print(f"Recent memories: {usage['recent_memories']}")
```

### Accessing Underlying Components

You can still access underlying components for advanced use cases:

```python
context = AgentContext(vector_store=vs, knowledge_graph=kg)

# Access underlying components
memory = context.memory          # AgentMemory instance
retriever = context.retriever   # ContextRetriever instance (if knowledge_graph available)
graph_builder = context.graph_builder  # ContextGraphBuilder instance (if knowledge_graph available)

# Use low-level methods
memory.store("Custom memory", metadata={"custom": "data"})
results = retriever.retrieve("query", max_results=10)
```

## Basic Usage

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

### Additional Graph Construction Methods

```python
from semantica.context import ContextGraphBuilder

builder = ContextGraphBuilder()

# High-level construction
graph = builder.from_text("Python is used for machine learning")
graph = builder.from_documents(["Doc 1", "Doc 2"])
graph = builder.from_conversations(conversations)
stats = builder.add(entities=entities, relationships=relationships)

# Query methods
results = builder.find("Python")
node = builder.find_node("node1")
nodes = builder.find_nodes(node_type="entity")
edges = builder.find_edges(edge_type="related_to")
path = builder.find_path("node1", "node2", max_hops=5)

# Graph operations
subgraph = builder.get_subgraph(["node1", "node2"])
merge_stats = builder.merge(other_builder)
cloned = builder.clone()

# Statistics
stats = builder.stats()
node_count = builder.node_count(node_type="entity")
edge_count = builder.edge_count(edge_type="related_to")
density = builder.density()
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

### Additional Memory Management Methods

```python
from semantica.context import AgentMemory

memory = AgentMemory(vector_store=vs, knowledge_graph=kg)

# Basic operations
exists = memory.exists("mem123")
count = memory.count()
count = memory.count(conversation_id="conv1")
memory_item = memory.get("mem123")
memory.update("mem123", content="Updated", metadata={"key": "value"})
memory.delete("mem123")
deleted = memory.clear(conversation_id="conv1")

# Search methods
results = memory.search("Python", max_results=10)
similar = memory.find_similar("Python programming", limit=5)
by_entity = memory.find_by_entity("entity_123", limit=10)
by_relationship = memory.find_by_relationship("related_to", limit=10)

# List and filter methods
memories = memory.list(conversation_id="conv1", limit=50, offset=10)
conv_memories = memory.get_by_conversation("conv1", limit=100)
user_memories = memory.get_by_user("user123", limit=100)
recent = memory.get_recent(limit=10)
by_date = memory.get_by_date("2024-01-01", "2024-12-31", limit=100)
by_type = memory.get_by_type("conversation", limit=100)

# Batch operations
ids = memory.batch_store(["Item 1", "Item 2"])
deleted = memory.batch_delete(["mem1", "mem2"])
updated = memory.batch_update([{"memory_id": "mem1", "content": "New"}])

# Export/import
data = memory.export(conversation_id="conv1", format='json')
imported = memory.import_data(data, format='json')

# Statistics
stats = memory.stats(conversation_id="conv1")
type_counts = memory.count_by_type()
user_counts = memory.count_by_user()
conv_counts = memory.count_by_conversation()
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

### Additional Retrieval Methods

```python
from semantica.context import ContextRetriever

retriever = ContextRetriever(memory_store=memory, knowledge_graph=kg, vector_store=vs)

# Search methods
results = retriever.search("Python", max_results=10)
vector_results = retriever.vector_search("Python")
graph_results = retriever.graph_search("Python")
memory_results = retriever.memory_search("Python")
hybrid_results = retriever.hybrid_search("Python")

# Advanced retrieval
similar = retriever.find_similar("Python programming", limit=5)
context = retriever.get_context("Python", max_results=5)
expanded = retriever.expand_query("Python", max_hops=3)
related = retriever.get_related("entity_123", max_hops=2)
path = retriever.get_path("entity_1", "entity_2", max_hops=5)

# Filter methods
by_entity = retriever.filter_by_entity("entity_123", "Python")
by_type = retriever.filter_by_type("PROGRAMMING_LANGUAGE", "Python")
by_date = retriever.filter_by_date("2024-01-01", "2024-12-31", "Python")
by_score = retriever.filter_by_score(0.7, "Python")

# Batch operations
batch_results = retriever.batch_search(["Python", "Java", "C++"])
batch_contexts = retriever.batch_get_context(["Python", "Java"], max_results=5)
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

# Get entity URI
uri = linker.get_entity_uri("entity_1")
if uri:
    print(f"Entity URI: {uri}")
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

### Additional Entity Linking Methods

```python
from semantica.context import EntityLinker

linker = EntityLinker(knowledge_graph=kg)

# Linking methods
linked = linker.link_text("Python is used for ML", entities=[...])
batch_linked = linker.link_batch(entities)

# Search methods
similar = linker.find_similar("Python", threshold=0.8)
by_text = linker.find_by_text("Python", threshold=0.8)
by_type = linker.find_by_type("PROGRAMMING_LANGUAGE", limit=10)
related = linker.find_related("entity_123", max_hops=2)

# URI methods
uri = linker.get_uri("entity_123")
all_uris = linker.get_all_uris()
entity = linker.resolve_uri("https://semantica.dev/entity/python")

# Statistics
link_count = linker.link_count("entity_123")
stats = linker.stats()
most_linked = linker.most_linked(limit=10)
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
from semantica.context import registry
def custom_graph_builder(entities, relationships, **kwargs):
    """Custom graph building method."""
    # Custom implementation
    return {"nodes": [], "edges": [], "statistics": {}}

# Register custom method
registry.method_registry.register("graph", "custom_builder", custom_graph_builder)

# Use custom method
from semantica.context.methods import build_context_graph
graph = build_context_graph(entities, relationships, method="custom_builder")

# List registered methods
methods = registry.method_registry.list_all("graph")
print(f"Registered graph methods: {methods}")

# Unregister method
registry.method_registry.unregister("graph", "custom_builder")
```

## Configuration

### Using Configuration

```python
from semantica.context import config

# Get configuration
retention = config.context_config.get("retention_policy", default="unlimited")
max_size = config.context_config.get("max_memory_size", default=10000)

# Set configuration
config.context_config.set("retention_policy", "30_days")
config.context_config.set("max_memory_size", 5000)

# Method-specific configuration
config.context_config.set_method_config("graph", {
    "extract_entities": True,
    "extract_relationships": True
})

method_config = config.context_config.get_method_config("graph")

# Get all configurations
all_configs = config.context_config.get_all()
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
from semantica.context import config

# Load from config file
context_config = config.ContextConfig(config_file="context_config.yaml")
```

## Advanced Examples

### Complete Agent Context Workflow

```python
from semantica.context import (
    AgentMemory,
    ContextRetriever,
    EntityLinker,
    ContextGraphBuilder
)

# Step 1: Build context graph
builder = ContextGraphBuilder()
graph = builder.build_from_entities_and_relationships(entities, relationships)

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

