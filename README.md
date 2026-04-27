# yandex_py

Python-клиент для Yandex API на базе httpx и pydantic.

Сейчас библиотека организована по продуктам. Текущая реализация покрывает `yandex_py.direct`.

## Установка

```bash
pip install yandex_py
```

## Использование

```python
from yandex_py.direct import DirectClient
from yandex_py.direct.reports.types import (
    DateRangeType, FieldName, Page,
    ReportDefinition, ReportRequest, ReportType, SelectionCriteria,
)

request = ReportRequest(
    params=ReportDefinition(
        selection_criteria=SelectionCriteria(),
        field_names=[FieldName.Date, FieldName.Clicks, FieldName.Cost],
        report_name="my-report",
        report_type=ReportType.CUSTOM_REPORT,
        date_range_type=DateRangeType.LAST_7_DAYS,
        page=Page(limit=10000),
    )
)

async with DirectClient(token="your_token", client_login="your_login") as client:
    rows = await client.reports.fetch(request)
```
