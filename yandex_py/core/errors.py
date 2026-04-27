from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ErrorDetails:
    product: str
    message: str
    http_status: int | None = None
    code: str | int | None = None
    request_id: str | None = None
    raw: Any = None


class YandexAPIError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        product: str,
        http_status: int | None = None,
        code: str | int | None = None,
        request_id: str | None = None,
        raw: Any = None,
    ):
        super().__init__(message)
        self.details = ErrorDetails(
            product=product,
            message=message,
            http_status=http_status,
            code=code,
            request_id=request_id,
            raw=raw,
        )

    @property
    def product(self) -> str:
        return self.details.product

    @property
    def http_status(self) -> int | None:
        return self.details.http_status

    @property
    def code(self) -> str | int | None:
        return self.details.code

    @property
    def request_id(self) -> str | None:
        return self.details.request_id

    @property
    def raw(self) -> Any:
        return self.details.raw


class AuthenticationError(YandexAPIError):
    pass


class RateLimitError(YandexAPIError):
    pass


class NotFoundError(YandexAPIError):
    pass


class RequestValidationError(YandexAPIError):
    pass


class ServerError(YandexAPIError):
    pass


class YandexTimeoutError(YandexAPIError):
    pass
