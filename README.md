# Форк Graphiti с поддержкой FalkorDB и relevance score

## 🎯 Что добавлено в этом форке

### 1. ✅ Полная поддержка FalkorDB
- **Проблема**: Оригинальный Graphiti работает только с Neo4j, который требует Enterprise лицензию для векторного поиска
- **Решение**: Добавлена полная поддержка FalkorDB с нативным векторным поиском из коробки
- **Статус**: Полностью работает

### 2. ✅ Relevance Score в результатах поиска
- **Проблема**: Оригинальный Graphiti вычисляет score внутри запросов, но не возвращает его
- **Решение**: Добавлена передача score из базы данных в результаты поиска
- **Статус**: Реализовано и протестировано

### 3. ✅ Fulltext поиск по связям (relationships)
- **Проблема**: FalkorDB v4.2.2 не поддерживает `db.idx.fulltext.queryRelationships` (планируется в [Issue #1211](https://github.com/FalkorDB/FalkorDB/issues/1211))
- **Решение**: Реализован паттерн FactIndex для полнотекстового поиска по фактам
- **Статус**: Работает со всеми операторами RediSearch

## 📋 Детали реализации

### FactIndex Pattern

Поскольку FalkorDB пока не поддерживает нативный fulltext поиск по связям, реализовано решение через дополнительные узлы:

```python
# При добавлении фактов создаются FactIndex узлы
FactIndexNode(
    fact_id=edge.uuid,          # UUID оригинальной связи
    text=edge.fact,             # Полный текст факта
    text_lower=fact.lower(),    # Для регистронезависимого поиска
    keywords=extracted_keywords, # Ключевые слова
    group_id=edge.group_id      # Для фильтрации по контексту
)
```

### Как работает поиск

```cypher
# Вместо несуществующего в FalkorDB:
CALL db.idx.fulltext.queryRelationships('RELATES_TO', 'search query')

# Используется:
CALL db.idx.fulltext.queryNodes('FactIndex', 'search query')
YIELD node AS fact_node, score
MATCH (n:Entity)-[e:RELATES_TO {uuid: fact_node.fact_id}]->(m:Entity)
RETURN e, score
```

### Поддерживаемые операторы поиска

- **Wildcards**: `Tesla*` найдет "Tesla", "Teslas", "Tesla's"
- **Phrases**: `"founded in 2003"` для точного совпадения фразы
- **OR**: `Tesla | SpaceX` для поиска любого из терминов
- **NOT**: `Musk -Twitter` исключит результаты с "Twitter"
- **Combinations**: `"Elon Musk" Tesla* -Twitter` - сложные запросы

## 🚀 Установка

```bash
# Установка форка с поддержкой FalkorDB
pip install git+https://github.com/vlad29042/graphiti.git@main
```

## 💻 Использование

### Базовый пример

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

# Подключение к FalkorDB
driver = FalkorDriver(
    host="localhost",
    port=6379,
    password=""  # Или ваш пароль
)

# Инициализация Graphiti
graphiti = Graphiti(graph_driver=driver)

# Добавление данных
await graphiti.add_episode(
    name="Tesla Info",
    episode_body="Tesla was founded by Elon Musk in 2003. The company produces electric vehicles.",
    source_description="Company data"
)

# Поиск с relevance score
results = await graphiti.search("Tesla founded*")
for edge in results:
    print(f"Fact: {edge.fact}")
    print(f"Relevance: {edge.score}")  # Score теперь доступен!
```

### Продвинутый поиск

```python
# Гибридный поиск (vector + fulltext)
config = SearchConfig(
    edge_config=EdgeSearchConfig(
        search_methods=[
            EdgeSearchMethod.cosine_similarity,  # Векторный поиск
            EdgeSearchMethod.bm25                 # Fulltext поиск
        ],
        sim_min_score=0.7  # Минимальный score для векторного поиска
    )
)

results = await graphiti._search(
    query="electric vehicles Tesla",
    config=config,
    group_ids=["company_data"]
)
```

## 📊 Производительность

- **Storage overhead**: ~20% из-за FactIndex узлов
- **Search performance**: Сравнима с нативным fulltext поиском
- **Vector search**: Быстрее чем Neo4j Community (нативная поддержка)
- **Indexing**: Происходит при добавлении данных (не требует отдельного шага)

## 🔄 Совместимость

Форк полностью совместим с оригинальным Graphiti API. Можно безболезненно переключаться между Neo4j и FalkorDB:

```python
# Neo4j
driver = Neo4jDriver(uri="bolt://localhost:7687", ...)

# FalkorDB (этот форк)
driver = FalkorDriver(host="localhost", port=6379, ...)

# Остальной код одинаковый
graphiti = Graphiti(graph_driver=driver)
```

## 🛠️ Связанные проекты

### [graphiti-api](https://github.com/vlad29042/graphiti-api)
Production-ready HTTP API обёртка для этого форка, которая добавляет:
- RESTful endpoints для всех операций
- n8n интеграцию для workflow automation
- Изоляцию event loop для совместимости с async системами
- Docker Compose для быстрого развертывания
- OpenAPI документацию

## 🔮 Планы развития

1. **Миграция на нативный fulltext поиск** когда FalkorDB добавит `queryRelationships`
2. **Оптимизация FactIndex** - улучшение извлечения ключевых слов
3. **Расширенная фильтрация** - поддержка сложных фильтров в поиске

## 📝 Лицензия

Этот форк следует лицензии оригинального Graphiti (Apache 2.0).