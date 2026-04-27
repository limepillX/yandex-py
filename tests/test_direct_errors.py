import httpx
import pytest

from yandex_py.core.errors import (
    AuthenticationError,
    RateLimitError,
    RequestValidationError,
    ServerError,
    YandexTimeoutError,
)
from yandex_py.direct import DirectClient
from yandex_py.direct.reports.types import (
    DateRangeType,
    FieldName,
    Page,
    ReportDefinition,
    ReportRequest,
    ReportType,
    SelectionCriteria,
)


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


def make_client(status_code: int, *, json_body: dict | None = None, text: str = "") -> DirectClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json=json_body,
            text=text,
            headers={"RequestId": "req-123"},
        )

    transport = httpx.MockTransport(handler)
    return DirectClient(
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
def test_direct_reports_api_maps_http_errors(status_code, expected_error):
    client = make_client(
        status_code,
        json_body={
            "error": {
                "error_code": 1,
                "error_string": "failure",
                "error_detail": "details",
            }
        },
    )

    with pytest.raises(expected_error) as exc_info:
        client.reports.fetch_sync(make_request())

    assert exc_info.value.product == "direct"
    assert exc_info.value.http_status == status_code
    assert exc_info.value.request_id == "req-123"

    client.close()


def test_direct_reports_api_raises_timeout_error_after_retries():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(201, headers={"retryIn": "0"})

    transport = httpx.MockTransport(handler)
    client = DirectClient(
        token="token",
        client_login="login",
        client=httpx.Client(transport=transport),
        async_client=httpx.AsyncClient(transport=transport),
    )

    with pytest.raises(YandexTimeoutError):
        client.reports.fetch_sync(make_request(), max_retries=1)

    client.close()
