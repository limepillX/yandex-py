from __future__ import annotations

from typing import Any

from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.constants import DICTIONARIES_SERVICE
from yandex_py.direct.dictionaries.types import GeoRegion
from yandex_py.direct.rpc import unwrap_result


class DirectDictionariesAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def get_geo_regions_sync(self) -> list[GeoRegion]:
        response = self._transport.post(DICTIONARIES_SERVICE, self._body())
        return self._parse(response)

    async def get_geo_regions(self) -> list[GeoRegion]:
        response = await self._transport.post_async(DICTIONARIES_SERVICE, self._body())
        return self._parse(response)

    @staticmethod
    def _body() -> dict[str, Any]:
        return {"method": "get", "params": {"DictionaryNames": ["GeoRegions"]}}

    @staticmethod
    def _parse(response: Any) -> list[GeoRegion]:
        return [
            GeoRegion.model_validate(region)
            for region in unwrap_result(response).get("GeoRegions", [])
        ]
