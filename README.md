# yandex_py
[Pypi](https://pypi.org/project/yandex_py/) — [Github](https://github.com/limepillX/)



Python-клиент для Yandex API на базе `httpx` и `pydantic`.

Библиотека организована по продуктам и сейчас покрывает:

- `yandex_py.direct.reports` - отчеты Yandex Direct
- `yandex_py.direct.campaigns` - кампании Yandex Direct (`campaigns.get`)
- `yandex_py.metrika.stat` - API статистики Yandex Metrika
- `yandex_py.metrika.management` - API управления счетчиками и целями Yandex Metrika

Поддерживаются синхронные и асинхронные вызовы, таймауты, единый transport и типизированные модели запросов и ответов.

## Установка

```bash
pip install yandex_py
```

Требуется Python `>=3.10`.

## Быстрый старт

### Yandex Direct

Асинхронный запрос отчета:

```python
from yandex_py.direct import DirectClient
from yandex_py.direct.reports.types import (
    DateRangeType,
    FieldName,
    Page,
    ReportDefinition,
    ReportRequest,
    ReportType,
    SelectionCriteria,
)

request = ReportRequest(
    params=ReportDefinition(
        selection_criteria=SelectionCriteria(),
        field_names=[FieldName.Date, FieldName.Clicks, FieldName.Cost],
        report_name="weekly-performance",
        report_type=ReportType.CUSTOM_REPORT,
        date_range_type=DateRangeType.LAST_7_DAYS,
        page=Page(limit=1000),
    )
)

async with DirectClient(
    token="your_token",
    client_login="your_client_login",
) as client:
    rows = await client.reports.fetch(request)

for row in rows:
    print(row[FieldName.Date], row[FieldName.Clicks], row[FieldName.Cost])
```

Синхронный вариант использует `client.reports.fetch_sync(request)`.

### Yandex Direct: кампании

```python
from yandex_py.direct import DirectClient

with DirectClient(token="your_token", client_login="your_client_login") as client:
    campaigns = client.campaigns.get_sync(states=["ON", "SUSPENDED"])

for campaign in campaigns:
    print(campaign.id, campaign.name, campaign.state, campaign.daily_budget)
```

Агентство: токен представителя агентства + `client_login` клиента-рекламодателя; `use_operator_units=True`
тратит баллы агентства. `client_login` можно не указывать (например, для сервиса AgencyClients).

Пагинация по `LimitedBy` выполняется автоматически. Ошибки в теле ответа с HTTP 200
(`{"error": {...}}`) тоже поднимаются как исключения (например, код 53 - `AuthenticationError`,
152 - `RateLimitError`). `get_page_sync(...).units` - баллы из заголовка `Units`
(`spent`, `remaining`, `limit`). Асинхронный вариант: `await client.campaigns.get(...)`.

### Yandex Metrika Stat API

Синхронный запрос табличной статистики:

```python
from datetime import date

from yandex_py.metrika import MetrikaClient
from yandex_py.metrika.stat.types import TableQuery

with MetrikaClient(token="your_token") as client:
    response = client.stat.table_sync(
        TableQuery(
            ids=[12345678],
            metrics=["ym:s:visits", "ym:s:users"],
            dimensions=["ym:s:trafficSource"],
            date1=date(2024, 1, 1),
            date2=date(2024, 1, 31),
            limit=100,
        )
    )

for row in response.data:
    print(row.dimensions[0].name, row.metrics)
```

Асинхронные методы:

- `await client.stat.table(query)`
- `await client.stat.by_time(query)`

### Yandex Metrika Management API

Получение целей счетчика:

```python
from yandex_py.metrika import MetrikaClient

with MetrikaClient(token="your_token") as client:
    goals = client.management.get_goals_by_counter_sync(12345678)

for goal in goals:
    print(goal.id, goal.name, goal.type, goal.status)
```

Асинхронный вариант использует `await client.management.get_goals_by_counter(counter_id)`.

## Структура API

```python
from yandex_py.direct import DirectClient
from yandex_py.metrika import MetrikaClient
```

`DirectClient`:

- `reports.fetch_sync(...)`
- `reports.fetch(...)`
- `campaigns.get_sync(...)`
- `campaigns.get(...)`
- `campaigns.get_page_sync(...)`
- `campaigns.get_page(...)`

`MetrikaClient`:

- `stat.table_sync(...)`
- `stat.table(...)`
- `stat.by_time_sync(...)`
- `stat.by_time(...)`
- `management.get_goals_by_counter_sync(...)`
- `management.get_goals_by_counter(...)`

## Обработка ошибок

Библиотека поднимает единые исключения из `yandex_py.core.errors`, например:

- `AuthenticationError`
- `RequestValidationError`
- `RateLimitError`
- `NotFoundError`
- `ServerError`
- `YandexTimeoutError`

У исключений доступны поля `product`, `http_status`, `code`, `request_id` и `raw`.

## Интеграционные тесты для Direct sandbox

По умолчанию интеграционные тесты отключены. Для запуска нужны:

- `YANDEX_DIRECT_API_TOKEN`
- `YANDEX_DIRECT_CLIENT_LOGIN`

Запуск тестов:

```bash
uv run pytest tests
```
