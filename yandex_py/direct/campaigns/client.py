from __future__ import annotations

from typing import Any, Sequence

from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.campaigns.types import Campaign, CampaignsPage
from yandex_py.direct.constants import CAMPAIGNS_SERVICE
from yandex_py.direct.rpc import (
    parse_units,
    unwrap_result,
)

DEFAULT_FIELD_NAMES = (
    "Id",
    "Name",
    "Type",
    "State",
    "Status",
    "StatusPayment",
    "StatusClarification",
    "DailyBudget",
)
PAGE_LIMIT = 10000


class DirectCampaignsAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def get_page_sync(
        self,
        *,
        states: Sequence[str] | None = None,
        ids: Sequence[int] | None = None,
        types: Sequence[str] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        limit: int = PAGE_LIMIT,
        offset: int = 0,
    ) -> CampaignsPage:
        body = self._body(states, ids, types, field_names, limit, offset)
        response = self._transport.post(CAMPAIGNS_SERVICE, body, self._headers())
        return self._parse(response)

    async def get_page(
        self,
        *,
        states: Sequence[str] | None = None,
        ids: Sequence[int] | None = None,
        types: Sequence[str] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        limit: int = PAGE_LIMIT,
        offset: int = 0,
    ) -> CampaignsPage:
        body = self._body(states, ids, types, field_names, limit, offset)
        response = await self._transport.post_async(
            CAMPAIGNS_SERVICE, body, self._headers()
        )
        return self._parse(response)

    def get_sync(
        self,
        *,
        states: Sequence[str] | None = None,
        ids: Sequence[int] | None = None,
        types: Sequence[str] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
    ) -> list[Campaign]:
        campaigns: list[Campaign] = []
        offset = 0
        while True:
            page = self.get_page_sync(
                states=states,
                ids=ids,
                types=types,
                field_names=field_names,
                offset=offset,
            )
            campaigns.extend(page.campaigns)
            if page.limited_by is None:
                return campaigns
            offset = page.limited_by

    async def get(
        self,
        *,
        states: Sequence[str] | None = None,
        ids: Sequence[int] | None = None,
        types: Sequence[str] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
    ) -> list[Campaign]:
        campaigns: list[Campaign] = []
        offset = 0
        while True:
            page = await self.get_page(
                states=states,
                ids=ids,
                types=types,
                field_names=field_names,
                offset=offset,
            )
            campaigns.extend(page.campaigns)
            if page.limited_by is None:
                return campaigns
            offset = page.limited_by

    @staticmethod
    def _body(
        states: Sequence[str] | None,
        ids: Sequence[int] | None,
        types: Sequence[str] | None,
        field_names: Sequence[str],
        limit: int,
        offset: int,
    ) -> dict[str, Any]:
        criteria = {
            key: list(value)
            for key, value in (("States", states), ("Ids", ids), ("Types", types))
            if value is not None
        }
        return {
            "method": "get",
            "params": {
                "SelectionCriteria": criteria,
                "FieldNames": list(field_names),
                "Page": {"Limit": limit, "Offset": offset},
            },
        }

    @staticmethod
    def _headers() -> dict[str, str]:
        return {"Accept-Language": "ru"}

    def _parse(self, response: Any) -> CampaignsPage:
        page = CampaignsPage.model_validate(unwrap_result(response))
        page.units = parse_units(response.headers.get("Units"))
        return page
