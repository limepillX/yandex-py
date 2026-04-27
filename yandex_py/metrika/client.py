from __future__ import annotations

import httpx

from yandex_py.core.transport import HTTPTransport
from yandex_py.metrika.constants import API_URL
from yandex_py.metrika.management.client import MetrikaManagementAPI
from yandex_py.metrika.stat.client import MetrikaStatAPI


class MetrikaClient:
    def __init__(
        self,
        token: str,
        *,
        base_url: str = API_URL,
        timeout: float | httpx.Timeout = 30.0,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self._transport = HTTPTransport(
            base_url=base_url,
            auth_headers={"Authorization": f"OAuth {token}"},
            timeout=timeout,
            client=client,
            async_client=async_client,
        )
        self.management = MetrikaManagementAPI(self._transport)
        self.stat = MetrikaStatAPI(self._transport)

    def close(self) -> None:
        self._transport.close()

    async def aclose(self) -> None:
        await self._transport.aclose()

    def __enter__(self) -> "MetrikaClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    async def __aenter__(self) -> "MetrikaClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
