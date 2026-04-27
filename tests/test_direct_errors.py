import httpx
import pytest

from yandex_py.core.errors import (
    AuthenticationError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexTimeoutError,
)
from yandex_py.reports.report import YDirectReport
from yandex_py.reports.types import (
    DateRangeType,
    FieldName,
    Page,
    ReportDefinition,
    ReportRequest,
    ReportType,
    SelectionCriteria,
)
from yandex_py.request_sender.request_sender import HTTPRequestSender


def make_request() -> ReportRequest:
    return ReportRequest(
        params=ReportDefinition(
            selection_criteria=SelectionCriteria(),
            field_names=[FieldName.Date, FieldName.Clicks],
            report_name="test",
            report_type=ReportType.CUSTOM_REPORT,
            date_range_type=DateRangeType.LAST_7_DAYS,
            page=Page(limit=10),
        )
    )


def make_sender(status_code: int, *, json_body: dict | None = None, text: str = "") -> HTTPRequestSender:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json=json_body,
            text=text,
            headers={"RequestId": "req-123"},
        )

    transport = httpx.MockTransport(handler)
    return HTTPRequestSender(
        token="token",
        client_login="login",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (400, RequestValidationError),
        (401, AuthenticationError),
        (403, AuthenticationError),
        (429, RateLimitError),
        (500, ServerError),
    ],
)
def test_direct_report_maps_http_errors(status_code, expected_error):
    sender = make_sender(
        status_code,
        json_body={
            "error": {
                "error_code": 1,
                "error_string": "failure",
                "error_detail": "details",
            }
        },
    )
    report = YDirectReport(request=make_request(), sender=sender)

    with pytest.raises(expected_error) as exc_info:
        report.fetch_sync()

    assert exc_info.value.product == "direct"
    assert exc_info.value.http_status == status_code
    assert exc_info.value.request_id == "req-123"

    sender.close()


def test_direct_report_raises_timeout_error_after_retries():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, headers={"retryIn": "0"})

    transport = httpx.MockTransport(handler)
    sender = HTTPRequestSender(
        token="token",
        client_login="login",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )
    report = YDirectReport(request=make_request(), sender=sender, max_retries=1)

    with pytest.raises(YandexTimeoutError):
        report.fetch_sync()

    sender.close()
