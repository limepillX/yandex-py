import httpx

from yandex_py.constants import BASE_URL


class RequestSender:
    def __init__(
        self,
        token: str,
        client_login: str,
        base_url: str = BASE_URL,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url
        self._auth_headers = {
            "Authorization": f"Bearer {token}",
            "Client-Login": client_login,
        }
        self._client = client or httpx.Client()
        self._async_client = async_client or httpx.AsyncClient()

    def _url(self, service: str) -> str:
        return f"{self._base_url}/{service}"

    def post(
        self,
        service: str,
        body: dict,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return self._client.post(
            self._url(service),
            json=body,
            headers={**self._auth_headers, **(headers or {})},
        )

    async def post_async(
        self,
        service: str,
        body: dict,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self._async_client.post(
            self._url(service),
            json=body,
            headers={**self._auth_headers, **(headers or {})},
        )

    def close(self) -> None:
        self._client.close()

    async def aclose(self) -> None:
        await self._async_client.aclose()

    def __enter__(self) -> "RequestSender":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    async def __aenter__(self) -> "RequestSender":
        return self

    async def __aexit__(self, *args) -> None:
        await self.aclose()
