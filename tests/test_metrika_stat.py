from datetime import date

import httpx
import pytest

from yandex_py.core.errors import AuthenticationError, NotFoundError, RequestValidationError
from yandex_py.metrika import MetrikaClient
from yandex_py.metrika.stat.types import ByTimeQuery, TableQuery


def test_metrika_table_sync_serializes_params_and_parses_response():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        captured["headers"] = dict(request.headers)
        return httpx.Response(
            200,
            json={
                "query": {
                    "dimensions": ["ym:s:trafficSource"],
                    "metrics": ["ym:s:visits"],
                    "date1": "2024-01-01",
                    "date2": "2024-01-07",
                    "limit": 100,
                    "offset": 1,
                },
                "data": [
                    {
                        "dimensions": [{"name": "Search engine", "id": "organic"}],
                        "metrics": [123],
                    }
                ],
                "total_rows": 1,
                "sampled": False,
                "totals": [123],
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = client.stat.table_sync(
        TableQuery(
            ids=[1, 2],
            metrics=["ym:s:visits"],
            dimensions=["ym:s:trafficSource"],
            date1=date(2024, 1, 1),
            date2=date(2024, 1, 7),
            filters="ym:s:browser=='Chrome'",
            include_undefined=True,
            sort=["-ym:s:visits"],
            limit=100,
            offset=1,
        )
    )

    assert captured["method"] == "GET"
    assert captured["path"] == "/stat/v1/data"
    assert captured["params"] == {
        "ids": "1,2",
        "metrics": "ym:s:visits",
        "date1": "2024-01-01",
        "date2": "2024-01-07",
        "dimensions": "ym:s:trafficSource",
        "filters": "ym:s:browser=='Chrome'",
        "include_undefined": "true",
        "limit": "100",
        "offset": "1",
        "sort": "-ym:s:visits",
    }
    assert captured["headers"]["authorization"] == "OAuth token"
    assert "client-login" not in captured["headers"]
    assert response.total_rows == 1
    assert response.data[0].dimensions[0].name == "Search engine"
    assert response.data[0].dimensions[0].model_extra == {"id": "organic"}
    assert response.data[0].metrics == [123]

    client.close()


async def test_metrika_table_async_works():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "query": {"metrics": ["ym:s:visits"]},
                "data": [],
                "total_rows": 0,
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = await client.stat.table(TableQuery(ids=[1], metrics=["ym:s:visits"]))

    assert response.total_rows == 0

    client.close()
    await client.aclose()


def test_metrika_by_time_sync_serializes_params_and_parses_response():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        return httpx.Response(
            200,
            json={
                "query": {
                    "dimensions": ["ym:s:browser"],
                    "metrics": ["ym:s:visits"],
                    "date1": "2024-01-01",
                    "date2": "2024-01-02",
                    "group": "day",
                },
                "data": [
                    {
                        "dimensions": [{"name": "Chrome", "id": "chrome"}],
                        "metrics": [[10, 12]],
                    }
                ],
                "total_rows": 1,
                "sampled": False,
                "totals": [[10, 12]],
                "annotations": [
                    [
                        {
                            "id": 1,
                            "date": "2024-01-01",
                            "time": "12:00:00",
                            "title": "Deploy",
                            "message": "Release",
                            "group": "A",
                        }
                    ]
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = client.stat.by_time_sync(
        ByTimeQuery(
            ids=[1],
            metrics=["ym:s:visits"],
            dimensions=["ym:s:browser"],
            date1=date(2024, 1, 1),
            date2=date(2024, 1, 2),
            group="day",
            include_annotations=True,
            annotation_groups=["A", "HOLIDAY"],
            keys_sort=["-ym:s:visits"],
            row_ids=[["Chrome"], ["Firefox"]],
            top_keys=2,
        )
    )

    assert captured["method"] == "GET"
    assert captured["path"] == "/stat/v1/data/bytime"
    assert captured["params"] == {
        "ids": "1",
        "metrics": "ym:s:visits",
        "date1": "2024-01-01",
        "date2": "2024-01-02",
        "dimensions": "ym:s:browser",
        "annotation_groups": "A,HOLIDAY",
        "group": "day",
        "include_annotations": "true",
        "keys_sort": "-ym:s:visits",
        "row_ids": '[["Chrome"],["Firefox"]]',
        "top_keys": "2",
    }
    assert response.total_rows == 1
    assert response.data[0].metrics == [[10, 12]]
    assert response.annotations is not None
    assert response.annotations[0][0].title == "Deploy"

    client.close()


async def test_metrika_by_time_async_works():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "query": {"metrics": ["ym:s:visits"], "group": "week"},
                "data": [],
                "total_rows": 0,
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = await client.stat.by_time(ByTimeQuery(ids=[1], metrics=["ym:s:visits"], group="week"))

    assert response.total_rows == 0
    assert response.query.group == "week"

    client.close()
    await client.aclose()


@pytest.mark.parametrize(
    ("status_code", "payload", "expected_error"),
    [
        (
            400,
            {
                "errors": [
                    {
                        "error_type": "invalid_parameter",
                        "message": "Invalid ids",
                        "location": "ids",
                    }
                ],
                "code": 400,
                "message": "Bad request",
            },
            RequestValidationError,
        ),
        (
            403,
            {
                "errors": [{"error_type": "access_denied", "message": "Access denied"}],
                "code": 403,
                "message": "Forbidden",
            },
            AuthenticationError,
        ),
        (
            404,
            {
                "errors": [{"error_type": "not_found", "message": "Counter not found"}],
                "code": 404,
                "message": "Not found",
            },
            NotFoundError,
        ),
    ],
)
def test_metrika_maps_api_errors(status_code, payload, expected_error):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload, headers={"RequestId": "req-456"})

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    with pytest.raises(expected_error) as exc_info:
        client.stat.table_sync(TableQuery(ids=[1], metrics=["ym:s:visits"]))

    assert exc_info.value.product == "metrika"
    assert exc_info.value.http_status == status_code
    assert exc_info.value.request_id == "req-456"

    client.close()
