# Форк Graphiti с поддержкой relevance score

## Зачем этот форк?

Этот форк добавляет возможность получения relevance score (оценки релевантности) в результатах поиска Graphiti.

### Проблема
Оригинальный Graphiti вычисляет score внутри Neo4j запросов, но не возвращает его в результатах. Это ограничивает возможности фильтрации результатов по релевантности.

### Решение
Добавлены 3 строки кода для передачи score из Neo4j в результаты поиска.

### Связанный проект
Этот форк используется в [graphiti-api](https://github.com/vlad29042/graphiti-api) - Production-ready HTTP API обёртке для Graphiti, которая решает проблемы event loop conflicts и добавляет:
- RESTful HTTP endpoints
- n8n совместимость
- Фильтрацию по relevance score

## Изменения

1. **graphiti_core/models/edges/edge_db_queries.py** (строка 102)
   - Добавлено `score AS score` в ENTITY_EDGE_RETURN

2. **graphiti_core/edges.py** (строка ~204)
   - Добавлено поле `score: float | None` в класс EntityEdge

3. **graphiti_core/edges.py** (строка ~470)
   - Добавлено извлечение score в `get_entity_edge_from_record`

## Использование

```python
# Теперь результаты поиска содержат score
results = await graphiti.search("query", group_ids=["id"])
for edge in results:
    print(f"Fact: {edge.fact}, Score: {edge.score}")
```

## Установка

```bash
pip install git+https://github.com/vlad29042/graphiti.git@main
```