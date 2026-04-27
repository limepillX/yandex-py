from __future__ import annotations

from typing import Any

from yandex_py.core.errors import (
    AuthenticationError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexAPIError,
)


def raise_direct_api_error(response: Any) -> None:
    request_id = response.headers.get("RequestId")

    try:
        payload = response.json()
    except ValueError:
        payload = None

    error_payload = payload.get("error", payload) if isinstance(payload, dict) else None
    message = response.text
    code = None

    if isinstance(error_payload, dict):
        message = (
            error_payload.get("error_detail")
            or error_payload.get("error_string")
            or error_payload.get("message")
            or message
        )
        code = error_payload.get("error_code") or error_payload.get("code")

    error_kwargs = {
        "message": message,
        "product": "direct",
        "http_status": response.status_code,
        "code": code,
        "request_id": request_id,
        "raw": payload if payload is not None else response.text,
    }

    if response.status_code in (400, 422):
        raise RequestValidationError(**error_kwargs)
    if response.status_code in (401, 403):
        raise AuthenticationError(**error_kwargs)
    if response.status_code == 429:
        raise RateLimitError(**error_kwargs)
    if response.status_code >= 500:
        raise ServerError(**error_kwargs)
    raise YandexAPIError(**error_kwargs)
