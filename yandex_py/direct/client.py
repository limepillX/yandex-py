from __future__ import annotations

import httpx

from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.constants import API_URL
from yandex_py.direct.reports.client import DirectReportsAPI


class DirectClient:
    def __init__(
        self,
        token: str,
        client_login: str,
        *,
        base_url: str = API_URL,
        timeout: float | httpx.Timeout = 30.0,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self._transport = HTTPTransport(
            base_url=base_url,
            auth_headers={
                "Authorization": f"Bearer {token}",
                "Client-Login": client_login,
            },
            timeout=timeout,
            client=client,
            async_client=async_client,
        )
        self.reports = DirectReportsAPI(self._transport)

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
