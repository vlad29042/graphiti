# Graphiti with FalkorDB Support

This fork adds full FalkorDB support to Graphiti, including advanced fulltext search capabilities for relationships (facts).

## Key Features

- ✅ **Vector Search** - Works with proper scoring (0.6-0.8 range)
- ✅ **Fulltext Search on Relationships** - Using FactIndex nodes pattern
- ✅ **RediSearch Operators** - Wildcards (*), phrases (""), OR (|), NOT (-)
- ✅ **TF-IDF Scoring** - Automatic relevance scoring
- ✅ **Hybrid Search** - Combines vector and text search

## Installation

```bash
pip install git+https://github.com/vlad29042/graphiti.git
```

## Configuration

### Docker Compose for FalkorDB

```yaml
version: '3.8'
services:
  falkordb:
    image: falkordb/falkordb:v4.2.2
    ports:
      - "6379:6379"
    environment:
      - FALKORDB_CLUSTER_ENABLED=no
    volumes:
      - falkordb_data:/data
    command: redis-server --requirepass ""

volumes:
  falkordb_data:
```

### Usage with Graphiti

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

# Create FalkorDB driver
driver = FalkorDriver(
    host="localhost",
    port=6379,
    password=""  # Empty password for local development
)

# Initialize Graphiti
graphiti = Graphiti(graph_driver=driver)

# Add episodes
await graphiti.add_episode(
    name="Company Info",
    episode_body="DonKrovlyaStroy sells metal tiles for 550 rubles per square meter.",
    source_description="Business data"
)

# Search with RediSearch operators
results = await graphiti.search("metal* | tiles")  # OR search
results = await graphiti.search("\"550 rubles\"")  # Exact phrase
results = await graphiti.search("tiles -ceramic")  # Exclusion
```

## How It Works

### FactIndex Pattern

Since FalkorDB doesn't support fulltext search on relationships directly, this fork implements a FactIndex pattern:

1. When adding episodes, FactIndex nodes are created for each relationship
2. These nodes contain the full text of facts and are indexed for fulltext search
3. During search, FactIndex nodes are queried first, then original relationships are retrieved

### Search Flow

```
User Query → RediSearch on FactIndex → Get fact_id → Retrieve original RELATES_TO edge → Return with score
```

## Differences from Original

1. **No Neo4j dependency** - Works only with FalkorDB
2. **FactIndex nodes** - Additional nodes for fulltext indexing
3. **Modified search** - Uses FactIndex instead of db.idx.fulltext.queryRelationships
4. **Better scoring** - Consistent score values for ranking

## Testing

Run the comprehensive test:

```bash
python test_complex_relationships.py
```

This will demonstrate:
- Search by specific facts (amounts, percentages, technologies)
- All RediSearch operators
- Relevance scoring
- Complex relationship chains

## Performance Considerations

- FactIndex nodes add ~20% storage overhead
- Search performance is similar to Neo4j
- Indexing happens during episode addition

## License

Same as original Graphiti project.