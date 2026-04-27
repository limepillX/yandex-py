import os

import pytest

from yandex_py import HTTPRequestSender, YDirectReport
from yandex_py.constants import SANDBOX_URL
from yandex_py.reports.schemas import (
    DateRangeType,
    FieldName,
    Page,
    ReportDefinition,
    ReportRequest,
    ReportType,
    SelectionCriteria,
)


@pytest.fixture
def sender():
    token = os.environ.get("YANDEX_DIRECT_API_TOKEN")
    client_login = os.environ.get("YANDEX_DIRECT_CLIENT_LOGIN")

    if not token:
        pytest.skip("YANDEX_DIRECT_API_TOKEN не задан")
    if not client_login:
        pytest.skip("YANDEX_DIRECT_CLIENT_LOGIN не задан")

    return HTTPRequestSender(token=token, client_login=client_login)


@pytest.fixture
def basic_request():
    return ReportRequest(
        params=ReportDefinition(
            selection_criteria=SelectionCriteria(),
            field_names=[FieldName.Date, FieldName.Clicks, FieldName.Impressions, FieldName.Cost],
            report_name="sandbox-test",
            report_type=ReportType.CUSTOM_REPORT,
            date_range_type=DateRangeType.LAST_7_DAYS,
            page=Page(limit=10),
        )
    )


@pytest.mark.integration
def test_fetch_report_sync(sender, basic_request):
    report = YDirectReport(request=basic_request, sender=sender)
    rows = report.fetch_sync()

    assert isinstance(rows, list)
    if rows:
        assert FieldName.Date in rows[0]
        assert FieldName.Clicks in rows[0]


@pytest.mark.integration
async def test_fetch_report_async(sender, basic_request):
    report = YDirectReport(request=basic_request, sender=sender)
    rows = await report.fetch()

    assert isinstance(rows, list)
    if rows:
        assert FieldName.Date in rows[0]
        assert FieldName.Clicks in rows[0]
