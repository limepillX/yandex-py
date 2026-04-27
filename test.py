from __future__ import annotations

from pprint import pprint

import httpx

from yandex_py.metrika import MetrikaClient
from yandex_py.metrika.stat.types import TableQuery


METRIKA_TOKEN = ""
METRIKA_COUNTER_ID = 86236072
METRIKA_TIMEOUT = 60.0


def require(value: object, name: str) -> None:
    if value in ("", 0, None):
        raise ValueError(f"Fill {name} at the top of test.py")


def run_metrika_table() -> None:
    require(METRIKA_TOKEN, "METRIKA_TOKEN")
    require(METRIKA_COUNTER_ID, "METRIKA_COUNTER_ID")

    query = TableQuery(
        ids=[METRIKA_COUNTER_ID],
        metrics=["ym:s:visits", "ym:s:pageviews"],
        dimensions=["ym:s:trafficSource"],
        date1="7daysAgo",
        date2="today",
        limit=10,
    )

    try:
        with MetrikaClient(token=METRIKA_TOKEN, timeout=METRIKA_TIMEOUT) as client:
            response = client.stat.table_sync(query)
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            f"Metrika request timed out after {METRIKA_TIMEOUT} seconds. "
            "Increase METRIKA_TIMEOUT or simplify the query."
        ) from exc

    print("METRIKA TABLE")
    print(f"total_rows: {response.total_rows}")
    print(f"returned_rows: {len(response.data)}")
    if response.data:
        pprint(response.data[0].model_dump())


if __name__ == "__main__":
    run_metrika_table()
