import json

import httpx
import pytest

from yandex_py.core.errors import RequestValidationError
from yandex_py.direct import DirectClient
from yandex_py.direct.bid_modifiers import DirectBidModifiersAPI
from yandex_py.direct.dictionaries import DirectDictionariesAPI


def make_client(handler) -> DirectClient:
    transport = httpx.MockTransport(handler)
    return DirectClient(
        token="".join(("test", "-token")),
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )


def modifier(modifier_id: int, **extra) -> dict:
    return {
        "Id": modifier_id,
        "CampaignId": 1,
        "Level": "CAMPAIGN",
        "Type": "REGIONAL_ADJUSTMENT",
        "RegionalAdjustment": {"RegionId": 2, "BidModifier": 110, "Enabled": "YES"},
        **extra,
    }


def test_bid_modifiers_request_and_response():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["headers"] = request.headers
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={"result": {"BidModifiers": [modifier(3), {"Id": 4}]}},
            headers={"Units": "1/2/3"},
        )

    page = make_client(handler).bid_modifiers.get_page_sync(
        levels=["CAMPAIGN"], campaign_ids=[1], limit=2
    )

    assert seen["url"].endswith("/json/v501/bidmodifiers")
    assert seen["headers"]["Accept-Language"] == "ru"
    assert seen["body"] == {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "Levels": ["CAMPAIGN"],
                "CampaignIds": [1],
                "Types": ["REGIONAL_ADJUSTMENT"],
            },
            "FieldNames": ["Id", "CampaignId", "AdGroupId", "Level", "Type"],
            "RegionalAdjustmentFieldNames": ["RegionId", "BidModifier", "Enabled"],
            "Page": {"Limit": 2, "Offset": 0},
        },
    }
    adjustment = page.bid_modifiers[0].regional_adjustment
    assert adjustment is not None
    assert adjustment.region_id == 2
    assert page.bid_modifiers[1].regional_adjustment is None
    assert page.units is not None
    assert page.units.remaining == 2


def test_bid_modifiers_empty_result_and_sync_pagination():
    empty_client = make_client(lambda request: httpx.Response(200, json={"result": {}}))
    assert empty_client.bid_modifiers.get_sync(levels=["CAMPAIGN"], ids=[1]) == []

    offsets = []

    def handler(request: httpx.Request) -> httpx.Response:
        offset = json.loads(request.content)["params"]["Page"]["Offset"]
        offsets.append(offset)
        result: dict[str, object] = {"BidModifiers": [modifier(offset + 1)]}
        if offset == 0:
            result["LimitedBy"] = 1
        return httpx.Response(200, json={"result": result})

    client = make_client(handler)
    assert client.bid_modifiers.get_page_sync(
        levels=["CAMPAIGN"], ids=[1]
    ).bid_modifiers
    assert [
        item.id for item in client.bid_modifiers.get_sync(levels=["CAMPAIGN"], ids=[1])
    ] == [1, 2]
    assert offsets == [0, 0, 1]


async def test_bid_modifiers_async_pagination():
    def handler(request: httpx.Request) -> httpx.Response:
        offset = json.loads(request.content)["params"]["Page"]["Offset"]
        result: dict[str, object] = {"BidModifiers": [modifier(offset + 1)]}
        if offset == 0:
            result["LimitedBy"] = 1
        return httpx.Response(200, json={"result": result})

    result = await make_client(handler).bid_modifiers.get(levels=["CAMPAIGN"], ids=[1])
    assert [item.id for item in result] == [1, 2]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"levels": [], "ids": [1]},
        {"levels": ["CAMPAIGN"]},
        {"levels": ["CAMPAIGN"], "campaign_ids": list(range(11))},
        {"levels": ["CAMPAIGN"], "ids": [1], "limit": 0},
        {"levels": ["CAMPAIGN"], "ids": [1], "limit": 1.5},
        {"levels": ["CAMPAIGN"], "ids": [1], "limit": True},
        {"levels": ["CAMPAIGN"], "ids": [1], "offset": -1},
        {"levels": ["CAMPAIGN"], "ids": [1], "offset": 0.5},
        {"levels": ["CAMPAIGN"], "ids": [1], "offset": False},
        {"levels": ["CAMPAIGN"], "ids": [1], "offset": 120000},
    ],
)
def test_bid_modifiers_validation(kwargs):
    with pytest.raises(RequestValidationError) as exc_info:
        DirectBidModifiersAPI._body(**kwargs)
    assert exc_info.value.product == "direct"


def test_bid_modifiers_pagination_does_not_silently_truncate_at_ceiling():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(json.loads(request.content)["params"]["Page"])
        return httpx.Response(200, json={"result": {"LimitedBy": 120000}})

    with pytest.raises(RequestValidationError):
        make_client(handler).bid_modifiers.get_sync(levels=["CAMPAIGN"], ids=[1])
    assert calls == [{"Limit": 10000, "Offset": 0}]


def test_dictionaries_request_response_and_client_properties():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200,
            json={
                "result": {
                    "GeoRegions": [
                        {
                            "GeoRegionId": 1,
                            "GeoRegionName": "Russia",
                            "GeoRegionType": "COUNTRY",
                            "ParentId": 0,
                        }
                    ]
                }
            },
        )

    client = make_client(handler)
    regions = client.dictionaries.get_geo_regions_sync()
    assert isinstance(client.bid_modifiers, DirectBidModifiersAPI)
    assert isinstance(client.dictionaries, DirectDictionariesAPI)
    assert seen["url"].endswith("/json/v501/dictionaries")
    assert seen["body"] == {
        "method": "get",
        "params": {"DictionaryNames": ["GeoRegions"]},
    }
    assert regions[0].geo_region_name == "Russia"


async def test_dictionaries_async_and_body_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"error": {"error_code": 1, "error_string": "x"}}
        )

    with pytest.raises(RequestValidationError):
        await make_client(handler).dictionaries.get_geo_regions()


def test_bid_modifiers_rejects_non_regional_type():
    with pytest.raises(RequestValidationError):
        DirectBidModifiersAPI._body(
            levels=["CAMPAIGN"], types=["MOBILE_ADJUSTMENT"], ids=[1]
        )
