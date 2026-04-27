import httpx

from yandex_py.core.transport import HTTPTransport


def test_transport_builds_url_and_merges_headers():
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["method"] = request.method
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    sender = HTTPTransport(
        base_url="https://example.com/api/",
        auth_headers={"Authorization": "Bearer token"},
        client=client,
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = sender.get("stat/v1/data", headers={"X-Test": "1"})

    assert response.status_code == 200
    assert captured["url"] == "https://example.com/api/stat/v1/data"
    assert captured["method"] == "GET"
    assert captured["headers"]["authorization"] == "Bearer token"
    assert captured["headers"]["x-test"] == "1"

    sender.close()


async def test_transport_supports_async_requests():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"path": request.url.path})

    transport = httpx.MockTransport(handler)
    sender = HTTPTransport(
        base_url="https://example.com",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    response = await sender.get_async("/ping")

    assert response.json() == {"path": "/ping"}

    sender.close()
    await sender.aclose()
