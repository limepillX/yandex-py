from enum import Enum
from datetime import date
from typing import Optional

from pydantic import BaseModel, model_validator


class DateRangeType(str, Enum):
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    LAST_3_DAYS = "LAST_3_DAYS"
    LAST_5_DAYS = "LAST_5_DAYS"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_14_DAYS = "LAST_14_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"
    LAST_90_DAYS = "LAST_90_DAYS"
    LAST_365_DAYS = "LAST_365_DAYS"
    THIS_WEEK_MON_TODAY = "THIS_WEEK_MON_TODAY"
    THIS_WEEK_SUN_TODAY = "THIS_WEEK_SUN_TODAY"
    LAST_WEEK = "LAST_WEEK"
    LAST_BUSINESS_WEEK = "LAST_BUSINESS_WEEK"
    LAST_WEEK_SUN_SAT = "LAST_WEEK_SUN_SAT"
    THIS_MONTH = "THIS_MONTH"
    LAST_MONTH = "LAST_MONTH"
    ALL_TIME = "ALL_TIME"
    CUSTOM_DATE = "CUSTOM_DATE"
    AUTO = "AUTO"


class TimePeriod(BaseModel):
    """
    Период отчета.

    При DateRangeType=CUSTOM_DATE необходимо указать date_from и date_to.
    """

    date_range_type: DateRangeType
    date_from: Optional[date] = None
    date_to: Optional[date] = None

    @model_validator(mode="after")
    def validate_custom_date(self) -> "TimePeriod":
        if self.date_range_type == DateRangeType.CUSTOM_DATE:
            if self.date_from is None or self.date_to is None:
                raise ValueError("date_from и date_to обязательны при DateRangeType=CUSTOM_DATE")
            if self.date_from > self.date_to:
                raise ValueError("date_from не может быть позже date_to")
        return self
