from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from yandex_py.reports.schemas.fields import FieldName
from yandex_py.reports.schemas.time_period import DateRangeType


class ReportType(str, Enum):
    ACCOUNT_PERFORMANCE_REPORT = "ACCOUNT_PERFORMANCE_REPORT"
    ADGROUP_PERFORMANCE_REPORT = "ADGROUP_PERFORMANCE_REPORT"
    AD_PERFORMANCE_REPORT = "AD_PERFORMANCE_REPORT"
    CAMPAIGN_PERFORMANCE_REPORT = "CAMPAIGN_PERFORMANCE_REPORT"
    CRITERIA_PERFORMANCE_REPORT = "CRITERIA_PERFORMANCE_REPORT"
    CUSTOM_REPORT = "CUSTOM_REPORT"
    REACH_AND_FREQUENCY_PERFORMANCE_REPORT = "REACH_AND_FREQUENCY_PERFORMANCE_REPORT"
    SEARCH_QUERY_PERFORMANCE_REPORT = "SEARCH_QUERY_PERFORMANCE_REPORT"


class FilterOperator(str, Enum):
    EQUALS = "EQUALS"
    NOT_EQUALS = "NOT_EQUALS"
    IN = "IN"
    NOT_IN = "NOT_IN"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    STARTS_WITH_IGNORE_CASE = "STARTS_WITH_IGNORE_CASE"
    DOES_NOT_START_WITH_IGNORE_CASE = "DOES_NOT_START_WITH_IGNORE_CASE"
    STARTS_WITH_ANY_IGNORE_CASE = "STARTS_WITH_ANY_IGNORE_CASE"
    DOES_NOT_START_WITH_ALL_IGNORE_CASE = "DOES_NOT_START_WITH_ALL_IGNORE_CASE"


class AttributionModel(str, Enum):
    FC = "FC"          # first click
    LC = "LC"          # last click
    LSC = "LSC"        # last significant click
    LYDC = "LYDC"      # last Yandex Direct click
    FCCD = "FCCD"      # first click cross-device
    LSCCD = "LSCCD"    # last significant click cross-device
    LYDCCD = "LYDCCD"  # last Yandex Direct click cross-device
    AUTO = "AUTO"


class SortOrder(str, Enum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class YesNo(str, Enum):
    YES = "YES"
    NO = "NO"


class FilterItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field: FieldName = Field(..., alias="Field")
    operator: FilterOperator = Field(..., alias="Operator")
    values: list[str] = Field(..., alias="Values")


class SelectionCriteria(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date_from: Optional[str] = Field(None, alias="DateFrom")
    date_to: Optional[str] = Field(None, alias="DateTo")
    filter: Optional[list[FilterItem]] = Field(None, alias="Filter")


class Page(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., alias="Limit")
    offset: Optional[int] = Field(None, alias="Offset")


class OrderBy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field: FieldName = Field(..., alias="Field")
    sort_order: Optional[SortOrder] = Field(None, alias="SortOrder")


class ReportDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    selection_criteria: SelectionCriteria = Field(..., alias="SelectionCriteria")
    field_names: list[FieldName] = Field(..., alias="FieldNames")
    report_name: str = Field(..., alias="ReportName")
    report_type: ReportType = Field(..., alias="ReportType")
    date_range_type: DateRangeType = Field(..., alias="DateRangeType")
    format: Literal["TSV"] = Field("TSV", alias="Format")
    include_vat: YesNo = Field(YesNo.NO, alias="IncludeVAT")
    include_discount: YesNo = Field(YesNo.NO, alias="IncludeDiscount")
    goals: Optional[list[str]] = Field(None, alias="Goals")
    attribution_models: Optional[list[AttributionModel]] = Field(None, alias="AttributionModels")
    page: Optional[Page] = Field(None, alias="Page")
    order_by: Optional[list[OrderBy]] = Field(None, alias="OrderBy")


class ReportRequest(BaseModel):
    """Тело запроса к API отчётов Яндекс.Директ."""

    model_config = ConfigDict(populate_by_name=True)

    params: ReportDefinition = Field(..., alias="params")
