from __future__ import annotations

import httpx

from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.bid_modifiers.client import DirectBidModifiersAPI
from yandex_py.direct.campaigns.client import DirectCampaignsAPI
from yandex_py.direct.constants import API_URL
from yandex_py.direct.dictionaries.client import DirectDictionariesAPI
from yandex_py.direct.reports.client import DirectReportsAPI


class DirectClient:
    def __init__(
        self,
        token: str,
        client_login: str | None = None,
        *,
        use_operator_units: bool = False,
        base_url: str = API_URL,
        timeout: float | httpx.Timeout = 30.0,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        auth_headers = {"Authorization": f"Bearer {token}"}
        if client_login:
            auth_headers["Client-Login"] = client_login
        if use_operator_units:
            auth_headers["Use-Operator-Units"] = "true"

        self._transport = HTTPTransport(
            base_url=base_url,
            auth_headers=auth_headers,
            timeout=timeout,
            client=client,
            async_client=async_client,
        )
        self.reports = DirectReportsAPI(self._transport)
        self.campaigns = DirectCampaignsAPI(self._transport)
        self.bid_modifiers = DirectBidModifiersAPI(self._transport)
        self.dictionaries = DirectDictionariesAPI(self._transport)

    def close(self) -> None:
        self._transport.close()

    async def aclose(self) -> None:
        await self._transport.aclose()

    def __enter__(self) -> "DirectClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    async def __aenter__(self) -> "DirectClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
