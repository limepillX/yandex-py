from __future__ import annotations

from typing import Any

from yandex_py.core.errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexAPIError,
    YandexTimeoutError,
)


def raise_metrika_api_error(response: Any) -> None:
    request_id = (
        response.headers.get("RequestId")
        or response.headers.get("X-Request-Id")
        or response.headers.get("X-RequestId")
    )

    try:
        payload = response.json()
    except ValueError:
        payload = None

    first_error = None
    if isinstance(payload, dict):
        errors = payload.get("errors")
        if isinstance(errors, list) and errors:
            first_error = errors[0]

    message = response.text
    code = None

    if isinstance(payload, dict):
        message = payload.get("message") or message

    if isinstance(first_error, dict):
        message = first_error.get("message") or message
        location = first_error.get("location")
        code = first_error.get("error_type") or payload.get("code") if isinstance(payload, dict) else None
        if location:
            message = f"{message} (location: {location})"
    elif isinstance(payload, dict):
        code = payload.get("code")

    error_kwargs = {
        "message": message,
        "product": "metrika",
        "http_status": response.status_code,
        "code": code,
        "request_id": request_id,
        "raw": payload if payload is not None else response.text,
    }

    if response.status_code == 400 or response.status_code == 406:
        raise RequestValidationError(**error_kwargs)
    if response.status_code in (401, 403):
        raise AuthenticationError(**error_kwargs)
    if response.status_code == 404:
        raise NotFoundError(**error_kwargs)
    if response.status_code == 429:
        raise RateLimitError(**error_kwargs)
    if response.status_code == 504:
        raise YandexTimeoutError(**error_kwargs)
    if response.status_code >= 500:
        raise ServerError(**error_kwargs)
    raise YandexAPIError(**error_kwargs)
