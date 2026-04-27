from __future__ import annotations

from typing import Any, Mapping

import httpx


class HTTPTransport:
    def __init__(
        self,
        *,
        base_url: str,
        auth_headers: Mapping[str, str] | None = None,
        client: httpx.Client | None = None,
        async_client: httpx.AsyncClient | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._auth_headers = dict(auth_headers or {})
        self._client = client or httpx.Client()
        self._async_client = async_client or httpx.AsyncClient()

    def _url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        return f"{self._base_url}/{path.lstrip('/')}"

    def _headers(self, headers: Mapping[str, str] | None = None) -> dict[str, str]:
        return {**self._auth_headers, **dict(headers or {})}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self._client.request(
            method=method,
            url=self._url(path),
            params=params,
            json=json,
            headers=self._headers(headers),
        )

    async def arequest(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return await self._async_client.request(
            method=method,
            url=self._url(path),
            params=params,
            json=json,
            headers=self._headers(headers),
        )

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("GET", path, params=params, headers=headers)

    async def get_async(
        self,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return await self.arequest("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        body: dict[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("POST", path, json=body, headers=headers)

    async def post_async(
        self,
        path: str,
        body: dict[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return await self.arequest("POST", path, json=body, headers=headers)

    def close(self) -> None:
        self._client.close()

    async def aclose(self) -> None:
        await self._async_client.aclose()

    def __enter__(self) -> "HTTPTransport":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    async def __aenter__(self) -> "HTTPTransport":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
