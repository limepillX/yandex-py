import asyncio
import time

from yandex_py.constants import REPORTS_SERVICE
from yandex_py.reports.parser import ReportRow, parse_report
from yandex_py.reports.schemas.headers import AcceptLanguage, ProcessingMode
from yandex_py.reports.schemas.request import ReportRequest
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

    def _handle_response(self, response) -> list[ReportRow] | None:
        if response.status_code == 200:
            return parse_report(response.text)
        if response.status_code in (201, 202):
            return None
        raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    async def fetch(self) -> list[ReportRow]:
        body = self._body()
        for _ in range(self._max_retries):
            response = await self._sender.post_async(REPORTS_SERVICE, body, self._headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            await asyncio.sleep(retry_in)
        raise TimeoutError(f"Отчёт не сформирован за {self._max_retries} попыток")

    def fetch_sync(self) -> list[ReportRow]:
        body = self._body()
        for _ in range(self._max_retries):
            response = self._sender.post(REPORTS_SERVICE, body, self._headers)
            result = self._handle_response(response)
            if result is not None:
                return result
            retry_in = int(response.headers.get("retryIn", 10))
            time.sleep(retry_in)
        raise TimeoutError(f"Отчёт не сформирован за {self._max_retries} попыток")
