import asyncio
import time
from typing import Any

from yandex_py.constants import REPORTS_SERVICE
from yandex_py.core.errors import (
    AuthenticationError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexAPIError,
    YandexTimeoutError,
)
from yandex_py.reports.parser import ReportRow, parse_report
from yandex_py.reports.types.headers import AcceptLanguage, ProcessingMode
from yandex_py.reports.types.request import ReportRequest
from yandex_py.request_sender.request_sender import HTTPRequestSender


class YDirectReport:
    def __init__(
        self,
        request: ReportRequest,
        sender: HTTPRequestSender,
        processing_mode: ProcessingMode = ProcessingMode.auto,
        accept_language: AcceptLanguage = AcceptLanguage.ru,
        max_retries: int = 100,
    ):
        self._request = request
        self._sender = sender
        self._headers = {
            "Accept-Language": accept_language.value,
            "processingMode": processing_mode.value,
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true",
            "Accept-Encoding": "gzip",
        }
        self._max_retries = max_retries

    def _body(self) -> dict:
        return self._request.model_dump(by_alias=True, exclude_none=True)

    def _raise_api_error(self, response: Any) -> None:
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

    def _handle_response(self, response: Any) -> list[ReportRow] | None:
        if response.status_code == 200:
            return parse_report(response.text)
        if response.status_code in (201, 202):
            return None
        self._raise_api_error(response)

    async def fetch(self) -> list[ReportRow]:
        body = self._body()
        for _ in range(self._max_retries):
            response = await self._sender.post_async(REPORTS_SERVICE, body, self._headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            await asyncio.sleep(retry_in)
        raise YandexTimeoutError(
            f"Отчёт не сформирован за {self._max_retries} попыток",
            product="direct",
        )

    def fetch_sync(self) -> list[ReportRow]:
        body = self._body()
        for _ in range(self._max_retries):
            response = self._sender.post(REPORTS_SERVICE, body, self._headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            time.sleep(retry_in)
        raise YandexTimeoutError(
            f"Отчёт не сформирован за {self._max_retries} попыток",
            product="direct",
        )
