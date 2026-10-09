from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from yandex_py.direct.rpc import DirectUnits


class DailyBudget(BaseModel):
    """Дневной бюджет: amount в микроединицах валюты, mode — режим показа."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    amount: int = Field(alias="Amount")
    mode: str = Field(alias="Mode")


class Campaign(BaseModel):
    """Кампания; type/state/status — строки как в API, без enum.

    Кроме id все поля необязательны: API возвращает только запрошенные field_names.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int = Field(alias="Id")
    name: str | None = Field(default=None, alias="Name")
    type: str | None = Field(default=None, alias="Type")
    state: str | None = Field(default=None, alias="State")
    status: str | None = Field(default=None, alias="Status")
    status_payment: str | None = Field(default=None, alias="StatusPayment")
    status_clarification: str | None = Field(default=None, alias="StatusClarification")
    daily_budget: DailyBudget | None = Field(default=None, alias="DailyBudget")


class CampaignsPage(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    campaigns: list[Campaign] = Field(default_factory=list, alias="Campaigns")
    limited_by: int | None = Field(default=None, alias="LimitedBy")
    units: DirectUnits | None = None
