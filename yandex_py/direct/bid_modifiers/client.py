from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from yandex_py.core.errors import RequestValidationError
from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.bid_modifiers.types import BidModifier, BidModifiersPage
from yandex_py.direct.constants import BID_MODIFIERS_SERVICE
from yandex_py.direct.rpc import parse_units, unwrap_result

DEFAULT_FIELD_NAMES = ("Id", "CampaignId", "AdGroupId", "Level", "Type")
DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES = ("RegionId", "BidModifier", "Enabled")
PAGE_LIMIT = 10000
MAX_LIMIT_OFFSET_SUM = 120000
MAX_CAMPAIGN_IDS = 10
REGIONAL_ADJUSTMENT_TYPE = "REGIONAL_ADJUSTMENT"


class DirectBidModifiersAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def get_page_sync(
        self,
        *,
        levels: Sequence[str],
        types: Sequence[str] = (REGIONAL_ADJUSTMENT_TYPE,),
        campaign_ids: Sequence[int] | None = None,
        ad_group_ids: Sequence[int] | None = None,
        ids: Sequence[int] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        regional_adjustment_field_names: Sequence[str] = (
            DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES
        ),
        limit: int = PAGE_LIMIT,
        offset: int = 0,
    ) -> BidModifiersPage:
        body = self._body(
            levels,
            types,
            campaign_ids,
            ad_group_ids,
            ids,
            field_names,
            regional_adjustment_field_names,
            limit,
            offset,
        )
        response = self._transport.post(BID_MODIFIERS_SERVICE, body, self._headers())
        return self._parse(response)

    async def get_page(
        self,
        *,
        levels: Sequence[str],
        types: Sequence[str] = (REGIONAL_ADJUSTMENT_TYPE,),
        campaign_ids: Sequence[int] | None = None,
        ad_group_ids: Sequence[int] | None = None,
        ids: Sequence[int] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        regional_adjustment_field_names: Sequence[str] = (
            DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES
        ),
        limit: int = PAGE_LIMIT,
        offset: int = 0,
    ) -> BidModifiersPage:
        body = self._body(
            levels,
            types,
            campaign_ids,
            ad_group_ids,
            ids,
            field_names,
            regional_adjustment_field_names,
            limit,
            offset,
        )
        response = await self._transport.post_async(
            BID_MODIFIERS_SERVICE, body, self._headers()
        )
        return self._parse(response)

    def get_sync(
        self,
        *,
        levels: Sequence[str],
        types: Sequence[str] = (REGIONAL_ADJUSTMENT_TYPE,),
        campaign_ids: Sequence[int] | None = None,
        ad_group_ids: Sequence[int] | None = None,
        ids: Sequence[int] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        regional_adjustment_field_names: Sequence[str] = (
            DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES
        ),
    ) -> list[BidModifier]:
        bid_modifiers: list[BidModifier] = []
        offset = 0
        while True:
            limit = min(PAGE_LIMIT, MAX_LIMIT_OFFSET_SUM - offset)
            if limit <= 0:
                self._raise_ceiling_error()
            page = self.get_page_sync(
                levels=levels,
                types=types,
                campaign_ids=campaign_ids,
                ad_group_ids=ad_group_ids,
                ids=ids,
                field_names=field_names,
                regional_adjustment_field_names=regional_adjustment_field_names,
                limit=limit,
                offset=offset,
            )
            bid_modifiers.extend(page.bid_modifiers)
            if page.limited_by is None:
                return bid_modifiers
            offset = page.limited_by

    async def get(
        self,
        *,
        levels: Sequence[str],
        types: Sequence[str] = (REGIONAL_ADJUSTMENT_TYPE,),
        campaign_ids: Sequence[int] | None = None,
        ad_group_ids: Sequence[int] | None = None,
        ids: Sequence[int] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        regional_adjustment_field_names: Sequence[str] = (
            DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES
        ),
    ) -> list[BidModifier]:
        bid_modifiers: list[BidModifier] = []
        offset = 0
        while True:
            limit = min(PAGE_LIMIT, MAX_LIMIT_OFFSET_SUM - offset)
            if limit <= 0:
                self._raise_ceiling_error()
            page = await self.get_page(
                levels=levels,
                types=types,
                campaign_ids=campaign_ids,
                ad_group_ids=ad_group_ids,
                ids=ids,
                field_names=field_names,
                regional_adjustment_field_names=regional_adjustment_field_names,
                limit=limit,
                offset=offset,
            )
            bid_modifiers.extend(page.bid_modifiers)
            if page.limited_by is None:
                return bid_modifiers
            offset = page.limited_by

    @staticmethod
    def _body(
        levels: Sequence[str],
        types: Sequence[str] = (REGIONAL_ADJUSTMENT_TYPE,),
        campaign_ids: Sequence[int] | None = None,
        ad_group_ids: Sequence[int] | None = None,
        ids: Sequence[int] | None = None,
        field_names: Sequence[str] = DEFAULT_FIELD_NAMES,
        regional_adjustment_field_names: Sequence[str] = (
            DEFAULT_REGIONAL_ADJUSTMENT_FIELD_NAMES
        ),
        limit: int = PAGE_LIMIT,
        offset: int = 0,
    ) -> dict[str, Any]:
        DirectBidModifiersAPI._validate(
            levels, types, campaign_ids, ad_group_ids, ids, limit, offset
        )
        criteria = {
            "Levels": list(levels),
            "Types": list(types),
            **{
                key: list(value)
                for key, value in (
                    ("CampaignIds", campaign_ids),
                    ("AdGroupIds", ad_group_ids),
                    ("Ids", ids),
                )
                if value is not None
            },
        }
        return {
            "method": "get",
            "params": {
                "SelectionCriteria": criteria,
                "FieldNames": list(field_names),
                "RegionalAdjustmentFieldNames": list(regional_adjustment_field_names),
                "Page": {"Limit": limit, "Offset": offset},
            },
        }

    @staticmethod
    def _validate(
        levels: Sequence[str],
        types: Sequence[str],
        campaign_ids: Sequence[int] | None,
        ad_group_ids: Sequence[int] | None,
        ids: Sequence[int] | None,
        limit: int,
        offset: int,
    ) -> None:
        if not levels:
            DirectBidModifiersAPI._raise_validation_error("levels must be non-empty")
        if not types or any(item != REGIONAL_ADJUSTMENT_TYPE for item in types):
            DirectBidModifiersAPI._raise_validation_error(
                "only REGIONAL_ADJUSTMENT types are supported"
            )
        selectors = (campaign_ids, ad_group_ids, ids)
        if not any(selector for selector in selectors):
            DirectBidModifiersAPI._raise_validation_error(
                "one non-empty selector is required"
            )
        if campaign_ids is not None and len(campaign_ids) > MAX_CAMPAIGN_IDS:
            DirectBidModifiersAPI._raise_validation_error(
                "campaign_ids may contain at most 10 values"
            )
        if type(limit) is not int or not 1 <= limit <= PAGE_LIMIT:
            DirectBidModifiersAPI._raise_validation_error(
                "limit must be an integer from 1 to 10000"
            )
        if type(offset) is not int or offset < 0:
            DirectBidModifiersAPI._raise_validation_error(
                "offset must be a non-negative integer"
            )
        if limit + offset > MAX_LIMIT_OFFSET_SUM:
            DirectBidModifiersAPI._raise_validation_error(
                "limit + offset must not exceed 120000"
            )

    @staticmethod
    def _raise_validation_error(message: str) -> None:
        raise RequestValidationError(message, product="direct")

    @staticmethod
    def _raise_ceiling_error() -> None:
        DirectBidModifiersAPI._raise_validation_error(
            "pagination cannot continue beyond the 120000-item API ceiling"
        )

    @staticmethod
    def _headers() -> dict[str, str]:
        return {"Accept-Language": "ru"}

    def _parse(self, response: Any) -> BidModifiersPage:
        page = BidModifiersPage.model_validate(unwrap_result(response))
        page.units = parse_units(response.headers.get("Units"))
        return page
