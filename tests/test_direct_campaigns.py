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

    assert seen["url"].endswith("/json/v501/campaigns")
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


def test_parse_budget_unknown_values_and_partial_fields():
    body = {
        "result": {
            "Campaigns": [
                campaign(1, DailyBudget={"Amount": 300000000, "Mode": "STANDARD"}),
                campaign(2, DailyBudget=None),
                {"Id": 3},
            ]
        }
    }
    client = make_client(lambda request: httpx.Response(200, json=body))

    first, second, partial = client.campaigns.get_sync()

    assert first.type == "FUTURE_TYPE"
    assert first.daily_budget.amount == 300000000
    assert first.daily_budget.mode == "STANDARD"
    assert second.daily_budget is None
    assert partial.id == 3 and partial.name is None


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
            json={
                "error": {"error_code": code, "error_string": "x", "request_id": "r9"}
            },
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


@pytest.mark.parametrize(
    ("kwargs", "login", "operator"),
    [
        ({}, None, None),
        ({"client_login": "c", "use_operator_units": True}, "c", "true"),
    ],
)
def test_agency_headers(kwargs, login, operator):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.headers)
        return httpx.Response(200, json={"result": {}})

    transport = httpx.MockTransport(handler)
    client = DirectClient(token="t", client=httpx.Client(transport=transport), **kwargs)
    client.campaigns.get_sync()

    assert seen.get("client-login") == login
    assert seen.get("use-operator-units") == operator


TYPED_KEYS = {
    "text_campaign_field_names": "TextCampaignFieldNames",
    "unified_campaign_field_names": "UnifiedCampaignFieldNames",
    "text_campaign_placement_types_field_names": (
        "TextCampaignSearchStrategyPlacementTypesFieldNames"
    ),
    "unified_campaign_placement_types_field_names": (
        "UnifiedCampaignSearchStrategyPlacementTypesFieldNames"
    ),
}


def test_typed_field_names_absent_by_default():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content)["params"])
        return httpx.Response(200, json={"result": {}})

    make_client(handler).campaigns.get_sync()

    assert not set(TYPED_KEYS.values()) & set(seen)


@pytest.mark.parametrize("arg", list(TYPED_KEYS))
def test_typed_field_names_sent_as_is(arg):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content)["params"])
        return httpx.Response(200, json={"result": {}})

    make_client(handler).campaigns.get_sync(**{arg: ["BiddingStrategy"]})

    assert seen[TYPED_KEYS[arg]] == ["BiddingStrategy"]
    assert set(TYPED_KEYS.values()) & set(seen) == {TYPED_KEYS[arg]}


def test_parse_typed_campaigns():
    strategy = {
        "BiddingStrategy": {
            "Search": {
                "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                "PlacementTypes": {
                    "SearchResults": "YES",
                    "Maps": "NO",
                    "SearchOrganizationList": "YES",
                },
            },
            "Network": {"BiddingStrategyType": "SERVING_OFF"},
        }
    }
    body = {
        "result": {
            "Campaigns": [
                campaign(1, TextCampaign=strategy),
                campaign(2, UnifiedCampaign=strategy),
                campaign(3),
            ]
        }
    }
    client = make_client(lambda request: httpx.Response(200, json=body))

    text, unified, plain = client.campaigns.get_sync()

    for typed in (text.text_campaign, unified.unified_campaign):
        search = typed.bidding_strategy.search
        assert search.bidding_strategy_type == "WB_MAXIMUM_CLICKS"
        assert search.placement_types.search_results == "YES"
        assert search.placement_types.maps == "NO"
        assert search.placement_types.search_organization_list == "YES"
        assert search.placement_types.product_gallery is None
        assert typed.bidding_strategy.network.bidding_strategy_type == "SERVING_OFF"
    assert text.unified_campaign is None and unified.text_campaign is None
    assert plain.text_campaign is None


async def test_async_get_forwards_typed_field_names():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content)["params"])
        return httpx.Response(200, json={"result": {}})

    await make_client(handler).campaigns.get(
        unified_campaign_placement_types_field_names=["Maps"]
    )

    assert seen["UnifiedCampaignSearchStrategyPlacementTypesFieldNames"] == ["Maps"]
