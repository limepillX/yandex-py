from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


def _serialize_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _serialize_value(value: Any) -> str:
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        return ",".join(_serialize_scalar(item) for item in value)
    return _serialize_scalar(value)


class BaseStatQuery(BaseModel):
    ids: list[int]
    accuracy: str | None = None
    attribution: str | None = None
    callback: str | None = None
    date1: str | date | None = None
    date2: str | date | None = None
    dimensions: list[str] | None = None
    direct_client_logins: list[str] | None = None
    filters: str | None = None
    include_undefined: bool | None = None
    lang: str | None = None
    limit: int | None = None
    offset: int | None = None
    preset: str | None = None
    pretty: bool | None = None
    proposed_accuracy: bool | None = None
    timezone: str | None = None

    def to_params(self) -> dict[str, str]:
        return {
            key: _serialize_value(value)
            for key, value in self.model_dump(exclude_none=True).items()
        }


class TableQuery(BaseStatQuery):
    metrics: list[str]
    sort: list[str] | None = None


class TableQueryResult(BaseModel):
    timezone: str | None = None
    preset: str | None = None
    dimensions: list[str] | None = None
    metrics: list[str] | None = None
    sort: list[str] | None = None
    date1: str | None = None
    date2: str | None = None
    filters: str | None = None
    limit: int | None = None
    offset: int | None = None


class DimensionValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None


class TableRow(BaseModel):
    dimensions: list[DimensionValue]
    metrics: list[float | int | None]


class TableResponse(BaseModel):
    query: TableQueryResult
    data: list[TableRow]
    total_rows: int
    total_rows_rounded: bool | None = None
    sampled: bool | None = None
    contains_sensitive_data: bool | None = None
    sample_share: float | None = None
    sample_size: int | None = None
    sample_space: int | None = None
    data_lag: int | None = None
    totals: list[float | int | None] | None = None
    min: list[float | int | None] | None = None
    max: list[float | int | None] | None = None


class ByTimeQuery(BaseStatQuery):
    metrics: list[str]
    annotation_groups: list[str] | None = None
    group: str | None = None
    include_annotations: bool | None = None
    keys_sort: list[str] | None = None
    row_ids: list[list[str]] | None = None
    top_keys: int | None = None


class ByTimeQueryResult(BaseModel):
    timezone: str | None = None
    preset: str | None = None
    dimensions: list[str] | None = None
    metrics: list[str] | None = None
    sort: list[str] | None = None
    date1: str | None = None
    date2: str | None = None
    filters: str | None = None
    group: str | None = None


class ByTimeRow(BaseModel):
    dimensions: list[DimensionValue]
    metrics: list[list[float | int | None]]


class Annotation(BaseModel):
    id: int
    date: str
    time: str
    title: str
    message: str
    group: str


class ByTimeResponse(BaseModel):
    query: ByTimeQueryResult
    data: list[ByTimeRow]
    total_rows: int
    total_rows_rounded: bool | None = None
    sampled: bool | None = None
    contains_sensitive_data: bool | None = None
    sample_share: float | None = None
    sample_size: int | None = None
    sample_space: int | None = None
    data_lag: int | None = None
    totals: list[list[float | int | None]] | None = None
    annotations: list[list[Annotation]] | None = None
