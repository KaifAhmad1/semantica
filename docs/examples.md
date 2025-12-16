# Examples

Real-world examples and use cases for Semantica.

!!! tip "Interactive Learning"
    For hands-on interactive tutorials, check out our [Cookbook](cookbook.md) with Jupyter notebooks covering everything from basics to advanced use cases.

---

## Example Gallery

<div class="grid cards" markdown>

-   :material-school: **Getting Started**
    ---
    Quick examples to get you up and running in 5 minutes.
    
    [View Examples](#getting-started-5-min-examples)

-   :material-cogs: **Core Workflows**
    ---
    Common workflows for building production-ready graphs.
    
    [View Examples](#core-workflows-15-min-examples)

-   :material-rocket: **Advanced Patterns**
    ---
    Complex use cases and production deployments.
    
    [View Examples](#advanced-patterns-30-min-examples)

-   :material-factory: **Production Patterns**
    ---
    Scalable deployment patterns for enterprise use.
    
    [View Examples](#production-patterns)

</div>

---

## Getting Started (5 min examples)

### Example 1: Basic Knowledge Graph

**Difficulty**: Beginner

Build a knowledge graph from a single document.

```python
from semantica.core import Semantica

semantica = Semantica()

# Build KG from PDF
result = semantica.build_knowledge_base(
    sources=["research_paper.pdf"],
    embeddings=True,
    graph=True
)

kg = result["knowledge_graph"]
print(f"Entities: {len(kg['entities'])}")
print(f"Relationships: {len(kg['relationships'])}")
```

### Example 2: Entity Extraction

**Difficulty**: Beginner

Extract entities from text using Named Entity Recognition.

```python
from semantica.core import Semantica

semantica = Semantica()
text = "Apple Inc. is a technology company founded by Steve Jobs."

entities = semantica.semantic_extract.extract_entities(text)
for entity in entities["entities"]:
    print(f"{entity['text']}: {entity['type']}")
```

### Example 3: Multi-Source Integration

**Difficulty**: Beginner

Combine data from multiple sources into a unified knowledge graph.

```python
from semantica.core import Semantica

semantica = Semantica()
sources = [
    "documents/finance_report.pdf",
    "https://example.com/news-article"
]

result = semantica.build_knowledge_base(sources)
print(f"Unified graph: {len(result['knowledge_graph']['entities'])} entities")
```

---

## Core Workflows (15 min examples)

### Example 4: Conflict Resolution

**Difficulty**: Intermediate

Resolve conflicts in data from multiple sources.

```python
from semantica.core import Semantica
from semantica.conflicts import ConflictResolver

semantica = Semantica()
result = semantica.build_knowledge_base(["source1.pdf", "source2.pdf"])

# Detect and resolve conflicts
conflicts = semantica.kg.detect_conflicts(result["knowledge_graph"])
resolver = ConflictResolver(default_strategy="voting")
resolved = resolver.resolve_conflicts(conflicts)
```

### Example 5: Custom Configuration

**Difficulty**: Intermediate

Use custom configuration for specific use cases.

```python
from semantica.core import Semantica, Config

config = Config(
    embeddings=True,
    graph=True,
    normalize=True,
    conflict_resolution="highest_confidence"
)

semantica = Semantica(config=config)
result = semantica.build_knowledge_base(["document.pdf"])
```

### Example 6: Incremental Graph Building

**Difficulty**: Intermediate

Build knowledge graph incrementally.

```python
from semantica.core import Semantica

semantica = Semantica()

# Build graphs separately
kg1 = semantica.kg.build_graph(["source1.pdf"])
kg2 = semantica.kg.build_graph(["source2.pdf"])

# Merge into unified graph
merged_kg = semantica.kg.merge([kg1, kg2])
```

---

## Advanced Patterns (30+ min examples)

### Example 7: Graph Store (Persistent Storage)

**Difficulty**: Intermediate

Store and query knowledge graphs in a persistent graph database like Neo4j.

```python
from semantica.graph_store import GraphStore

# Initialize with Neo4j
store = GraphStore(
    backend="neo4j",
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)
store.connect()

# Create nodes and relationships
apple = store.create_node(
    labels=["Company"],
    properties={"name": "Apple Inc."}
)
tim = store.create_node(
    labels=["Person"],
    properties={"name": "Tim Cook"}
)
store.create_relationship(
    start_node_id=tim["id"],
    end_node_id=apple["id"],
    rel_type="CEO_OF"
)

store.close()
```

### Example 8: FalkorDB for Real-Time Applications

**Difficulty**: Intermediate

Ultra-fast graph queries for LLM applications using FalkorDB.

```python
from semantica.graph_store import GraphStore

store = GraphStore(
    backend="falkordb",
    host="localhost",
    port=6379,
    graph_name="knowledge_graph"
)
store.connect()

# Fast queries
results = store.execute_query("MATCH (n)-[r]->(m) WHERE n.name CONTAINS 'AI' RETURN n")
store.close()
```

---

## Production Patterns

### Example 9: Streaming Data Processing

**Difficulty**: Advanced

Process data streams in real-time.

```python
from semantica.ingest import StreamIngestor
from semantica.core import Semantica

semantica = Semantica()
stream_ingestor = StreamIngestor(stream_uri="kafka://localhost:9092/topic")

for batch in stream_ingestor.stream(batch_size=100):
    result = semantica.build_knowledge_base(
        sources=batch,
        embeddings=True,
        graph=True
    )
    # Process results
```

### Example 10: Batch Processing Large Datasets

**Difficulty**: Intermediate

Process large datasets efficiently with batching.

```python
from semantica.core import Semantica

semantica = Semantica()
sources = [f"data/doc_{i}.pdf" for i in range(1000)]
batch_size = 50

for i in range(0, len(sources), batch_size):
    batch = sources[i:i+batch_size]
    result = semantica.build_knowledge_base(batch)
    # Save intermediate results
```

---

## More Resources

- **[Quick Start Guide](quickstart.md)** - Step-by-step tutorial
- **[API Reference](reference/core.md)** - Complete API documentation
- **[Cookbook](cookbook.md)** - Interactive Jupyter notebooks
- **[Use Cases](use-cases.md)** - Real-world applications

---

!!! info "Contribute"
    Have an example to share? [Contribute on GitHub](https://github.com/Hawksight-AI/semantica)

**Last Updated**: 2024
