import httpx

from yandex_py.metrika import MetrikaClient


def test_metrika_management_get_goals_by_counter_sync_returns_goal_ids_and_names():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        captured["headers"] = dict(request.headers)
        return httpx.Response(
            200,
            json={
                "rows": 1,
                "counters": [
                    {
                        "id": 86236072,
                        "name": "PROD (credistory.ru)",
                        "goals": [
                            {
                                "id": 226333731,
                                "name": "ЛК: Регистрация",
                                "type": "action",
                                "status": "Active",
                            },
                            {
                                "id": 226341835,
                                "name": "ЛК: Авторизация",
                                "type": "action",
                                "status": "Active",
                            },
                        ],
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    goals = client.management.get_goals_by_counter_sync(86236072)

    assert captured["path"] == "/management/v1/counters"
    assert captured["params"] == {
        "counter_ids": "86236072",
        "field": "goals",
    }
    assert captured["headers"]["authorization"] == "OAuth token"
    assert [goal.id for goal in goals] == [226333731, 226341835]
    assert [goal.name for goal in goals] == ["ЛК: Регистрация", "ЛК: Авторизация"]

    client.close()


async def test_metrika_management_get_goals_by_counter_async_returns_empty_list_for_missing_counter():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "rows": 1,
                "counters": [
                    {
                        "id": 1,
                        "goals": [],
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    client = MetrikaClient(
        token="token",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    goals = await client.management.get_goals_by_counter(86236072)

    assert goals == []

    client.close()
    await client.aclose()
