# 🚀 FalkorDB Fork of Graphiti

> **IMPORTANT**: This is a fork of [Graphiti](https://github.com/getzep/graphiti) that replaces Neo4j with FalkorDB and adds critical features for production use.

## 🎯 What This Fork Provides

### 1. **FalkorDB as Primary Database** (Neo4j Replacement)
- **Problem with Neo4j**: Community Edition lacks vector search (`vector.similarity.cosine` requires Enterprise license)
- **Solution**: FalkorDB has native vector support via `vecf32` type - no license restrictions
- **Benefits**: 
  - Smaller Docker image
  - Faster startup
  - Native vector operations out of the box
  - Full open source

### 2. **Fulltext Search on Relationships**
- **Problem**: FalkorDB v4.2.2 doesn't support `db.idx.fulltext.queryRelationships` ([planned in Issue #1211](https://github.com/FalkorDB/FalkorDB/issues/1211))
- **Solution**: Implemented FactIndex pattern for fulltext search on facts
- **How it works**:
  ```cypher
  # Instead of (not available in FalkorDB):
  CALL db.idx.fulltext.queryRelationships('RELATES_TO', 'search query')
  
  # We use:
  CALL db.idx.fulltext.queryNodes('FactIndex', 'search query')
  YIELD node, score
  MATCH (n)-[e:RELATES_TO {uuid: node.fact_id}]->(m)
  ```
- **Supports all RediSearch operators**: wildcards (*), phrases (""), OR (|), NOT (-)

### 3. **Relevance Score in Results**
- **Problem**: Original Graphiti calculates score but doesn't return it
- **Solution**: Modified search methods to include score in results
- **Usage**: `edge.score` is now available in search results for filtering

## 📦 Quick Start with FalkorDB

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

# Connect to FalkorDB (instead of Neo4j)
driver = FalkorDriver(
    host="localhost",
    port=6379,
    password=""  # or your password
)

# Everything else works the same!
graphiti = Graphiti(graph_driver=driver)

# Add data
await graphiti.add_episode(
    name="Company Facts",
    episode_body="Tesla was founded by Elon Musk in 2003.",
    source_description="Business data"
)

# Search with relevance scores
results = await graphiti.search("Tesla founded*")
for edge in results:
    print(f"Fact: {edge.fact}")
    print(f"Score: {edge.score}")  # Now available!
```

## 🔧 Technical Details

### FactIndex Implementation
Located in: `graphiti_core/search/search_utils.py::edge_fulltext_search()`

When relationships are created, corresponding FactIndex nodes are automatically generated:
```python
FactIndexNode(
    fact_id=edge.uuid,      # Links to original relationship
    text=edge.fact,         # Full text for search
    text_lower=fact.lower(), # Case-insensitive search
    keywords=keywords,       # Extracted keywords
    group_id=edge.group_id  # For filtering
)
```

### Modified Files
- `graphiti_core/utils/bulk_utils.py` - Creates FactIndex nodes
- `graphiti_core/search/search_utils.py` - Implements FactIndex search
- `graphiti_core/graph_queries.py` - FalkorDB-specific queries
- `graphiti_core/nodes.py` - Added FactIndexNode class

## 🔗 Related Projects

- **[graphiti-api](https://github.com/vlad29042/graphiti-api)** - Production HTTP API wrapper with FastAPI
- **Original Graphiti**: See below for the complete original documentation

---

<p align="center">
  <a href="https://www.getzep.com/">
    <img src="https://github.com/user-attachments/assets/119c5682-9654-4257-8922-56b7cb8ffd73" width="150" alt="Zep Logo">
  </a>
</p>

<h1 align="center">
Graphiti
</h1>
<h2 align="center"> Build Real-Time Knowledge Graphs for AI Agents</h2>
<div align="center">

[![Lint](https://github.com/getzep/Graphiti/actions/workflows/lint.yml/badge.svg?style=flat)](https://github.com/getzep/Graphiti/actions/workflows/lint.yml)
[![Unit Tests](https://github.com/getzep/Graphiti/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/getzep/Graphiti/actions/workflows/unit_tests.yml)
[![MyPy Check](https://github.com/getzep/Graphiti/actions/workflows/typecheck.yml/badge.svg)](https://github.com/getzep/Graphiti/actions/workflows/typecheck.yml)

![GitHub Repo stars](https://img.shields.io/github/stars/getzep/graphiti)
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?&logo=discord&logoColor=white)](https://discord.com/invite/W8Kw6bsgXQ)
[![arXiv](https://img.shields.io/badge/arXiv-2501.13956-b31b1b.svg?style=flat)](https://arxiv.org/abs/2501.13956)
[![Release](https://img.shields.io/github/v/release/getzep/graphiti?style=flat&label=Release&color=limegreen)](https://github.com/getzep/graphiti/releases)

</div>
<div align="center">

<a href="https://trendshift.io/repositories/12986" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12986" alt="getzep%2Fgraphiti | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

</div>

:star: _Help us reach more developers and grow the Graphiti community. Star this repo!_

<br />

> [!TIP]
> Check out the new [MCP server for Graphiti](mcp_server/README.md)! Give Claude, Cursor, and other MCP clients powerful Knowledge Graph-based memory.

Graphiti is a framework for building and querying temporally-aware knowledge graphs, specifically tailored for AI agents operating in dynamic environments. Unlike traditional retrieval-augmented generation (RAG) methods, Graphiti continuously integrates user interactions, structured and unstructured enterprise data, and external information into a coherent, queryable graph. The framework supports incremental data updates, efficient retrieval, and precise historical queries without requiring complete graph recomputation, making it suitable for developing interactive, context-aware AI applications.

Use Graphiti to:

- Integrate and maintain dynamic user interactions and business data.
- Facilitate state-based reasoning and task automation for agents.
- Query complex, evolving data with semantic, keyword, and graph-based search methods.

<br />

<p align="center">
    <img src="images/graphiti-graph-intro.gif" alt="Graphiti temporal walkthrough" width="700px">   
</p>

<br />

A knowledge graph is a network of interconnected facts, such as _"Kendra loves Adidas shoes."_ Each fact is a "triplet" represented by two entities, or
nodes ("Kendra", "Adidas shoes"), and their relationship, or edge ("loves"). Knowledge Graphs have been explored
extensively for information retrieval. What makes Graphiti unique is its ability to autonomously build a knowledge graph
while handling changing relationships and maintaining historical context.

## Graphiti and Zep's Context Engineering Platform.

Graphiti powers the core of [Zep](https://www.getzep.com), a turn-key context engineering platform for AI Agents. Zep offers agent memory, Graph RAG for dynamic data, and context retrieval and assembly.

Using Graphiti, we've demonstrated Zep is
the [State of the Art in Agent Memory](https://blog.getzep.com/state-of-the-art-agent-memory/).

Read our paper: [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956).

We're excited to open-source Graphiti, believing its potential reaches far beyond AI memory applications.

<p align="center">
    <a href="https://arxiv.org/abs/2501.13956"><img src="images/arxiv-screenshot.png" alt="Zep: A Temporal Knowledge Graph Architecture for Agent Memory" width="700px"></a>
</p>

## Why Graphiti?

Traditional RAG approaches often rely on batch processing and static data summarization, making them inefficient for frequently changing data. Graphiti addresses these challenges by providing:

- **Real-Time Incremental Updates:** Immediate integration of new data episodes without batch recomputation.
- **Bi-Temporal Data Model:** Explicit tracking of event occurrence and ingestion times, allowing accurate point-in-time queries.
- **Efficient Hybrid Retrieval:** Combines semantic embeddings, keyword (BM25), and graph traversal to achieve low-latency queries without reliance on LLM summarization.
- **Custom Entity Definitions:** Flexible ontology creation and support for developer-defined entities through straightforward Pydantic models.
- **Scalability:** Efficiently manages large datasets with parallel processing, suitable for enterprise environments.

<p align="center">
    <img src="/images/graphiti-intro-slides-stock-2.gif" alt="Graphiti structured + unstructured demo" width="700px">   
</p>

## Graphiti vs. GraphRAG

| Aspect                     | GraphRAG                              | Graphiti                                         |
| -------------------------- | ------------------------------------- | ------------------------------------------------ |
| **Primary Use**            | Static document summarization         | Dynamic data management                          |
| **Data Handling**          | Batch-oriented processing             | Continuous, incremental updates                  |
| **Knowledge Structure**    | Entity clusters & community summaries | Episodic data, semantic entities, communities    |
| **Retrieval Method**       | Sequential LLM summarization          | Hybrid semantic, keyword, and graph-based search |
| **Adaptability**           | Low                                   | High                                             |
| **Temporal Handling**      | Basic timestamp tracking              | Explicit bi-temporal tracking                    |
| **Contradiction Handling** | LLM-driven summarization judgments    | Temporal edge invalidation                       |
| **Query Latency**          | Seconds to tens of seconds            | Typically sub-second latency                     |
| **Custom Entity Types**    | No                                    | Yes, customizable                                |
| **Scalability**            | Moderate                              | High, optimized for large datasets               |

## Requirements

- Python 3.10 - 3.12
- LLM Provider API access (OpenAI, Anthropic, Gemini, Groq, or compatible)
- An embedding model (Voyage, OpenAI, or compatible)
- Graph Database (Neo4j or FalkorDB) [**Fork Note**: FalkorDB recommended]

### Database Prerequisites

#### Neo4j

- Recommended: Use [Neo4j Desktop](https://neo4j.com/download/) for local development
- Alternatively: Create a cloud instance at [Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database)
- Requires APOC plugin for enhanced functionality

#### FalkorDB [**Fork Note**: Preferred for this fork]

- Start FalkorDB using Docker:
  ```bash
  docker run -p 6379:6379 falkordb/falkordb:v4.3.0
  ```

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

First, install Graphiti:

```bash
pip install graphiti-core
```

**Fork Note**: To use this FalkorDB fork instead:
```bash
pip install git+https://github.com/vlad29042/graphiti.git
```

Then set up your graph database:

```python
# Original Neo4j setup
from graphiti_core.driver.neo4j_driver import Neo4jDriver

neo4j_driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="your-password"
)

# FalkorDB setup (this fork)
from graphiti_core.driver.falkordb_driver import FalkorDriver

falkor_driver = FalkorDriver(
    host="localhost",
    port=6379,
    password=""  # optional
)
```

Now you can create your Graphiti instance and start building your knowledge graph:

```python
from graphiti_core import Graphiti
from graphiti_core.clients import OpenAIClient
from graphiti_core.embedder import OpenAIEmbedder

# Initialize clients
llm_client = OpenAIClient()
embedder = OpenAIEmbedder()

# Create Graphiti instance
graphiti = Graphiti(
    driver=falkor_driver,  # or neo4j_driver
    llm_client=llm_client,
    embedder=embedder
)

# Add your first episode
await graphiti.add_episode(
    name="User preferences",
    episode_body="Emma loves sushi and enjoys hiking on weekends",
    source_description="User survey"
)

# Search the knowledge graph
results = await graphiti.search("What does Emma enjoy?")
print(results)
```

## Key Features

### Temporal Awareness

Track how facts evolve:

```python
# Day 1: Add initial information
await graphiti.add_episode(
    name="Tech Trends 2024",
    episode_body="Currently, React is the most popular frontend framework",
    source_description="Industry Report",
    reference_time=datetime(2024, 1, 15)
)

# Day 30: Add updated information
await graphiti.add_episode(
    name="Tech Trends Update",
    episode_body="Vue.js has overtaken React as the most popular frontend framework",
    source_description="Industry Report",
    reference_time=datetime(2024, 2, 15)
)

# Query at different points in time
facts_in_january = await graphiti.search(
    "most popular frontend framework",
    reference_time=datetime(2024, 1, 20)
)
# Returns: React is the most popular

facts_in_february = await graphiti.search(
    "most popular frontend framework",
    reference_time=datetime(2024, 2, 20)
)
# Returns: Vue.js is the most popular
```

### Entity Resolution

Graphiti automatically resolves entities across different contexts:

```python
await graphiti.add_episode(
    name="Meeting Notes",
    episode_body="The CEO of TechCorp announced a new AI product",
    source_description="Board Meeting"
)

await graphiti.add_episode(
    name="Industry News",
    episode_body="John Smith, who leads TechCorp, spoke at the AI conference",
    source_description="Tech Conference"
)

# Graphiti recognizes "CEO of TechCorp" and "John Smith who leads TechCorp" 
# as the same entity and creates unified node relationships
```

### Semantic + Graph Search

Combine vector similarity with graph traversal:

```python
# Create rich interconnected data
await graphiti.add_episode(
    name="Product Launch",
    episode_body="""TechCorp's new AI assistant uses RAG architecture. 
    The assistant was developed by the AI Research team led by Dr. Sarah Chen.""",
    source_description="Press Release"
)

# Search using natural language
results = await graphiti.search(
    "Who developed TechCorp's RAG system?",
    num_results=5
)
# Automatically finds connections through semantic similarity and graph relationships
```

## Advanced Usage

### Custom Entity Types

Define domain-specific entities:

```python
from pydantic import BaseModel, Field
from graphiti_core.nodes import EntityNode
from typing import Literal

class ProductNode(EntityNode):
    """Custom node type for products"""
    label: Literal["Product"] = Field(default="Product")
    price: float | None = Field(description="Product price in USD")
    category: str | None = Field(description="Product category")

# Register custom entity
graphiti = Graphiti(
    driver=driver,
    llm_client=llm_client,
    embedder=embedder,
    entity_types={
        "Product": ProductNode
    }
)

# The LLM will now extract and create ProductNodes with price and category fields
await graphiti.add_episode(
    name="Product Catalog",
    episode_body="The new iPhone 15 Pro costs $999 and belongs to the smartphone category",
    source_description="Apple Store"
)
```

### Graph Schema Definition

Control relationship types and connections:

```python
graphiti = Graphiti(
    driver=driver,
    llm_client=llm_client,
    embedder=embedder,
    # Define allowed relationship types between entities
    edge_type_map={
        ("User", "Product"): ["PURCHASED", "WANTS", "REVIEWED"],
        ("Product", "Category"): ["BELONGS_TO"],
        ("User", "User"): ["FOLLOWS", "FRIEND_OF"]
    }
)
```

### Search Configuration

Fine-tune search behavior:

```python
from graphiti_core.search import SearchConfig

config = SearchConfig(
    max_results=20,
    min_score=0.7,  # Minimum similarity score
    traversal_depth=3,  # How deep to traverse relationships
    include_neighbors=True,  # Include connected nodes
    semantic_weight=0.7,  # Balance between semantic and graph scores
)

results = await graphiti.search(
    "Emma's friends who like sushi",
    search_config=config
)
```

## Architecture

Graphiti is built on a modular architecture:

- **LLM Client**: Interfaces with language models for entity extraction and resolution
- **Embedder**: Creates vector representations for semantic search
- **Driver**: Manages database connections (Neo4j or FalkorDB)
- **Search Engine**: Hybrid retrieval combining vectors, keywords, and graph traversal

The pipeline for adding information:

1. **Episode Processing**: Raw text is processed to extract entities and relationships
2. **Entity Resolution**: Entities are matched against existing nodes or created
3. **Embedding Generation**: Text chunks and entities are embedded for semantic search
4. **Graph Construction**: Nodes and edges are created with temporal metadata
5. **Index Updates**: Search indices are updated for efficient retrieval

## Best Practices

### 1. Meaningful Episode Names

```python
# Good: Descriptive and searchable
await graphiti.add_episode(
    name="Q3 2024 Sales Meeting - Customer Feedback",
    episode_body="...",
    source_description="Quarterly Business Review"
)

# Avoid: Generic names
await graphiti.add_episode(
    name="Meeting Notes",
    episode_body="...",
    source_description="Meeting"
)
```

### 2. Consistent Entity References

```python
# Help entity resolution by using consistent naming
episode_body = """
Dr. Sarah Chen from the AI Research team presented the new model.
The model developed by Dr. Chen's team shows 95% accuracy.
"""  # "Dr. Sarah Chen" and "Dr. Chen" will be resolved to the same entity
```

### 3. Time-Based Organization

```python
from datetime import datetime, timedelta

# Add historical data with proper timestamps
historical_data = [
    ("Tech evolved from mainframes", datetime(1950, 1, 1)),
    ("Personal computers emerged", datetime(1980, 1, 1)),
    ("Internet became mainstream", datetime(1995, 1, 1)),
    ("Cloud computing took over", datetime(2010, 1, 1))
]

for content, time in historical_data:
    await graphiti.add_episode(
        name=f"Tech History - {time.year}",
        episode_body=content,
        source_description="Historical Records",
        reference_time=time
    )
```

### 4. Leverage Graph Relationships

```python
# Create rich, interconnected episodes that build relationships
await graphiti.add_episode(
    name="Team Structure",
    episode_body="""
    Sarah leads the AI team. John works under Sarah.
    The AI team collaborates with the Data Engineering team led by Mike.
    """,
    source_description="Org Chart"
)

# Later, you can traverse these relationships
results = await graphiti.search("Who does John report to?")
```

## Performance Optimization

### Bulk Operations

```python
episodes = [
    {
        "name": f"Customer Feedback {i}",
        "episode_body": feedback,
        "source_description": "Support Ticket"
    }
    for i, feedback in enumerate(feedback_list)
]

# Process multiple episodes efficiently
await graphiti.add_episodes(episodes)
```

### Search Optimization

```python
# Use filters to narrow search scope
from graphiti_core.search import SearchFilters

filters = SearchFilters(
    date_range=(datetime(2024, 1, 1), datetime(2024, 12, 31)),
    entity_types=["Person", "Organization"],
    required_properties={"status": "active"}
)

results = await graphiti.search(
    "active team members",
    filters=filters
)
```

## Community and Support

- [Discord Community](https://discord.com/invite/W8Kw6bsgXQ): Join for discussions and support
- [GitHub Issues](https://github.com/getzep/graphiti/issues): Report bugs or request features
- [Documentation](https://docs.getzep.com/graphiti): Comprehensive guides and API reference

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up the development environment
- Running tests
- Submitting pull requests
- Code style guidelines

## License

Graphiti is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for the full license text.

---

Built with ❤️ by the [Zep](https://www.getzep.com) team