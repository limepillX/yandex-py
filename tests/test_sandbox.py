import os

import pytest

from yandex_py.direct import DirectClient
from yandex_py.direct.constants import SANDBOX_URL
from yandex_py.direct.reports.types import (
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

    return DirectClient(token=token, client_login=client_login, base_url=SANDBOX_URL)


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
    rows = sender.reports.fetch_sync(basic_request)

    assert isinstance(rows, list)
    if rows:
        assert FieldName.Date in rows[0]
        assert FieldName.Clicks in rows[0]


@pytest.mark.integration
async def test_fetch_report_async(sender, basic_request):
    rows = await sender.reports.fetch(basic_request)

    assert isinstance(rows, list)
    if rows:
        assert FieldName.Date in rows[0]
        assert FieldName.Clicks in rows[0]
