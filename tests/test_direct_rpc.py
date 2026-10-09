import httpx
import pytest

from yandex_py.core.errors import AuthenticationError, RateLimitError, ServerError
from yandex_py.direct.rpc import DirectUnits, parse_units, unwrap_result


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("10/20828/64000", DirectUnits(10, 20828, 64000)),
        (None, None),
        ("", None),
        ("1/2", None),
        ("a/b/c", None),
    ],
)
def test_parse_units(header, expected):
    assert parse_units(header) == expected


def test_unwrap_result_returns_result():
    assert unwrap_result(httpx.Response(200, json={"result": {"x": 1}})) == {"x": 1}


@pytest.mark.parametrize(
    ("code", "expected"),
    [(53, AuthenticationError), (152, RateLimitError), (1000, ServerError)],
)
def test_unwrap_result_raises_body_error(code, expected):
    response = httpx.Response(
        200, json={"error": {"error_code": code, "error_string": "x", "request_id": "r1"}}
    )
    with pytest.raises(expected) as exc_info:
        unwrap_result(response)
    assert exc_info.value.details.code == code
    assert exc_info.value.request_id == "r1"
