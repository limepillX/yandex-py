from __future__ import annotations

from yandex_py.core.transport import HTTPTransport
from yandex_py.metrika.constants import STAT_BY_TIME_PATH, STAT_DATA_PATH
from yandex_py.metrika.errors import raise_metrika_api_error
from yandex_py.metrika.stat.types import ByTimeQuery, ByTimeResponse, TableQuery, TableResponse


class MetrikaStatAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def table_sync(self, query: TableQuery) -> TableResponse:
        response = self._transport.get(
            STAT_DATA_PATH,
            params=query.to_params(),
            headers={"Accept": "application/json"},
        )
        return self._parse_table_response(response)

    async def table(self, query: TableQuery) -> TableResponse:
        response = await self._transport.get_async(
            STAT_DATA_PATH,
            params=query.to_params(),
            headers={"Accept": "application/json"},
        )
        return self._parse_table_response(response)

    def by_time_sync(self, query: ByTimeQuery) -> ByTimeResponse:
        response = self._transport.get(
            STAT_BY_TIME_PATH,
            params=query.to_params(),
            headers={"Accept": "application/json"},
        )
        return self._parse_by_time_response(response)

    async def by_time(self, query: ByTimeQuery) -> ByTimeResponse:
        response = await self._transport.get_async(
            STAT_BY_TIME_PATH,
            params=query.to_params(),
            headers={"Accept": "application/json"},
        )
        return self._parse_by_time_response(response)

    def _parse_table_response(self, response) -> TableResponse:
        if response.status_code != 200:
            raise_metrika_api_error(response)
        return TableResponse.model_validate(response.json())

    def _parse_by_time_response(self, response) -> ByTimeResponse:
        if response.status_code != 200:
            raise_metrika_api_error(response)
        return ByTimeResponse.model_validate(response.json())
