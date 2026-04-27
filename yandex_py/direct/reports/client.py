from __future__ import annotations

import asyncio
import time

from yandex_py.core.errors import YandexTimeoutError
from yandex_py.core.transport import HTTPTransport
from yandex_py.direct.constants import REPORTS_SERVICE
from yandex_py.direct.errors import raise_direct_api_error
from yandex_py.direct.reports.parser import ReportRow, parse_report
from yandex_py.direct.reports.types.headers import AcceptLanguage, ProcessingMode
from yandex_py.direct.reports.types.request import ReportRequest


class DirectReportsAPI:
    def __init__(self, transport: HTTPTransport):
        self._transport = transport

    def fetch_sync(
        self,
        query: ReportRequest,
        *,
        processing_mode: ProcessingMode = ProcessingMode.auto,
        accept_language: AcceptLanguage = AcceptLanguage.ru,
        max_retries: int = 100,
    ) -> list[ReportRow]:
        body = query.model_dump(by_alias=True, exclude_none=True)
        headers = self._headers(processing_mode, accept_language)

        for _ in range(max_retries):
            response = self._transport.post(REPORTS_SERVICE, body, headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            time.sleep(retry_in)

        raise YandexTimeoutError(
            f"Отчёт не сформирован за {max_retries} попыток",
            product="direct",
        )

    async def fetch(
        self,
        query: ReportRequest,
        *,
        processing_mode: ProcessingMode = ProcessingMode.auto,
        accept_language: AcceptLanguage = AcceptLanguage.ru,
        max_retries: int = 100,
    ) -> list[ReportRow]:
        body = query.model_dump(by_alias=True, exclude_none=True)
        headers = self._headers(processing_mode, accept_language)

        for _ in range(max_retries):
            response = await self._transport.post_async(REPORTS_SERVICE, body, headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            await asyncio.sleep(retry_in)

        raise YandexTimeoutError(
            f"Отчёт не сформирован за {max_retries} попыток",
            product="direct",
        )

    def _headers(
        self,
        processing_mode: ProcessingMode,
        accept_language: AcceptLanguage,
    ) -> dict[str, str]:
        return {
            "Accept-Language": accept_language.value,
            "processingMode": processing_mode.value,
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true",
            "Accept-Encoding": "gzip",
        }

    def _handle_response(self, response) -> list[ReportRow] | None:
        if response.status_code == 200:
            return parse_report(response.text)
        if response.status_code in (201, 202):
            return None
        raise_direct_api_error(response)
