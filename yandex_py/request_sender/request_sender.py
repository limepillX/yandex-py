import httpx

from yandex_py.constants import BASE_URL
from yandex_py.core.transport import HTTPTransport


class HTTPRequestSender(HTTPTransport):
    def __init__(
        self,
        token: str,
        client_login: str,
        base_url: str = BASE_URL,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        super().__init__(
            base_url=base_url,
            auth_headers={
                "Authorization": f"Bearer {token}",
                "Client-Login": client_login,
            },
            client=client,
            async_client=async_client,
        )
