from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from yandex_py.direct.errors import raise_direct_api_error, raise_for_direct_body


@dataclass(frozen=True, slots=True)
class DirectUnits:
    """Баллы Директа из заголовка Units: потрачено/осталось/лимит."""

    spent: int
    remaining: int
    limit: int


def parse_units(header: str | None) -> DirectUnits | None:
    if not header:
        return None
    parts = header.split("/")
    if len(parts) != 3:
        return None
    try:
        return DirectUnits(*(int(part) for part in parts))
    except ValueError:
        return None


def unwrap_result(response: Any) -> Any:
    if response.status_code != 200:
        raise_direct_api_error(response)
    payload = response.json()
    raise_for_direct_body(response, payload)
    return payload["result"]
