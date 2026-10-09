import json

import httpx
import pytest

from yandex_py.core.errors import AuthenticationError, RateLimitError, ServerError
from yandex_py.direct import DirectClient
from yandex_py.direct.rpc import DirectUnits


def make_client(handler) -> DirectClient:
    transport = httpx.MockTransport(handler)
    return DirectClient(
        token="token",
        client_login="login",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )


def campaign(campaign_id: int, **extra) -> dict:
    return {
        "Id": campaign_id,
        "Name": f"c{campaign_id}",
        "Type": "FUTURE_TYPE",
        "State": "ON",
        "Status": "ACCEPTED",
        "StatusPayment": "ALLOWED",
        "StatusClarification": "",
        "Unknown": 1,
        **extra,
    }


def test_request_body_and_headers():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content)
        seen["headers"] = request.headers
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"result": {"Campaigns": []}})

    client = make_client(handler)
    client.campaigns.get_page_sync(states=["ON"], limit=5)

    assert seen["url"].endswith("/campaigns")
    assert seen["body"]["method"] == "get"
    params = seen["body"]["params"]
    assert params["SelectionCriteria"] == {"States": ["ON"]}
    assert params["Page"] == {"Limit": 5, "Offset": 0}
    assert params["FieldNames"][0] == "Id"
    assert "DailyBudget" in params["FieldNames"]
    assert seen["headers"]["Accept-Language"] == "ru"
    assert seen["headers"]["Authorization"] == "Bearer token"
    assert seen["headers"]["Client-Login"] == "login"


def test_empty_selection_criteria():
    def handler(request: httpx.Request) -> httpx.Response:
        assert json.loads(request.content)["params"]["SelectionCriteria"] == {}
        return httpx.Response(200, json={"result": {}})

    assert make_client(handler).campaigns.get_sync() == []


def test_parse_daily_budget_and_unknown_values():
    body = {
        "result": {
            "Campaigns": [
                campaign(1, DailyBudget={"Amount": 300000000, "Mode": "STANDARD"}),
                campaign(2),
            ]
        }
    }
    client = make_client(lambda request: httpx.Response(200, json=body))

    first, second = client.campaigns.get_sync()

    assert first.daily_budget.amount == 300000000
    assert first.daily_budget.mode == "STANDARD"
    assert first.type == "FUTURE_TYPE"
    assert second.daily_budget is None


def test_pagination_uses_limited_by_as_offset():
    offsets = []

    def handler(request: httpx.Request) -> httpx.Response:
        offset = json.loads(request.content)["params"]["Page"]["Offset"]
        offsets.append(offset)
        if offset == 0:
            return httpx.Response(
                200, json={"result": {"Campaigns": [campaign(1)], "LimitedBy": 1}}
            )
        return httpx.Response(200, json={"result": {"Campaigns": [campaign(2)]}})

    result = make_client(handler).campaigns.get_sync()

    assert offsets == [0, 1]
    assert [c.id for c in result] == [1, 2]


def test_page_units_populated():
    client = make_client(
        lambda request: httpx.Response(
            200, json={"result": {"Campaigns": []}}, headers={"Units": "10/20828/64000"}
        )
    )
    page = client.campaigns.get_page_sync()
    assert page.units == DirectUnits(10, 20828, 64000)


@pytest.mark.parametrize(
    ("code", "expected"), [(53, AuthenticationError), (152, RateLimitError)]
)
def test_200_with_error_body(code, expected):
    client = make_client(
        lambda request: httpx.Response(
            200,
            json={"error": {"error_code": code, "error_string": "x", "request_id": "r9"}},
        )
    )
    with pytest.raises(expected) as exc_info:
        client.campaigns.get_sync()
    assert exc_info.value.details.code == code
    assert exc_info.value.request_id == "r9"


@pytest.mark.parametrize(
    ("status", "expected"), [(401, AuthenticationError), (500, ServerError)]
)
def test_http_errors(status, expected):
    client = make_client(
        lambda request: httpx.Response(
            status, json={"error": {"error_code": 1}}, headers={"RequestId": "h1"}
        )
    )
    with pytest.raises(expected) as exc_info:
        client.campaigns.get_sync()
    assert exc_info.value.http_status == status
    assert exc_info.value.request_id == "h1"


async def test_async_success():
    client = make_client(
        lambda request: httpx.Response(
            200, json={"result": {"Campaigns": [campaign(7)]}}
        )
    )
    result = await client.campaigns.get(states=["ON"])
    assert [c.id for c in result] == [7]


async def test_async_error():
    client = make_client(
        lambda request: httpx.Response(
            200, json={"error": {"error_code": 53, "error_string": "x"}}
        )
    )
    with pytest.raises(AuthenticationError):
        await client.campaigns.get()
