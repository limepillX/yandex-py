from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from yandex_py.reports.types.fields import FieldName
from yandex_py.reports.types.time_period import DateRangeType


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

    field: FieldName = Field(..., serialization_alias="Field")
    operator: FilterOperator = Field(..., serialization_alias="Operator")
    values: list[str] = Field(..., serialization_alias="Values")


class SelectionCriteria(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    date_from: Optional[str] = Field(None, serialization_alias="DateFrom")
    date_to: Optional[str] = Field(None, serialization_alias="DateTo")
    filter: Optional[list[FilterItem]] = Field(None, serialization_alias="Filter")


class Page(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int = Field(..., serialization_alias="Limit")
    offset: Optional[int] = Field(None, serialization_alias="Offset")


class OrderBy(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    field: FieldName = Field(..., serialization_alias="Field")
    sort_order: Optional[SortOrder] = Field(None, serialization_alias="SortOrder")


class ReportDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    selection_criteria: SelectionCriteria = Field(..., serialization_alias="SelectionCriteria")
    field_names: list[FieldName] = Field(..., serialization_alias="FieldNames")
    report_name: str = Field(..., serialization_alias="ReportName")
    report_type: ReportType = Field(..., serialization_alias="ReportType")
    date_range_type: DateRangeType = Field(..., serialization_alias="DateRangeType")
    format: Literal["TSV"] = Field("TSV", serialization_alias="Format")
    include_vat: YesNo = Field(YesNo.NO, serialization_alias="IncludeVAT")
    include_discount: YesNo = Field(YesNo.NO, serialization_alias="IncludeDiscount")
    goals: Optional[list[str]] = Field(None, serialization_alias="Goals")
    attribution_models: Optional[list[AttributionModel]] = Field(None, serialization_alias="AttributionModels")
    page: Optional[Page] = Field(None, serialization_alias="Page")
    order_by: Optional[list[OrderBy]] = Field(None, serialization_alias="OrderBy")


class ReportRequest(BaseModel):
    """Тело запроса к API отчётов Яндекс.Директ."""

    params: ReportDefinition
