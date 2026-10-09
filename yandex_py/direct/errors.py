from __future__ import annotations

from typing import Any

from yandex_py.core.errors import (
    AuthenticationError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexAPIError,
)


BODY_ERROR_CLASSES: dict[int, type[YandexAPIError]] = {
    52: ServerError,
    53: AuthenticationError,
    54: AuthenticationError,
    152: RateLimitError,
    506: RateLimitError,
    1000: ServerError,
}


def _error_kwargs(response: Any, payload: Any) -> dict[str, Any]:
    request_id = response.headers.get("RequestId")

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

    return {
        "message": message,
        "product": "direct",
        "http_status": response.status_code,
        "code": code,
        "request_id": request_id,
        "raw": payload if payload is not None else response.text,
    }


def raise_direct_api_error(response: Any) -> None:
    try:
        payload = response.json()
    except ValueError:
        payload = None

    error_kwargs = _error_kwargs(response, payload)

    if response.status_code in (400, 422):
        raise RequestValidationError(**error_kwargs)
    if response.status_code in (401, 403):
        raise AuthenticationError(**error_kwargs)
    if response.status_code == 429:
        raise RateLimitError(**error_kwargs)
    if response.status_code >= 500:
        raise ServerError(**error_kwargs)
    raise YandexAPIError(**error_kwargs)


def raise_for_direct_body(response: Any, payload: Any) -> None:
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return

    error_kwargs = _error_kwargs(response, payload)
    error_kwargs["request_id"] = error.get("request_id") or error_kwargs["request_id"]
    error_class = BODY_ERROR_CLASSES.get(error_kwargs["code"], RequestValidationError)
    raise error_class(**error_kwargs)
